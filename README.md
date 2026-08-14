# 📦 unit-suffix-remover (unsure)

[![GitHub Sponsors](https://img.shields.io/badge/Sponsor-GitHub%20Sponsors-blue?logo=github)](https://github.com/sponsors/kevinveenbirkenbach) [![Patreon](https://img.shields.io/badge/Support-Patreon-orange?logo=patreon)](https://www.patreon.com/c/kevinveenbirkenbach) [![Buy Me a Coffee](https://img.shields.io/badge/Buy%20me%20a%20Coffee-Funding-yellow?logo=buymeacoffee)](https://buymeacoffee.com/kevinveenbirkenbach) [![PayPal](https://img.shields.io/badge/Donate-PayPal-blue?logo=paypal)](https://s.veen.world/paypaldonate)

> Python CLI to stop, disable, and remove systemd `.timer` and `.service` units by suffix. 🔧🧹

## 🧭 How it works

```mermaid
flowchart TD
    A["unsure -s SUFFIX"] --> B["list *.service and *.timer in the unit dir"]
    B --> C{"name is PREFIX.SUFFIX with an optional @INSTANCE?"}
    C -- no --> B
    C -- yes --> D["collect the unit"]
    D --> E{"any unit collected?"}
    E -- no --> Y["No matching units found - exit 0"]
    E -- yes --> F{"--dry-run?"}
    F -- yes --> G["announce the removal, change nothing"]
    F -- no --> H["systemctl stop"]
    H --> I["systemctl disable"]
    I --> J["delete the unit file"]
    J --> K["systemctl daemon-reload"]
    G --> Z["exit 0"]
    K --> Z
```

## 🚀 Installation

```bash
pip install unit-suffix-remover
```

pip is the single supported installation path.

The package installs **two** identical commands: `unsure` (primary) and `usure` (kept for older documentation and scripts).

## 🔧 Requirements

* **Python 3.10+** 🐍
* **`systemctl`** on `PATH` (systemd)

If `systemctl` is missing, the command exits with code `127` and a one‑line error instead of a traceback.

## ⚙️ Usage

```bash
unsure -s SUFFIX [--dry-run] [--unit-dir DIR]
```

* `-s`, `--suffix`: suffix of unit files to target (e.g. `infinito` for `*.infinito.timer` and `*.infinito.service`). **Required**.
* `-d`, `--dry-run`: show actions without executing them.
* `--unit-dir`: directory to scan. Defaults to `/etc/systemd/system`.

Only the **exact** suffix directly before `@` or the extension matches:

| Unit file | `-s infinito` |
| --- | --- |
| `web.infinito.service` | ✅ matched |
| `web.infinito@db.timer` | ✅ matched |
| `web.infinito.nexus.timer` | ❌ extra part after the suffix |
| `web@db.infinito.timer` | ❌ suffix sits after `@` |
| `web.infinitoX.service` | ❌ suffix is only a prefix |

For full options:

```bash
unsure --help
```

### Exit codes

| Code | Meaning |
| --- | --- |
| `0` | Finished, or nothing matched. |
| `2` | Invalid command line arguments. |
| `127` | A required command is not installed. |

## 🧪 Development

```bash
make lint              # ruff check + ruff format --check
make format            # apply ruff format
make test              # unit + integration tests
make test-unit
make test-integration
make test-e2e          # install the package in a container and exercise the CLI
```

Tests run against the working tree — the `Makefile` puts `src/` on `PYTHONPATH`, so no install is needed. `--unit-dir` lets the integration tests work on a temporary directory instead of `/etc/systemd/system`.

## 👤 Author

Developed by **Kevin Veen‑Birkenbach**
🌐 [veen.world](https://www.veen.world/)

## 📜 License

This project is licensed under the **MIT License**.
