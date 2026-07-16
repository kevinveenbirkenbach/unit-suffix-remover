# 📦 unit-suffix-remover (usure)
[![GitHub Sponsors](https://img.shields.io/badge/Sponsor-GitHub%20Sponsors-blue?logo=github)](https://github.com/sponsors/kevinveenbirkenbach) [![Patreon](https://img.shields.io/badge/Support-Patreon-orange?logo=patreon)](https://www.patreon.com/c/kevinveenbirkenbach) [![Buy Me a Coffee](https://img.shields.io/badge/Buy%20me%20a%20Coffee-Funding-yellow?logo=buymeacoffee)](https://buymeacoffee.com/kevinveenbirkenbach) [![PayPal](https://img.shields.io/badge/Donate-PayPal-blue?logo=paypal)](https://s.veen.world/paypaldonate)


> Python CLI to stop, disable, and remove systemd `.timer` and `.service` units by suffix. 🔧🧹

## 🚀 Installation

Install via [Kevin’s package manager](https://github.com/kevinveenbirkenbach/package-manager):

```bash
pkgmgr install usure
```

## ⚙️ Usage

```bash
usure -s SUFFIX [--dry-run]
```

* `-s`, `--suffix`: suffix of unit files to target (e.g. `cymais` for `*.cymais.timer` and `*.cymais.service`). **Required**.
* `-d`, `--dry-run`: show actions without executing them.

For full options:

```bash
usure --help
```

## 👤 Author

Developed by **Kevin Veen‑Birkenbach**
🌐 [veen.world](https://www.veen.world/)

## 📜 License

This project is licensed under the **MIT License**.
