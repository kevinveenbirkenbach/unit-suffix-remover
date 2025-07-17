#!/usr/bin/env python3

import argparse
import glob
import os
import subprocess
import sys


def process_unit(unit_file, dry_run=False):
    unit = os.path.basename(unit_file)
    print(f"\n=== Processing unit: {unit} ===")

    # Stop unit if active
    cmd_stop = ["systemctl", "stop", unit]
    if not dry_run:
        subprocess.run(cmd_stop, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"→ Stopped {unit} (if active)")

    # Disable unit if enabled
    cmd_disable = ["systemctl", "disable", unit]
    if not dry_run:
        subprocess.run(cmd_disable, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"→ Disabled {unit} (if enabled)")

    # Remove unit file
    if not dry_run:
        os.remove(unit_file)
    print(f"→ Removed file: {unit_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Stop, disable, and remove systemd units matching the given suffix in /etc/systemd/system."
    )
    parser.add_argument(
        "-s", "--suffix",
        required=True,
        help="Suffix of unit files to target (e.g. 'cymais' for *.cymais.timer and *.cymais.service)."
    )
    parser.add_argument(
        "-d", "--dry-run",
        action="store_true",
        help="Show actions without executing them."
    )
    args = parser.parse_args()

    suffix = args.suffix
    unit_dir = "/etc/systemd/system"
    patterns = [f"*.{suffix}.timer", f"*.{suffix}.service"]

    print(f"Searching for units with suffix '{suffix}' in {unit_dir}...")

    found = False
    for pattern in patterns:
        glob_path = os.path.join(unit_dir, pattern)
        for unit_file in glob.glob(glob_path):
            found = True
            process_unit(unit_file, dry_run=args.dry_run)

    if not found:
        print("No matching units found.")
        sys.exit(0)

    # Reload systemd daemon
    print("\n→ Reloading systemd daemon...")
    cmd_reload = ["systemctl", "daemon-reload"]
    if not args.dry_run:
        subprocess.run(cmd_reload)

    print("Done. All matching units have been processed.")


if __name__ == "__main__":
    main()
