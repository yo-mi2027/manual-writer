import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import vault_writer_server as srv


def test_write_and_read_file(tmp_path, monkeypatch):
    monkeypatch.setitem(srv.config, "vault_path", str(tmp_path))

    res_write = srv.write_file("notes/example.md", "# Title", create_dirs=True)
    assert res_write["success"]
    saved = Path(res_write["path"])
    assert saved.exists()
    assert saved.read_text(encoding="utf-8") == "# Title"

    res_read = srv.read_file("notes/example.md")
    assert res_read["success"]
    assert res_read["content"] == "# Title"


def test_list_dir(tmp_path, monkeypatch):
    monkeypatch.setitem(srv.config, "vault_path", str(tmp_path))
    (tmp_path / "a").mkdir()
    (tmp_path / "a" / "file.txt").write_text("x", encoding="utf-8")

    res = srv.list_dir("a")
    assert res["success"]
    names = {entry["name"] for entry in res["entries"]}
    assert "file.txt" in names


def test_path_traversal_blocked(tmp_path, monkeypatch):
    monkeypatch.setitem(srv.config, "vault_path", str(tmp_path))

    res = srv.write_file("../escape.md", "bad")
    assert res["success"] is False
    assert res.get("error_code") == "path_traversal"


def test_ensure_manual_dirs(tmp_path, monkeypatch):
    monkeypatch.setitem(srv.config, "vault_path", str(tmp_path))

    res = srv.ensure_manual_dirs("給付金編")
    assert res["success"]

    # Check expected directories
    manual_root = tmp_path / "給付金編"
    assert (manual_root / "drafts").exists()
    assert (manual_root / "diagrams").exists()
    assert (manual_root / "tasks").exists()

    # Invalid name (path separator) should fail
    bad = srv.ensure_manual_dirs("../escape")
    assert bad["success"] is False
    assert bad.get("error_code") == "invalid_manual"
