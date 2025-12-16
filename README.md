# vault-writer (FastMCP)

手元の Obsidian vault（任意のテキストディレクトリ）に対して、MCP 経由で Markdown などのテキストを読み書きするための軽量サーバーです。機能はファイルの一覧・読み込み・書き込みのみに絞っています。

## Prerequisites
- Python 3.11+
- `pip`

## Setup
```bash
cd /Users/yo.mi/Projects/manual-writer
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

## Config
`config.yaml` で vault ルートを指定します（デフォルトは `/Users/yo.mi/Projects/manual-writer/vault`）。
```yaml
vault_path: "/Users/yo.mi/Projects/manual-writer/vault"
```
環境変数 `VAULT_WRITER_CONFIG_PATH`（レガシー: `KG_TOOLS_CONFIG_PATH`）で別パスの設定ファイルを指定できます。`VAULT_WRITER_VAULT_PATH`（レガシー: `KG_TOOLS_VAULT_PATH`）で vault パスを環境から上書きできます。

## Run
```bash
cd /Users/yo.mi/Projects/manual-writer
source .venv/bin/activate
python src/vault_writer_server.py
```
MCP クライアント側ではツールセット名 `vault-writer` を指定して接続してください。

## Available tools
- `list_dir(relative_dir=".")` : vault 内ディレクトリの一覧
- `read_file(relative_path)` : vault 内の UTF-8 テキストを読み込み
- `write_file(relative_path, content, create_dirs=True)` : vault 内に UTF-8 テキストを書き込み（上書き可、親ディレクトリ自動作成可）
- `ensure_manual_dirs(manual)` : `<manual>/`, `<manual>/drafts`, `<manual>/diagrams`, `<manual>/tasks` をまとめて作成（既存ならそのまま）

## Notes
- パストラバーサル対策済み（vault ルート外は拒否）。
- Obsidian 固有の frontmatter やリンク操作の機能は持ちません。純粋なファイル I/O のみです。
