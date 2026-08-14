#!/bin/sh
set -eu

fail() {
    echo "FAIL: $1" >&2
    exit 1
}

UNSURE="$(command -v unsure)" || fail "unsure is not on PATH after install"
echo "ok: unsure installed at ${UNSURE}"

command -v usure >/dev/null || fail "the usure alias is not on PATH after install"
echo "ok: usure alias installed"

case "${UNSURE}" in
    /usr/local/bin/*) ;;
    *) fail "unsure resolved to ${UNSURE}, outside the install prefix" ;;
esac
echo "ok: resolved from the installed package, not the source tree"

command -v systemctl >/dev/null || fail "systemctl is missing from the image"
echo "ok: real systemctl present at $(command -v systemctl)"

unsure --help | grep -q "systemd units" || fail "--help does not describe the tool"
echo "ok: --help"

set +e
unsure --unit-dir /tmp >/dev/null 2>&1
status=$?
set -e
[ "${status}" -eq 2 ] || fail "missing --suffix exited ${status}, expected 2"
echo "ok: missing --suffix exits 2"

mkdir -p /tmp/units
: >/tmp/units/web.infinito.service
: >/tmp/units/db.infinito@main.timer
: >/tmp/units/web.other.service
: >/tmp/units/web.infinito.nexus.timer

output="$(unsure -s infinito --unit-dir /tmp/units --dry-run)"
echo "${output}" | grep -q "Would remove file" || fail "dry-run did not announce a removal"
[ -f /tmp/units/web.infinito.service ] || fail "dry-run removed a unit file"
echo "ok: --dry-run keeps every unit file"

unsure -s infinito --unit-dir /tmp/units >/dev/null
[ ! -f /tmp/units/web.infinito.service ] || fail "web.infinito.service was not removed"
[ ! -f /tmp/units/db.infinito@main.timer ] || fail "db.infinito@main.timer was not removed"
[ -f /tmp/units/web.other.service ] || fail "web.other.service was removed but does not match"
[ -f /tmp/units/web.infinito.nexus.timer ] || fail "web.infinito.nexus.timer was removed but does not match"
echo "ok: removes exactly the units carrying the suffix, through real systemctl"

output="$(unsure -s nothing --unit-dir /tmp/units)"
echo "${output}" | grep -q "No matching units found." || fail "empty match not reported"
echo "ok: reports when nothing matches"

: >/tmp/units/late.infinito.service

set +e
output="$(env PATH=/nonexistent-bin "${UNSURE}" -s infinito --unit-dir /tmp/units 2>&1)"
status=$?
set -e
[ "${status}" -eq 127 ] || fail "missing systemctl exited ${status}, expected 127"
echo "${output}" | grep -q "required command 'systemctl' is not installed" || fail "missing systemctl message wrong"
if echo "${output}" | grep -q "Traceback"; then
    fail "missing systemctl produced a traceback"
fi
[ -f /tmp/units/late.infinito.service ] || fail "unit file removed despite the missing systemctl"
echo "ok: missing systemctl exits 127 cleanly and removes nothing"

echo "ALL E2E CHECKS PASSED"
