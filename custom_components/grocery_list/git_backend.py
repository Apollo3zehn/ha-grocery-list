"""Git transport backend (PLAN §2).

This module is the ONLY place that talks to git. It wraps dulwich (pure-Python
git) plus paramiko (SSH keys) and exposes a small, synchronous API:

- ``clone`` / ``open`` a local working repo
- ``fetch`` remote refs
- ``read_blob_at`` — read a file's bytes at an arbitrary commit (for the 3-way
  merge base = last_synced_commit)
- ``write_files`` + ``commit`` — stage and commit working-tree changes
- ``merge_commit`` — create a 2-parent commit (records a merge in history
  without relying on git's textual merge; the tree is produced by our semantic
  merge upstream)
- ``push``

DESIGN CONTRACT (see PLAN §2): git is a transport + history layer only. This
module NEVER performs textual merges or resolves conflicts. All merging happens
in ``merge.py`` on parsed models; the caller writes the already-merged files and
asks this module to record a (possibly 2-parent) commit. That keeps the whole
backend swappable (git binary / GitPython) without touching merge logic.

Threading: dulwich and paramiko are BLOCKING. Home Assistant is asyncio, so
every method here is synchronous and MUST be called via
``hass.async_add_executor_job`` from async code (done in the coordinator).
"""

from __future__ import annotations

import io
import logging
import os
import shutil
from dataclasses import dataclass
from typing import Callable

from dulwich import porcelain
from dulwich.client import get_transport_and_path
from dulwich.objects import Blob, Commit, Tree
from dulwich.repo import Repo

_LOGGER = logging.getLogger(__name__)


class GitBackendError(Exception):
    """Base error for git backend failures."""


class GitAuthError(GitBackendError):
    """Authentication/authorization failure (bad key, token, permissions)."""


class GitCloneError(GitBackendError):
    """Clone/connection failure (bad URL, host unreachable, not found)."""


@dataclass(slots=True)
class GitCredentials:
    """Authentication material for a repo (PLAN §7).

    Exactly one auth method is used:
    - SSH: ``ssh_key_data`` (PEM string) OR ``ssh_key_path`` (preferred; file
      mounted 600), used by paramiko.
    - HTTPS: ``https_token`` (repo-scoped fine-grained token), optional for
      public repos.
    """

    method: str  # "ssh" | "https"
    ssh_key_data: str | None = None
    ssh_key_path: str | None = None
    https_token: str | None = None
    https_username: str = "git"


def _is_ssh_url(url: str) -> bool:
    return url.startswith("git@") or url.startswith("ssh://")


def _is_https_url(url: str) -> bool:
    return url.startswith("http://") or url.startswith("https://")


def validate_url_for_method(url: str, method: str) -> bool:
    """Return True if the URL scheme matches the selected auth method."""
    if method == "ssh":
        return _is_ssh_url(url)
    if method == "https":
        return _is_https_url(url)
    return False


class GitBackend:
    """Synchronous git transport wrapper around a single local working repo."""

    def __init__(self, work_dir: str, url: str, creds: GitCredentials, branch: str):
        self._work_dir = work_dir
        self._url = url
        self._creds = creds
        self._branch = branch
        self._repo: Repo | None = None

    # -- connection helpers -------------------------------------------------

    def _https_url(self) -> str:
        """Inject a token into an HTTPS URL for authentication if provided."""
        if self._creds.method != "https" or not self._creds.https_token:
            return self._url
        # https://host/owner/repo.git -> https://user:token@host/owner/repo.git
        scheme, _, rest = self._url.partition("://")
        user = self._creds.https_username or "git"
        return f"{scheme}://{user}:{self._creds.https_token}@{rest}"

    def _ssh_vendor(self):
        """Build a dulwich Paramiko SSH vendor using the provided key.

        Returns a configured vendor instance, or None for non-SSH.
        """
        if self._creds.method != "ssh":
            return None
        # Import lazily so non-SSH setups don't require paramiko import cost.
        from dulwich.contrib.paramiko_vendor import ParamikoSSHVendor
        import paramiko

        key_obj = None
        if self._creds.ssh_key_data:
            key_obj = self._load_pkey_from_string(self._creds.ssh_key_data)
        elif self._creds.ssh_key_path:
            key_obj = self._load_pkey_from_path(self._creds.ssh_key_path)

        class _KeyVendor(ParamikoSSHVendor):
            def __init__(self, pkey, **kwargs):
                super().__init__(**kwargs)
                self._pkey = pkey

            def run_command(self, host, command, username=None, port=None, **kwargs):
                if self._pkey is not None:
                    kwargs["pkey"] = self._pkey
                # Do not fail on unknown host keys for a headless integration;
                # host key pinning is a documented future enhancement.
                kwargs.setdefault("look_for_keys", False)
                kwargs.setdefault("allow_agent", False)
                return super().run_command(
                    host, command, username=username, port=port, **kwargs
                )

        return _KeyVendor(key_obj)

    @staticmethod
    def _load_pkey_from_string(data: str):
        import paramiko

        # PEM/OpenSSH private keys are newline-sensitive and paramiko requires a
        # trailing newline; normalize CRLF and guarantee one.
        normalized = data.replace("\r\n", "\n")
        if not normalized.endswith("\n"):
            normalized += "\n"

        last_err: Exception | None = None
        for loader in (
            paramiko.Ed25519Key,
            paramiko.ECDSAKey,
            paramiko.RSAKey,
        ):
            try:
                return loader.from_private_key(io.StringIO(normalized))
            except paramiko.PasswordRequiredException as err:
                raise GitAuthError(
                    "SSH private key is passphrase-protected; provide an "
                    "unencrypted key."
                ) from err
            except Exception as err:  # noqa: BLE001 - try next key type
                last_err = err
                continue
        raise GitAuthError(
            f"Unsupported or invalid SSH private key data: {last_err}"
        )

    @staticmethod
    def _load_pkey_from_path(path: str):
        import paramiko

        if not os.path.isfile(path):
            raise GitAuthError(f"SSH key file not found: {path}")
        last_err: Exception | None = None
        for loader in (
            paramiko.Ed25519Key,
            paramiko.ECDSAKey,
            paramiko.RSAKey,
        ):
            try:
                return loader.from_private_key_file(path)
            except paramiko.PasswordRequiredException as err:
                raise GitAuthError(
                    "SSH private key is passphrase-protected; provide an "
                    "unencrypted key."
                ) from err
            except Exception as err:  # noqa: BLE001 - try next key type
                last_err = err
                continue
        raise GitAuthError(
            f"Unsupported or invalid SSH private key file {path}: {last_err}"
        )

    # -- lifecycle ----------------------------------------------------------

    def clone(self) -> None:
        """Clone the remote into the working directory.

        Handles the common "brand new, empty repository" case: a freshly
        created remote has no commits and no target branch, so a normal clone
        fails with "<branch> is not a valid branch or tag" / "neither
        origin_head nor branch are provided". In that case we initialize an
        empty local repo whose HEAD points at the target branch, ready for the
        first commit + push (which creates the branch on the remote).

        Raises GitAuthError/GitCloneError on failure so the config flow can map
        them to friendly messages and only accept config on success (PLAN §1).
        """
        url = self._url if self._creds.method == "ssh" else self._https_url()
        try:
            if self._creds.method == "ssh":
                vendor = self._ssh_vendor()
                if vendor is not None:
                    import dulwich.client as dclient

                    dclient.get_ssh_vendor = lambda: vendor
            porcelain.clone(
                url, self._work_dir, branch=self._branch.encode()
            )
            self._repo = Repo(self._work_dir)
        except GitAuthError:
            raise
        except Exception as err:  # noqa: BLE001
            msg = str(err).lower()
            if "auth" in msg or "permission" in msg or "denied" in msg:
                raise GitAuthError(str(err)) from err
            if self._is_empty_remote_error(msg):
                # Reachable + authorized, just empty. Initialize locally so the
                # first sync can push the initial branch.
                self._init_empty_working_repo()
                return
            raise GitCloneError(str(err)) from err

    @staticmethod
    def _is_empty_remote_error(msg: str) -> bool:
        """Heuristic: does this clone error mean the remote is empty?"""
        return (
            "is not a valid branch or tag" in msg
            or "neither origin_head nor branch" in msg
            or "empty repository" in msg
            or "no such ref was fetched" in msg
        )

    def _init_empty_working_repo(self) -> None:
        """Create a local repo with HEAD on the target branch for an empty remote.

        A partial clone may have created the working dir; clear it first so
        ``porcelain.init`` starts clean. ``fetch``/``push`` talk to the remote
        via ``self._url`` directly, so we only need the local branch to exist.
        """
        if os.path.isdir(self._work_dir):
            shutil.rmtree(self._work_dir)
        os.makedirs(self._work_dir, exist_ok=True)
        repo = porcelain.init(self._work_dir)
        repo.refs.set_symbolic_ref(
            b"HEAD", b"refs/heads/" + self._branch.encode()
        )
        config = repo.get_config()
        config.set((b"remote", b"origin"), b"url", self._url.encode())
        config.write_to_path()
        self._repo = repo

    def open(self) -> None:
        """Open an already-cloned working repo."""
        self._repo = Repo(self._work_dir)

    @property
    def repo(self) -> Repo:
        if self._repo is None:
            raise GitBackendError("Repo is not opened/cloned yet")
        return self._repo

    # -- read ---------------------------------------------------------------

    def head_commit_sha(self) -> str | None:
        """Return the current HEAD commit sha (hex) or None if unborn."""
        try:
            return self.repo.head().decode()
        except KeyError:
            return None

    def read_blob_at(self, commit_sha: str, rel_path: str) -> bytes | None:
        """Read a file's bytes at a given commit. None if absent.

        This is the primitive that lets us load the 3-way merge base from
        ``last_synced_commit`` without any textual git merge.
        """
        repo = self.repo
        try:
            commit = repo[commit_sha.encode()]
        except KeyError:
            return None
        tree = repo[commit.tree]
        parts = rel_path.strip("/").split("/")
        cur = tree
        for i, part in enumerate(parts):
            name = part.encode()
            if not isinstance(cur, Tree) or name not in cur:
                return None
            _mode, sha = cur[name]
            obj = repo[sha]
            if i == len(parts) - 1:
                if isinstance(obj, Blob):
                    return obj.data
                return None
            cur = obj
        return None

    def merge_base(
        self, a_sha: str | None, b_sha: str | None
    ) -> str | None:
        """Return the git merge-base (common ancestor) of two commits.

        This is the 3-way merge ancestor used to distinguish structural
        deletions from never-seen items. If either input is missing, or no
        common ancestor exists, returns ``None`` (callers then treat the base
        as empty). If the two commits are the same, that commit is returned.
        """
        if not a_sha or not b_sha:
            return None
        if a_sha == b_sha:
            return a_sha
        from dulwich.graph import find_merge_base

        repo = self.repo
        try:
            bases = find_merge_base(
                repo, [a_sha.encode(), b_sha.encode()]
            )
        except KeyError:
            return None
        if not bases:
            return None
        return bases[0].decode()

    def list_files(self, subdir: str) -> list[str]:
        """List file paths (relative to repo root) under a working-tree subdir."""
        base = os.path.join(self._work_dir, subdir)
        out: list[str] = []
        if not os.path.isdir(base):
            return out
        for root, _dirs, files in os.walk(base):
            for fname in files:
                full = os.path.join(root, fname)
                rel = os.path.relpath(full, self._work_dir)
                out.append(rel.replace(os.sep, "/"))
        return out

    # -- write --------------------------------------------------------------

    def write_files(self, files: dict[str, bytes]) -> None:
        """Write files (path -> bytes) into the working tree and stage them."""
        repo = self.repo
        to_stage: list[bytes] = []
        for rel_path, data in files.items():
            full = os.path.join(self._work_dir, rel_path)
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "wb") as fh:
                fh.write(data)
            to_stage.append(rel_path.encode())
        repo.stage(to_stage)

    def remove_files(self, rel_paths: list[str]) -> None:
        """Remove files from the working tree and stage the deletions."""
        repo = self.repo
        for rel_path in rel_paths:
            full = os.path.join(self._work_dir, rel_path)
            if os.path.isfile(full):
                os.remove(full)
        repo.stage([p.encode() for p in rel_paths])

    def commit(self, message: str, author: str) -> str:
        """Create a normal commit from the staged index. Returns commit sha."""
        author_bytes = author.encode()
        sha = self.repo.do_commit(
            message.encode(),
            author=author_bytes,
            committer=author_bytes,
        )
        return sha.decode()

    def merge_commit(
        self, message: str, author: str, their_parent_sha: str
    ) -> str:
        """Create a 2-parent merge commit recording our merge of theirs.

        The working tree/index must already contain the semantically merged
        result (produced by ``merge.py`` and written via ``write_files``). This
        only records history with two parents so the graph is honest; git never
        performs the merge itself.
        """
        repo = self.repo
        author_bytes = author.encode()
        parents = []
        head = self.head_commit_sha()
        if head:
            parents.append(head.encode())
        parents.append(their_parent_sha.encode())
        sha = repo.do_commit(
            message.encode(),
            author=author_bytes,
            committer=author_bytes,
            merge_heads=parents[1:],
        )
        return sha.decode()

    # -- remote -------------------------------------------------------------

    def _client_and_path(self):
        if self._creds.method == "ssh":
            vendor = self._ssh_vendor()
            if vendor is not None:
                import dulwich.client as dclient

                dclient.get_ssh_vendor = lambda: vendor
            return get_transport_and_path(self._url)
        return get_transport_and_path(self._https_url())

    def fetch(self) -> str | None:
        """Fetch remote refs into the local repo. Returns remote branch sha."""
        try:
            client, path = self._client_and_path()
            result = client.fetch(path, self.repo)
            ref = f"refs/heads/{self._branch}".encode()
            remote_sha = result.refs.get(ref)
            return remote_sha.decode() if remote_sha else None
        except Exception as err:  # noqa: BLE001
            msg = str(err).lower()
            if "auth" in msg or "permission" in msg or "denied" in msg:
                raise GitAuthError(str(err)) from err
            raise GitBackendError(str(err)) from err

    def push(self) -> None:
        """Push the local branch to the remote."""
        try:
            client, path = self._client_and_path()
            branch_ref = f"refs/heads/{self._branch}".encode()

            def update_refs(refs):
                return {branch_ref: self.repo.refs[branch_ref]}

            client.send_pack(
                path,
                update_refs,
                self.repo.object_store.generate_pack_data,
            )
        except Exception as err:  # noqa: BLE001
            msg = str(err).lower()
            if "auth" in msg or "permission" in msg or "denied" in msg:
                raise GitAuthError(str(err)) from err
            raise GitBackendError(str(err)) from err
