import argparse
import sys

from unit_suffix_remover.core import (
    EXIT_MISSING_BINARY,
    UNIT_DIR,
    MissingBinaryError,
    iter_matching_units,
    process_unit,
    systemctl,
)


def build_parser():
    """Return the argument parser for the unsure command."""
    parser = argparse.ArgumentParser(
        description=(
            "Stop, disable, and remove systemd units in /etc/systemd/system "
            "that have the EXACT given suffix before '@' or before the extension."
        )
    )
    parser.add_argument(
        "-s",
        "--suffix",
        required=True,
        help=(
            "Exact suffix to match (e.g. 'infinito' for '*.infinito.service' "
            "or '*.infinito@*.timer')."
        ),
    )
    parser.add_argument(
        "-d",
        "--dry-run",
        action="store_true",
        help="Show planned actions without executing them.",
    )
    parser.add_argument(
        "--unit-dir",
        default=UNIT_DIR,
        help=f"Directory to scan for unit files (default: {UNIT_DIR}).",
    )
    return parser


def main(argv=None):
    """Remove every systemd unit carrying the given suffix.

    Args:
        argv: Argument list, defaults to sys.argv[1:].

    Returns:
        Process exit code.
    """
    args = build_parser().parse_args(argv)

    print(
        f"Searching for units with EXACT suffix '{args.suffix}' in {args.unit_dir}..."
    )

    matched_units = sorted(iter_matching_units(args.unit_dir, args.suffix))
    if not matched_units:
        print("No matching units found.")
        return 0

    try:
        for unit_file in matched_units:
            process_unit(unit_file, dry_run=args.dry_run)

        print("\n→ Reloading systemd daemon...")
        if not args.dry_run:
            systemctl("daemon-reload", quiet=False)
    except MissingBinaryError as error:
        print(f"Error: {error}", file=sys.stderr)
        return EXIT_MISSING_BINARY

    print("Done. All matching units have been processed.")

    return 0
