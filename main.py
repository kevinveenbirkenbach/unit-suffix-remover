#!/usr/bin/env python3
import argparse
import os
import re
import subprocess
import sys

# Valid systemd unit extensions
VALID_EXTS = (".service", ".timer")


def has_exact_suffix(filename: str, suffix: str) -> bool:
    """
    Check if the given unit filename matches the exact suffix pattern.

    Allowed:
      <anything-without-@>.<suffix>.service
      <anything-without-@>.<suffix>.timer
      <anything-without-@>.<suffix>@.service
      <anything-without-@>.<suffix>@.timer
      <anything-without-@>.<suffix>@<instance>.service
      <anything-without-@>.<suffix>@<instance>.timer

    Disallowed (examples for suffix='infinito'):
      foo.infinito.nexus.timer     (extra part after suffix)
      foo@db.infinito.timer        (suffix appears after '@')
      foo.infinitoX.service        (suffix only as prefix, not exact match)
    """
    base = os.path.basename(filename)
    pattern = rf'^[^@]+\.{re.escape(suffix)}(?:@.*)?\.(?:service|timer)$'
    return re.fullmatch(pattern, base) is not None


def iter_matching_units(unit_dir: str, suffix: str):
    """
    Iterate over all unit files in unit_dir that match the given suffix.
    """
    try:
        entries = os.listdir(unit_dir)
    except FileNotFoundError:
        return

    for name in entries:
        if name.endswith(VALID_EXTS):
            full_path = os.path.join(unit_dir, name)
            if os.path.isfile(full_path) and has_exact_suffix(name, suffix):
                yield full_path


def process_unit(unit_file, dry_run=False):
    """
    Stop, disable, and remove a systemd unit file.
    """
    unit = os.path.basename(unit_file)
    print(f"\n=== Processing unit: {unit} ===")

    # Stop the unit if active
    cmd_stop = ["systemctl", "stop", unit]
    if not dry_run:
        subprocess.run(cmd_stop, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"→ Stopped {unit} (if active)")

    # Disable the unit if enabled
    cmd_disable = ["systemctl", "disable", unit]
    if not dry_run:
        subprocess.run(cmd_disable, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"→ Disabled {unit} (if enabled)")

    # Remove the unit file (works for files and symlinks)
    if not dry_run:
        try:
            os.remove(unit_file)
            print(f"→ Removed file: {unit_file}")
        except FileNotFoundError:
            print(f"→ File not found (already removed): {unit_file}")
    else:
        print(f"→ Would remove file: {unit_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Stop, disable, and remove systemd units in /etc/systemd/system "
                    "that have the EXACT given suffix before '@' or before the extension."
    )
    parser.add_argument(
        "-s", "--suffix",
        required=True,
        help="Exact suffix to match (e.g., 'infinito' for '*.infinito.service' or '*.infinito@*.timer')."
    )
    parser.add_argument(
        "-d", "--dry-run",
        action="store_true",
        help="Show planned actions without executing them."
    )
    args = parser.parse_args()

    unit_dir = "/etc/systemd/system"
    print(f"Searching for units with EXACT suffix '{args.suffix}' in {unit_dir}...")

    matched_units = list(iter_matching_units(unit_dir, args.suffix))
    if not matched_units:
        print("No matching units found.")
        sys.exit(0)

    for unit_file in sorted(matched_units):
        process_unit(unit_file, dry_run=args.dry_run)

    # Reload systemd daemon
    print("\n→ Reloading systemd daemon...")
    if not args.dry_run:
        subprocess.run(["systemctl", "daemon-reload"])
    print("Done. All matching units have been processed.")


if __name__ == "__main__":
    main()
