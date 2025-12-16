from __future__ import annotations

"""
vault-writer MCP server (vault-scoped file I/O)

Minimal toolset for reading/writing UTF-8 text files under the configured vault
root.
"""

from pathlib import Path
from typing import Any, Dict, List

from fastmcp import FastMCP

from config import load_config, ensure_vault_path_exists


config = load_config()
# Expose as "vault-writer" for MCP clients
mcp = FastMCP("vault-writer")


def _resolve_under_vault(relative_path: str, create_dirs: bool = False) -> Dict[str, Any]:
    """
    Resolve a relative path under the configured vault and guard against path traversal.
    Returns a dict with success flag, resolved path, and error details if any.
    """
    vault_path = ensure_vault_path_exists(config["vault_path"])
    base = vault_path

    rel = Path(relative_path)
    try:
        candidate = (base / rel).resolve()
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to resolve path: {e}",
            "error_code": "invalid_path",
        }

    try:
        base_resolved = base.resolve()
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to resolve vault path: {e}",
            "error_code": "invalid_vault",
        }

    if base_resolved not in candidate.parents and candidate != base_resolved:
        return {
            "success": False,
            "message": "Path escapes the vault root.",
            "error_code": "path_traversal",
        }

    if create_dirs:
        try:
            candidate.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to create parent directories: {e}",
                "error_code": "io_error",
            }

    return {"success": True, "path": candidate}


def _validate_manual_name(manual: str) -> Optional[str]:
    """
    Validate manual name to avoid path traversal. Returns None if invalid.
    """
    if not manual:
        return None
    p = Path(manual)
    # Allow only simple names without separators like "../" or "a/b"
    if len(p.parts) != 1:
        return None
    return manual


def read_file(relative_path: str) -> Dict[str, Any]:
    """
    Read a UTF-8 text file under the vault root.
    """
    resolved = _resolve_under_vault(relative_path)
    if not resolved.get("success"):
        return resolved

    file_path: Path = resolved["path"]
    if not file_path.exists():
        return {
            "success": False,
            "message": f"File not found: {relative_path}",
            "error_code": "not_found",
        }
    if not file_path.is_file():
        return {
            "success": False,
            "message": f"Not a file: {relative_path}",
            "error_code": "invalid_type",
        }

    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to read file: {e}",
            "error_code": "io_error",
        }

    return {
        "success": True,
        "path": str(file_path),
        "relative_path": relative_path,
        "content": content,
    }


def write_file(relative_path: str, content: str, create_dirs: bool = True) -> Dict[str, Any]:
    """
    Write a UTF-8 text file under the vault root. Overwrites if exists.
    """
    resolved = _resolve_under_vault(relative_path, create_dirs=create_dirs)
    if not resolved.get("success"):
        return resolved

    file_path: Path = resolved["path"]
    if file_path.exists() and file_path.is_dir():
        return {
            "success": False,
            "message": f"Target is a directory: {relative_path}",
            "error_code": "invalid_type",
        }

    try:
        file_path.write_text(content, encoding="utf-8")
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to write file: {e}",
            "error_code": "io_error",
        }

    return {
        "success": True,
        "path": str(file_path),
        "relative_path": relative_path,
        "message": "File written (overwrite enabled).",
    }


def list_dir(relative_dir: str = ".") -> Dict[str, Any]:
    """
    List entries under a directory inside the vault.
    """
    resolved = _resolve_under_vault(relative_dir)
    if not resolved.get("success"):
        return resolved

    dir_path: Path = resolved["path"]
    if not dir_path.exists():
        return {
            "success": False,
            "message": f"Directory not found: {relative_dir}",
            "error_code": "not_found",
        }
    if not dir_path.is_dir():
        return {
            "success": False,
            "message": f"Not a directory: {relative_dir}",
            "error_code": "invalid_type",
        }

    entries: List[Dict[str, Any]] = []
    try:
        for entry in dir_path.iterdir():
            entries.append(
                {
                    "name": entry.name,
                    "is_dir": entry.is_dir(),
                    "size": entry.stat().st_size,
                }
            )
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to list directory: {e}",
            "error_code": "io_error",
        }

    return {
        "success": True,
        "path": str(dir_path),
        "relative_path": relative_dir,
        "entries": entries,
    }


def ensure_manual_dirs(manual: str) -> Dict[str, Any]:
    """
    Ensure standard directories exist for a given manual.

    Creates (if missing):
      - <manual>/
      - <manual>/drafts
      - <manual>/diagrams
      - <manual>/tasks
    """
    valid = _validate_manual_name(manual)
    if not valid:
        return {
            "success": False,
            "message": "Invalid manual name.",
            "error_code": "invalid_manual",
        }

    base = ensure_vault_path_exists(config["vault_path"])
    created: List[str] = []
    paths: List[str] = []

    for sub in ["", "drafts", "diagrams", "tasks"]:
        target = (base / manual / sub) if sub else (base / manual)
        try:
            target.mkdir(parents=True, exist_ok=True)
            paths.append(str(target))
            if (target.exists() and not any(target.iterdir())):
                created.append(str(target))
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to create directory {target}: {e}",
                "error_code": "io_error",
            }

    return {
        "success": True,
        "manual": manual,
        "paths": paths,
        "message": "Manual directories ensured.",
    }


# Register tools with FastMCP while keeping callability for local tests
mcp.tool()(read_file)
mcp.tool()(write_file)
mcp.tool()(list_dir)
mcp.tool()(ensure_manual_dirs)


def main() -> None:
    """Entry point for running the vault-writer FastMCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
