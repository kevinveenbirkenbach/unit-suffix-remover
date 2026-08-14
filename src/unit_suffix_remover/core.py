import os
import re
import subprocess

VALID_EXTS = (".service", ".timer")
UNIT_DIR = "/etc/systemd/system"

REQUIRED_BINARIES = ("systemctl",)
EXIT_MISSING_BINARY = 127


class MissingBinaryError(RuntimeError):
    """A required external command is not installed.

    Args:
        binary: Name of the missing executable.
    """

    def __init__(self, binary):
        super().__init__(f"required command '{binary}' is not installed")
        self.binary = binary


def has_exact_suffix(filename, suffix):
    """Return True if the unit file carries exactly the given suffix.

    Accepted shapes for suffix 'infinito':
      <prefix>.infinito.service, <prefix>.infinito.timer,
      <prefix>.infinito@.service, <prefix>.infinito@<instance>.timer

    Args:
        filename: Unit file name or path.
        suffix: Suffix token that must sit directly before '@' or the extension.
    """
    base = os.path.basename(filename)
    pattern = rf"^[^@]+\.{re.escape(suffix)}(?:@.*)?\.(?:service|timer)$"
    return re.fullmatch(pattern, base) is not None


def iter_matching_units(unit_dir, suffix):
    """Yield paths of all unit files inside unit_dir that carry the suffix.

    Args:
        unit_dir: Directory holding the systemd unit files.
        suffix: Suffix token to match exactly.
    """
    try:
        entries = os.listdir(unit_dir)
    except FileNotFoundError:
        return

    for name in entries:
        if not name.endswith(VALID_EXTS):
            continue
        full_path = os.path.join(unit_dir, name)
        if os.path.isfile(full_path) and has_exact_suffix(name, suffix):
            yield full_path


def systemctl(*args, quiet=True):
    """Run systemctl and return its exit code.

    Args:
        args: Arguments handed to systemctl.
        quiet: Discard stdout and stderr when True.
    """
    streams = {}
    if quiet:
        streams = {"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}

    try:
        return subprocess.run(["systemctl", *args], check=False, **streams).returncode
    except FileNotFoundError as error:
        raise MissingBinaryError("systemctl") from error


def process_unit(unit_file, dry_run=False):
    """Stop, disable and remove a single systemd unit.

    Args:
        unit_file: Absolute path of the unit file.
        dry_run: Report the planned actions without performing them.
    """
    unit = os.path.basename(unit_file)
    print(f"\n=== Processing unit: {unit} ===")

    if not dry_run:
        systemctl("stop", unit)
    print(f"→ Stopped {unit} (if active)")

    if not dry_run:
        systemctl("disable", unit)
    print(f"→ Disabled {unit} (if enabled)")

    if dry_run:
        print(f"→ Would remove file: {unit_file}")
        return

    try:
        os.remove(unit_file)
        print(f"→ Removed file: {unit_file}")
    except FileNotFoundError:
        print(f"→ File not found (already removed): {unit_file}")
