# Wallet CLI Harness

Independent Codex JSON harness for the official `@ledgerhq/wallet-cli` command contract.

This repository contains a local Codex plugin and a small Python harness that helps Codex run `wallet-cli` predictably:

- validates command flags before launch;
- appends `--output json` when appropriate;
- parses the final JSON object from stdout instead of trusting the process exit code;
- preserves the wallet-cli command surface instead of substituting another wallet tool.

## Capabilities

| Capability | What it can run |
| --- | --- |
| Session labels | `session view`, `session reset` |
| Balances | `balances <label>` |
| History | `operations <label> --limit 20` |
| Receive | `receive <label>`, `receive <label> --no-verify` |
| Send | `send <label> --to <addr> --amount '<n> TICKER'` |
| Swap | `swap quote`, `swap execute`, `swap status` |
| Assets | `assets token`, `assets token-by-id` |
| Device check | `genuine-check` |

## Project Status

This is an independent local plugin. It is not affiliated with, endorsed by, or sponsored by Ledger.

## Repository Contents

- `.codex-plugin/plugin.json` - Codex plugin manifest.
- `skills/wallet-cli-harness/SKILL.md` - Codex operating instructions for wallet-cli flows.
- `scripts/wallet_cli_harness.py` - conservative command runner for `wallet-cli`.
- `assets/` - plugin icon and logo.
- `index.html` - static landing page for the project.

## Example

```bash
python3 scripts/wallet_cli_harness.py -- session view
python3 scripts/wallet_cli_harness.py -- balances ethereum-1
python3 scripts/wallet_cli_harness.py -- send ethereum-1 --to 0xRECIPIENT --amount '0.01 ETH' --dry-run
```

Live sends are passed through to wallet-cli and should only happen after the dry-run and human approval gates documented in the skill.

## Development

Validate the plugin from the Codex plugin creator skill:

```bash
python3 /Users/tetsuoarena/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .
```

Validate the skill:

```bash
python3 /Users/tetsuoarena/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/wallet-cli-harness
```
