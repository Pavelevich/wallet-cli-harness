# Wallet CLI Harness

Independent Codex JSON harness for the official `@ledgerhq/wallet-cli` command contract.

This repository contains a local Codex plugin and a small Python harness that helps Codex run `wallet-cli` predictably:

- validates command flags before launch;
- appends `--output json` when appropriate;
- parses the final JSON object from stdout instead of trusting the process exit code;
- preserves the wallet-cli command surface instead of substituting another wallet stack.
- provides a `balance-all` workflow for "check my wallet balance" style requests.

## Capabilities

| Capability | What it can run |
| --- | --- |
| Session labels | `session view`, `session reset` |
| Balances | `balance-all`, `balances <label>` |
| History | `operations <label> --limit 20` |
| Receive | `receive <label>`, `receive <label> --no-verify` |
| Send | `send <label> --to <addr> --amount '<n> TICKER'` |
| Swap | `swap quote`, `swap execute`, `swap status` |
| Assets | `assets token`, `assets token-by-id` |
| Device check | `device-check` |

## Decision Tree

The agent routing logic lives in [docs/decision-tree.md](docs/decision-tree.md). The same tree is embedded in the Codex skill so the LLM maps user language to `wallet-cli` commands before it reaches for general host tools.

## Install From GitHub

Add the public marketplace and install the plugin:

```bash
codex plugin marketplace add Pavelevich/wallet-cli-harness --ref main
codex plugin add ledger-wallet-cli@wallet-cli-harness
```

The marketplace entry lives at `.agents/plugins/marketplace.json` and points Codex at this repo as the plugin source.

## Project Status

This is an independent local plugin. It is not affiliated with, endorsed by, or sponsored by Ledger.

## Repository Contents

- `.codex-plugin/plugin.json` - Codex plugin manifest.
- `skills/wallet-cli-harness/SKILL.md` - Codex operating instructions for wallet-cli flows.
- `scripts/wallet_cli_harness.py` - conservative command runner for `wallet-cli`.
- `scripts/wallet_cli_workflow.py` - wallet-cli-only workflows for common user requests.
- `assets/` - plugin icon and logo.
- `index.html` - static landing page for the project.

## Example

```bash
python3 scripts/wallet_cli_harness.py -- session view
python3 scripts/wallet_cli_workflow.py balance-all
python3 scripts/wallet_cli_workflow.py device-check
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
