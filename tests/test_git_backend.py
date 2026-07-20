"""Integration tests for the git transport backend using local repos.

These tests avoid any network/SSH by using a local bare repository as the
"remote" and file paths as URLs (dulwich supports local transport). They verify
the transport contract the coordinator relies on: clone, commit, push, fetch,
and read_blob_at (the 3-way merge base primitive).
"""

import os

import pytest

from grocery_list.git_backend import GitBackend, GitCredentials

dulwich = pytest.importorskip("dulwich")
from dulwich import porcelain  # noqa: E402


def _init_bare_remote(path: str) -> None:
    os.makedirs(path, exist_ok=True)
    porcelain.init(path, bare=True)


def _creds() -> GitCredentials:
    # Local file transport needs no auth; use https method with no token so no
    # URL rewriting happens.
    return GitCredentials(method="https", https_token=None)


def _seed_remote_with_initial_commit(remote: str, seed_work: str) -> str:
    """Create an initial commit on the remote via a temporary working clone."""
    porcelain.clone(remote, seed_work)
    lists_dir = os.path.join(seed_work, "lists")
    os.makedirs(lists_dir, exist_ok=True)
    with open(os.path.join(lists_dir, "rewe.md"), "wb") as fh:
        fh.write(b"# Rewe\n\n## Vegetables\n- [ ] Tomatoes <!-- id:a1 cat:- by:- ts:2026-01-01T00:00:00Z upd:2026-01-01T00:00:00Z -->\n")
    porcelain.add(seed_work, [os.path.join(lists_dir, "rewe.md")])
    sha = porcelain.commit(
        seed_work, message=b"seed", author=b"seed <s@e.d>", committer=b"seed <s@e.d>"
    )
    porcelain.push(seed_work, remote, b"refs/heads/master")
    return sha.decode() if isinstance(sha, bytes) else str(sha)


@pytest.fixture()
def remote_repo(tmp_path):
    remote = str(tmp_path / "remote.git")
    _init_bare_remote(remote)
    seed_work = str(tmp_path / "seed")
    sha = _seed_remote_with_initial_commit(remote, seed_work)
    return remote, sha


def test_clone_and_read_head(remote_repo, tmp_path):
    remote, seed_sha = remote_repo
    work = str(tmp_path / "work")
    backend = GitBackend(work, remote, _creds(), branch="master")
    backend.clone()
    head = backend.head_commit_sha()
    assert head is not None
    assert os.path.isfile(os.path.join(work, "lists", "rewe.md"))


def test_read_blob_at_head(remote_repo, tmp_path):
    remote, _ = remote_repo
    work = str(tmp_path / "work")
    backend = GitBackend(work, remote, _creds(), branch="master")
    backend.clone()
    head = backend.head_commit_sha()
    data = backend.read_blob_at(head, "lists/rewe.md")
    assert data is not None
    assert b"Tomatoes" in data
    # Missing file returns None
    assert backend.read_blob_at(head, "lists/nope.md") is None


def test_commit_and_push_then_fetch_sees_it(remote_repo, tmp_path):
    remote, _ = remote_repo
    work_a = str(tmp_path / "a")
    backend_a = GitBackend(work_a, remote, _creds(), branch="master")
    backend_a.clone()
    backend_a.write_files(
        {"lists/aldi.md": b"# Aldi\n\n## Dairy\n- [ ] Milk <!-- id:b2 cat:- by:- ts:2026-01-02T00:00:00Z upd:2026-01-02T00:00:00Z -->\n"}
    )
    new_sha = backend_a.commit("add aldi", "pi <pi@host>")
    backend_a.push()

    # Second clone sees the pushed commit.
    work_b = str(tmp_path / "b")
    backend_b = GitBackend(work_b, remote, _creds(), branch="master")
    backend_b.clone()
    assert os.path.isfile(os.path.join(work_b, "lists", "aldi.md"))
    data = backend_b.read_blob_at(backend_b.head_commit_sha(), "lists/aldi.md")
    assert b"Milk" in data
    assert new_sha


def test_list_files(remote_repo, tmp_path):
    remote, _ = remote_repo
    work = str(tmp_path / "work")
    backend = GitBackend(work, remote, _creds(), branch="master")
    backend.clone()
    files = backend.list_files("lists")
    assert "lists/rewe.md" in files


def test_remove_files(remote_repo, tmp_path):
    remote, _ = remote_repo
    work = str(tmp_path / "work")
    backend = GitBackend(work, remote, _creds(), branch="master")
    backend.clone()
    backend.remove_files(["lists/rewe.md"])
    backend.commit("remove rewe", "pi <pi@host>")
    assert not os.path.isfile(os.path.join(work, "lists", "rewe.md"))


def test_clone_empty_remote_inits_local_branch(tmp_path):
    """Cloning a brand-new EMPTY remote must succeed by initializing locally.

    A freshly created remote has no commits and no target branch. ``clone``
    should detect this, init a local repo with HEAD on the target branch, and
    leave us ready to make the first commit + push (which creates the branch
    on the remote).
    """
    remote = str(tmp_path / "empty.git")
    _init_bare_remote(remote)
    work = str(tmp_path / "work")
    backend = GitBackend(work, remote, _creds(), branch="main")
    backend.clone()
    # HEAD points at the target branch even though no commit exists yet.
    assert backend.repo.refs.read_ref(b"HEAD") == b"ref: refs/heads/main"
    assert backend.head_commit_sha() is None
    # First commit + push creates the branch on the remote.
    backend.write_files({"lists/default.md": b"# Default\n"})
    backend.commit("init", "pi <pi@host>")
    backend.push()
    from dulwich.repo import Repo

    bare = Repo(remote)
    assert bare.refs.read_ref(b"refs/heads/main") is not None


def test_validate_url_for_method():
    from grocery_list.git_backend import validate_url_for_method

    assert validate_url_for_method("git@host:o/r.git", "ssh")
    assert validate_url_for_method("ssh://host/o/r.git", "ssh")
    assert not validate_url_for_method("https://host/o/r.git", "ssh")
    assert validate_url_for_method("https://host/o/r.git", "https")
    assert not validate_url_for_method("git@host:o/r.git", "https")


def _generate_ed25519_pem() -> str:
    """Return a fresh unencrypted RSA private key as a PEM string.

    (RSA is used because ``paramiko.RSAKey.generate`` is available across
    paramiko versions, whereas ``Ed25519Key.generate`` is not.)
    """
    import io as _io

    paramiko = pytest.importorskip("paramiko")
    key = paramiko.RSAKey.generate(2048)
    buf = _io.StringIO()
    key.write_private_key(buf)
    return buf.getvalue()


def test_load_pkey_from_string_roundtrip():
    from grocery_list.git_backend import GitBackend

    pem = _generate_ed25519_pem()
    key = GitBackend._load_pkey_from_string(pem)
    assert key is not None


def test_load_pkey_from_string_without_trailing_newline():
    """A textarea-pasted key missing its trailing newline must still load."""
    from grocery_list.git_backend import GitBackend

    pem = _generate_ed25519_pem().rstrip("\n")
    key = GitBackend._load_pkey_from_string(pem)
    assert key is not None


def test_load_pkey_from_string_crlf_normalized():
    """CRLF line endings (from some browsers) must be normalized and load."""
    from grocery_list.git_backend import GitBackend

    pem = _generate_ed25519_pem().replace("\n", "\r\n")
    key = GitBackend._load_pkey_from_string(pem)
    assert key is not None


def test_load_pkey_from_string_invalid_raises():
    from grocery_list.git_backend import GitAuthError, GitBackend

    with pytest.raises(GitAuthError):
        GitBackend._load_pkey_from_string("not a key")
