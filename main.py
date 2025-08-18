#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys

VALID_EXTS = (".service", ".timer")

def has_suffix_before_at(filename: str, suffix: str) -> bool:
    """
    Check that the unit 'filename' has '.<suffix>' appearing BEFORE any '@'.
    Accepts these patterns (X = anything, opt = optional):
      - X.<suffix>.service|.timer
      - X.<suffix>@opt.service|.timer
    Rejects:
      - X@opt.<suffix>.service|.timer
    """
    # Strip directory
    base = os.path.basename(filename)

    # Must end with .service or .timer
    if not base.endswith(VALID_EXTS):
        return False

    # Locate markers
    ext_dot = base.rfind(".")  # start of .service/.timer
    at_pos = base.find("@")
    suf_token = f".{suffix}"
    suf_pos = base.find(suf_token)

    if suf_pos == -1:
        return False

    # Ensure '.<suffix>' is part of the main name (i.e., before extension)
    if suf_pos > ext_dot:
        return False

    # If there is an '@', it must come AFTER the '.<suffix>'
    if at_pos != -1 and at_pos < (suf_pos + len(suf_token)):
        return False

    return True


def iter_matching_units(unit_dir: str, suffix: str):
    """
    Yield absolute paths of unit files in unit_dir that:
      - end with .service or .timer
      - contain '.<suffix>' before any optional '@'
    """
    try:
        entries = os.listdir(unit_dir)
    except FileNotFoundError:
        return

    for name in entries:
        if name.endswith(VALID_EXTS):
            full = os.path.join(unit_dir, name)
            if os.path.isfile(full) and has_suffix_before_at(name, suffix):
                yield full


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
        try:
            os.remove(unit_file)
            print(f"→ Removed file: {unit_file}")
        except FileNotFoundError:
            print(f"→ File not found (already removed): {unit_file}")
    else:
        print(f"→ Would remove file: {unit_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Stop, disable, and remove systemd units matching the given suffix in /etc/systemd/system, ensuring the suffix appears before any '@'."
    )
    parser.add_argument(
        "-s", "--suffix",
        required=True,
        help="Software suffix used in unit filenames (e.g. 'cymais' for '*.cymais.service' / '*.cymais@*.timer')."
    )
    parser.add_argument(
        "-d", "--dry-run",
        action="store_true",
        help="Show actions without executing them."
    )
    args = parser.parse_args()

    suffix = args.suffix
    unit_dir = "/etc/systemd/system"

    print(f"Searching for units with suffix '{suffix}' in {unit_dir} (suffix must appear before any '@')...")

    matched = list(iter_matching_units(unit_dir, suffix))

    if not matched:
        print("No matching units found.")
        sys.exit(0)

    for unit_file in sorted(matched):
        process_unit(unit_file, dry_run=args.dry_run)

    # Reload systemd daemon
    print("\n→ Reloading systemd daemon...")
    cmd_reload = ["systemctl", "daemon-reload"]
    if not args.dry_run:
        subprocess.run(cmd_reload)

    print("Done. All matching units have been processed.")


if __name__ == "__main__":
    main()
