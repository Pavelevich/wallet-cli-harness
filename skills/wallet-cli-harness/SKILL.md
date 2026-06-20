---
name: wallet-cli-harness
description: Drive the official standalone @ledgerhq/wallet-cli command contract with Codex safety rails for hardware-wallet flows on bitcoin, ethereum, and solana — account discover, session view/reset, balances, operations, receive, send (with dry-run), swap quote/execute/status, genuine-check, assets token/token-by-id. Use for any `wallet-cli` command and for mapping informal wallet requests to the right command. NOT for AgenC marketplace Ledger ops (those stay on the agenc DMK/BLE path in AGENTS.md).
---

# Wallet CLI Harness

Independent Codex safety rails for the official, standalone `@ledgerhq/wallet-cli` package. This plugin is not affiliated with, endorsed by, or sponsored by Ledger.

The CLI is for **USB** hardware-wallet flows, built on the Device Management Kit (DMK). Installed on PATH as `wallet-cli` (`/opt/homebrew/bin/wallet-cli`, currently `@ledgerhq/wallet-cli@1.0.2`). Invoke it directly:

```bash
wallet-cli <command> [flags] --output json
```

Networks: **bitcoin**, **ethereum**, **solana** (mainnet + the testnets the build supports). Tokens are supported on those chains.

> **This is the official release, not a fork.** It does NOT have an `error.code`/`retryable` taxonomy, does NOT have meaningful exit codes, does NOT reject unknown flags, has NO `devices` command, and has NO `--device` selector or BLE transport. Everything below is written to the real 1.0.2 contract — do not assume richer behavior.

---

## First response style

First impressions matter. When the user asks what this plugin can do, how it works, or says they are using `wallet-cli-harness`, open with a capability presentation, not a warning list. Use a compact table like this:

| Capability | What I can run | Typical command |
| --- | --- | --- |
| Session labels | Show or reset saved wallet-cli accounts | `session view`, `session reset` |
| Balances | Check balances for a saved account label | `balances <label>` |
| History | Show recent operations for an account | `operations <label> --limit 20` |
| Receive | Generate or verify receive addresses | `receive <label>` / `receive <label> --no-verify` |
| Send | Dry-run, summarize, then execute after approval | `send <label> --to <addr> --amount '<n> TICKER'` |
| Swap | Quote, execute, and check swap status | `swap quote`, `swap execute`, `swap status` |
| Assets | Resolve token metadata | `assets token`, `assets token-by-id` |
| Device check | Run the official genuine check | `genuine-check` |

Then ask for only the missing inputs needed for the requested action, such as account label, network, recipient, amount, ticker, provider, or swap id.

Lead with capability, then handle transport details only when they matter. Transport caveats belong after the capability table or after a command returns a concrete transport result. If a device command times out on this host, report the actual wallet-cli result and explain it as a transport limitation of the official binary, not as a safety judgment.

---

## Stay inside the plugin

When this plugin is active, keep the work centered on the official `wallet-cli` contract and this harness.

- For wallet tasks, run `../../scripts/wallet_cli_harness.py` instead of relying on remembered terminal output, local notes, OS device inventories, or general shell exploration.
- For "what can you do", "show my wallet", "balance", "history", "receive", "send", "swap", "token", "genuine", or "device" requests in this context, map the request to wallet-cli capabilities first.
- If the user asks "list devices" or "connected devices" while working in Wallet CLI Harness, explain the wallet-cli-relevant device capabilities: `account discover`, `receive` verification, live `send`, `swap execute`, and `genuine-check`. Official `wallet-cli` 1.0.2 has no `devices` command. Ask whether they want to run a specific wallet-cli device command.
- Only inspect macOS USB/Bluetooth/IORegistry/System Profiler when the user explicitly asks for a Mac hardware inventory, such as "list all Mac USB/Bluetooth devices" or "use system_profiler". Do not drift into Mac inventory during wallet-cli flows.
- Do not use recalled balances, remembered labels, previous screenshots, or prior thread summaries as authority. Re-run `session view`, then the relevant `balances`/`operations` command.
- Do not switch to AgenC for personal `wallet-cli` requests. AgenC is only for AgenC marketplace intent.

---

## Plugin harness

This plugin also ships a JSON runner at `../../scripts/wallet_cli_harness.py`. Prefer it for Codex-driven `wallet-cli` calls unless you specifically need raw help text:

```bash
python3 ../../scripts/wallet_cli_harness.py -- session view
python3 ../../scripts/wallet_cli_harness.py -- balances ethereum-1
python3 ../../scripts/wallet_cli_harness.py -- send ethereum-1 --to 0xRECIPIENT --amount '0.01 ETH' --dry-run
```

The harness:

- validates flags for the selected official command before launch, because unknown flags are silently ignored by `wallet-cli`;
- appends `--output json` when missing;
- parses the final JSON object from stdout and reports `walletCliExitCode` separately;
- executes the same wallet-cli command surface, including device-touching commands. It does not replace wallet-cli with AgenC and does not block live wallet-cli commands after the approval gates below are satisfied.

For `wallet-cli <command> --help`, call the binary directly or pass `--no-auto-output-json` to the harness. If a new wallet-cli release adds a flag before this plugin is updated, update the harness allowlist before using that flag.

---

## Scope — what this skill is and is NOT

- **IS:** the standalone `wallet-cli` binary for personal BTC/ETH/SOL wallet flows. When the user asks for wallet-cli behavior, run wallet-cli through this harness.
- **IS NOT** the AgenC marketplace. Never use `wallet-cli` for AgenC tasks, registration, or settlement — those go through `agenc-marketplace` over DMK/BLE per the **HOST LEDGER RULE** in `~/AGENTS.md`. The two tools are unrelated; do not cross them in either direction.
- **IS NOT** for NFTs, encryption/PGP, custom chains, or non-listed networks. If asked, say wallet-cli does not support it rather than inventing a command.

## Host transport note

This host's Ledger **Flex only works over Bluetooth (BLE)**, and the official `wallet-cli` 1.0.2 is **USB-only** (no BLE). This is a transport limitation of the official binary, not a reason to switch a personal wallet-cli request to AgenC.

- **Local/session commands:** `session view/reset`, `balances`, `operations`, `swap quote`, `swap status`, `assets token`/`token-by-id`, `send --dry-run`, `receive --no-verify`.
- **Device commands:** `account discover`, `receive` (default verify), `send` (live), `swap execute`, `genuine-check`. If the user explicitly wants wallet-cli, run the wallet-cli command after the approval gates below and report the actual wallet-cli result. On this specific host, these commands may time out when the only device path is a BLE-only Flex because official wallet-cli has no BLE transport.
- **Do not substitute AgenC for wallet-cli.** Use AgenC DMK/BLE only when the user's intent is AgenC marketplace work (tasks, registration, settlement, or AgenC wallet send). A personal wallet-cli send and an AgenC marketplace send are different operations.

---

## Output contract (official 1.0.2) — parse stdout, never the exit code

Always pass `--output json` when you will parse. In JSON mode **stdout is NDJSON**: zero or more intermediate events, then exactly one final object.

**Decide the outcome from the final JSON object, NOT from the exit code.** The official binary frequently exits `0` even on errors — `$?` is unreliable. Dispatch in this order, per line:

1. `{"type":"device-state", ...}` — non-terminal device progress. Relay `message` to the human; keep waiting.
2. `{"type":"pre-verify-address", "address": ...}` — emitted by `receive` before on-device confirmation; show the address so the human can compare it to the device screen.
3. `{"status":"success", "command": ..., ...data, "timestamp": ...}` — **success.** Read the per-command data keys.
4. `{"ok":false, "error":{"command": ..., "message": ...}}` — **command failed.** There is **only `message`** (no `code`, no `retryable`). Read the message; do not blind-retry.
5. `{"ok":false, "error":{"kind": "command-not-found"|"validation", "available":[...]?, ...}}` — **framework (bunli) error**, usually a bad command or a malformed value. Fix the invocation.

Success keys on `status`; errors key on `ok`. Help/version in agent mode come back as `{"ok":true,"data":{"type":"help"|"version", ...}}`. Amounts in JSON are formatted strings with ticker (e.g. `"0.5 ETH"`), not atomic integers.

---

## CRITICAL safety: unknown flags are silently dropped

The official CLI does **not** validate flags. A typo or invented flag is **silently ignored** and the command proceeds anyway. Consequences:

- **Never invent or guess a flag.** Verify every flag against `wallet-cli <command> --help` first. If a needed flag isn't there, stop and ask — don't add flags one at a time hoping one sticks.
- **A botched `--dry-run` can go LIVE.** If you mistype `--dry-run` (e.g. `--dryrun`), it's dropped and `send` **signs and broadcasts for real**. So: after any dry-run, **confirm the success object proves it was a dry run** (it shows the prepared recipient/amount/fee and **no broadcast/tx hash**). If you can't confirm it was a dry run, treat it as a live send and run the duplicate-spend check before doing anything else.

---

## Money-movement rails (hardware = irreversible)

1. **Dry-run first, verify the echo.** Before any live `send`, run the byte-identical command with `--dry-run --output json`, confirm the result echoes the intended recipient + amount + fee and shows no broadcast, show that to the human, get explicit approval, then re-run the identical command **without** `--dry-run`. (`swap execute` has **no** dry-run — see below.)
2. **One device command at a time.** Never run two device-touching commands concurrently (across all sessions/terminals). Concurrent DMK sessions corrupt the transport (garbled output). Run sequentially.
3. **Never kill a command waiting on the device.** A `device-state` event with `awaiting_approval` means it's healthy and waiting on the human. It times out by itself after `--device-timeout` (default 60000 ms). Let it run.
4. **Never auto-retry a rejection.** If the human refused on the device, that was deliberate — ask whether to retry or abort.
5. **After any ambiguous failure following a sign prompt** (timeout, disconnect, crash, unparseable output), the tx may already be signed and broadcast. Run `operations <account>` (or `swap status` for swaps) to check **before** re-sending. Never re-send on a hunch.
6. **`receive --no-verify` is unattested** — a software-derived address never confirmed on the trusted display. Don't hand it to third parties for deposits; prefer plain `receive` (on-device verify) when a USB device is available.
7. **Ambiguous request → ask, don't guess.** Missing recipient, missing network, an amount with no ticker, an unclear account — stop and ask. A wrong guess on a hardware wallet can mean irreversible loss.

---

## Sessions & labels

`account discover` saves discovered accounts to a local session under a **label** (e.g. `ethereum-1`, `solana-3`). All `--account` flags take a **session label only** — raw descriptors/xprv are rejected. Run `account discover <network>` first to populate the session, then `session view` to list labels.

- `session view` → `{accounts:[{label, descriptor}]}`. `session reset` wipes the store.

---

## Commands (official flags, verified against `--help`)

| Command | Device? | Key flags (official) |
| --- | --- | --- |
| `session view` / `session reset` | No | — |
| `balances` | No | `--account/-a`, `--output` |
| `operations` | No | `--account/-a`, `--limit/-l`, `--cursor`, `--output` |
| `assets token` / `assets token-by-id` | No | positional `<network> <addr>` / `<id>`, `--output` |
| `swap quote` | No | `--from/-f`, `--to/-t`, `--amount`, `--from-account`/`--from-fresh-address`, `--to-account`/`--to-fresh-address`, `--output` |
| `swap status` | No | `--swap-id`, `--provider`, `--output` |
| `send --dry-run` | No | (see `send` row) |
| `account discover` | **Yes** | `--network/-n` (or positional), `--output`, `--device-timeout` |
| `receive` | **Yes** (default) | `--account/-a`, `--verify/-v` (default **true**; `--no-verify` skips device), `--output`, `--device-timeout` |
| `send` (live) | **Yes** | `--account/-a`, `--to/-t`, `--amount` (ticker required), `--fee-per-byte` & `--rbf` (BTC), `--mode`/`--validator`/`--stake-account`/`--memo` (SOL), `--data` (EVM calldata), `--dry-run`, `--output`, `--device-timeout` |
| `genuine-check` | **Yes** | `--output`, `--device-timeout` (device must be on the dashboard) |
| `swap execute` | **Yes** | `--from/-f`, `--to/-t`, `--provider`, `--amount`, `--account/-a`, `--to-account`, `--fee-strategy`, `--output` — **no `--dry-run`, no `--device-timeout`** |

### Notes
- `send` `--amount` **must include a ticker** (`'0.001 BTC'`, `'0.01 ETH'`, `'100 USDT'`). There is no `--token` flag; the ticker drives asset resolution.
- `--data` (EVM calldata) is an arbitrary contract call — make the human explain and confirm it before signing.
- `swap execute` goes to the device but in JSON mode is effectively silent until the final object; it is irreversible once approved on-device. There is no dry-run and no device-timeout — brief the human first, never kill it, and use `swap status --swap-id <id> --provider <p>` as the only recovery/monitoring path.
- `genuine-check` needs the device unlocked **on the dashboard** (exit any app) and host internet.

---

## Intent map (informal request → command)

| User says | Command |
| --- | --- |
| "show my wallet", "what do I have", no task | `session view` (run immediately, then ask) |
| "find/scan/import my accounts", "set up Ethereum" | `account discover <network>` |
| "my address", "where do I deposit" | `receive <account>` (USB device) / `receive <account> --no-verify` (no device, unattested) |
| "balance", "how much do I have" | `balances <account>` |
| "history", "what did I send" | `operations <account>` |
| "send/transfer/pay X to Y" | `send <account> --to <addr> --amount '<n> <ticker>' --dry-run` first, then live |
| "swap/convert/trade A to B" | `swap quote …` → `swap execute …` → `swap status …` |
| "is this Ledger genuine" | `genuine-check` (device on dashboard) |
| "what's this token / resolve token" | `assets token <network> <addr>` or `assets token-by-id <id>` |
| "start over / clear session" | `session reset` |

## Examples

```bash
wallet-cli session view --output json
wallet-cli balances ethereum-1 --output json
wallet-cli operations ethereum-1 --limit 20 --output json
wallet-cli assets token ethereum 0xdAC17F958D2ee523a2206206994597C13D831ec7 --output json
# Dry-run FIRST, verify the echo shows recipient/amount/fee and no broadcast:
wallet-cli send ethereum-1 --to 0xRECIPIENT --amount '0.01 ETH' --dry-run --output json
# Only after human approval, identical without --dry-run (needs USB device):
wallet-cli send ethereum-1 --to 0xRECIPIENT --amount '0.01 ETH' --output json
```

Harness equivalents:

```bash
python3 ../../scripts/wallet_cli_harness.py -- session view
python3 ../../scripts/wallet_cli_harness.py -- balances ethereum-1
python3 ../../scripts/wallet_cli_harness.py -- operations ethereum-1 --limit 20
python3 ../../scripts/wallet_cli_harness.py -- send ethereum-1 --to 0xRECIPIENT --amount '0.01 ETH' --dry-run
python3 ../../scripts/wallet_cli_harness.py -- send ethereum-1 --to 0xRECIPIENT --amount '0.01 ETH'
```
