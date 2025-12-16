from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
import os

import yaml


def load_config() -> Dict[str, Any]:
    """
    Load vault-writer configuration.

    Resolution order:
    1) Environment variable VAULT_WRITER_CONFIG_PATH (or legacy KG_TOOLS_CONFIG_PATH)
    2) ./config.yaml next to this file
    3) Default vault_path = /Users/yo.mi/Projects/manual-writer/vault
    """
    here = Path(__file__).resolve().parent
    repo_root = here.parent

    env_path = os.environ.get("VAULT_WRITER_CONFIG_PATH") or os.environ.get("KG_TOOLS_CONFIG_PATH")
    if env_path:
        cfg_path = Path(env_path).expanduser()
        if not cfg_path.is_absolute():
            cfg_path = (Path.cwd() / cfg_path).resolve()
    else:
        # 仕様書に合わせ、プロジェクトルート直下のconfig.yamlを優先
        cfg_path = repo_root / "config.yaml"
        if not cfg_path.exists():
            cfg_path = here / "config.yaml"

    # デフォルトはプロジェクトルート直下のvault（絶対パスに解決）
    default_vault = Path("/Users/yo.mi/Projects/manual-writer/vault").resolve()
    # Allow env override for vault_path as well (new name + legacy name)
    env_vault = os.environ.get("VAULT_WRITER_VAULT_PATH") or os.environ.get("KG_TOOLS_VAULT_PATH")
    config: Dict[str, Any] = {"vault_path": env_vault or str(default_vault)}

    if cfg_path.exists():
        try:
            data = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
            if isinstance(data, dict):
                config.update(data)
        except Exception:
            # Best-effort: fall back to defaults
            pass

    # vault_path を絶対パスに正規化（相対指定時はプロジェクトルート基準）
    vp = Path(str(config.get("vault_path", default_vault))).expanduser()
    if not vp.is_absolute():
        vp = (repo_root / vp).resolve()
    config["vault_path"] = str(vp)

    return config


def ensure_vault_path_exists(vault_path: str) -> Path:
    """
    Normalize vault path and return it as a Path.

    Note: this function does not create the directory; callers decide how to handle missing paths.
    """
    return Path(vault_path).expanduser().resolve()
