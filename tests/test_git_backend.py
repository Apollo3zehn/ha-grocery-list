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


def test_validate_url_for_method():
    from grocery_list.git_backend import validate_url_for_method

    assert validate_url_for_method("git@host:o/r.git", "ssh")
    assert validate_url_for_method("ssh://host/o/r.git", "ssh")
    assert not validate_url_for_method("https://host/o/r.git", "ssh")
    assert validate_url_for_method("https://host/o/r.git", "https")
    assert not validate_url_for_method("git@host:o/r.git", "https")
