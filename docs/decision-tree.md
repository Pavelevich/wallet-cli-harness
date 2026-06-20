# Wallet CLI Harness Decision Tree

Use this tree to route user language into `wallet-cli` commands.

## 1. Route The Domain

If the user asks about AgenC marketplace tasks, agents, registration, settlement, creator/worker flows, or AgenC wallet sends, leave this plugin and follow the host AgenC rules.

Otherwise treat the message as a personal `wallet-cli` request.

## 2. Pick The Wallet Intent

| User intent | Required inputs | Action |
| --- | --- | --- |
| What can this plugin do? | none | Show capability table, then ask what to run |
| Find devices, discover accounts, scan wallet | network | `account discover <network>` |
| Check wallet, balance, holdings | saved labels | `session view`, then `balances <label>` for each label |
| Transaction history | account label | `operations <label> --limit 20` |
| Receive/deposit address | account label, verification preference | `receive <label>` or `receive <label> --no-verify` |
| Send/transfer/pay | account label, recipient, amount with ticker | dry-run `send`, summarize, ask approval, then live `send` |
| Swap/convert/trade | from, to, amount, account, provider as needed | `swap quote`, `swap execute`, or `swap status` |
| Token metadata | network + address, or token id | `assets token` or `assets token-by-id` |
| Genuine check | none | `genuine-check` |
| Reset session | none | `session reset` |

## 3. Ask Only For Missing Inputs

Examples:

- Missing network for discovery: `Which network should I scan: bitcoin, ethereum, or solana?`
- Missing account label for balance/history/receive: run `session view`, show labels, ask which label.
- Missing send details: ask only for missing account label, recipient, amount, or ticker.

## 4. Run Through The Harness

Prefer:

```bash
python3 scripts/wallet_cli_harness.py -- <wallet-cli args>
```

The harness appends `--output json`, validates flags, and parses the final JSON object.

## 5. Report Results

- Report concrete values from the final JSON object.
- Mention how many labels/accounts were checked.
- For balances, list nonzero balances first, then zeros.
- For sends, summarize recipient, amount, and fee before asking for approval.
- For command errors, report the wallet-cli error and ask whether to retry or adjust inputs.
