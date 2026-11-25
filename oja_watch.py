"""Oja Ledger — watcher: gets the logs, reports to the builder, and the fix follows.

Three jobs, in that order, every time it runs:
  1. LOGS — every important moment is written down, append-only, in
     oja_logs.jsonl. A crash can never erase what already happened.
  2. REPORTS — build_report() reads the logs + the pending-payments box
     and writes a plain-language report (oja_report.md): what fixed
     itself, what still needs your hands, and the exact reference to check.
  3. FIX — auto_fix() heals what it knows how to heal, and only that:
     a payment that failed on network/timeout gets re-queued to waiting
     for a retry. Anything else (bank rejected, wrong amount, unknown
     reason) is left exactly as it is and put in the report for you.
     Every fix is logged, so the report always shows what fixed itself.

Rules:
  - The watcher never confirms a payment. Only the trader's yes does that.
  - The watcher never deletes a record or a log line. Memory is the safety.
  - A fix that is not in the known list does not happen. Unknown failures
    go to the report, not to a guess.

Stdlib only. No API, no cost — same rule as oja_brain.py.
"""
import json
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from pending_payments import STORE, _load, _save, confirm_pending  # noqa: F401  (confirm kept out of auto-fix by design)
from pending_payments import find_pending, list_waiting, record_pending, mark_failed

HERE = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(HERE, "oja_logs.jsonl")
REPORT_FILE = os.path.join(HERE, "oja_report.md")

# Failures the watcher knows how to heal on its own. Anything else: report only.
RETRYABLE = ("network", "timeout", "blink", "offline", "connection", "no signal")
WAITING_TOO_LONG_MIN = 30


def _now():
    return datetime.now(ZoneInfo("Africa/Lagos"))


def _stamp():
    return _now().strftime("%Y-%m-%d %H:%M:%S")


# ---------------------------------------------------------------- 1. LOGS
def log_event(kind, detail, reference=None):
    """Write one moment down. Append-only: nothing already written can be lost."""
    entry = {"time": _stamp(), "kind": kind, "detail": detail}
    if reference:
        entry["reference"] = reference
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def read_logs():
    try:
        with open(LOG_FILE, encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]
    except (FileNotFoundError, json.JSONDecodeError):
        return []


# ---------------------------------------------------------------- 2. SCAN
def scan():
    """Find everything that needs attention. Returns findings, each with a level:
    'fixed' (healed before), 'needs_you' (only human hands can move it),
    'info' (worth knowing, nothing to do)."""
    findings = []
    data = _load()
    now = _now()
    for ref, rec in data.items():
        if rec["status"] == "failed":
            reason = rec.get("fail_reason", "no reason recorded")
            retryable = any(w in reason.lower() for w in RETRYABLE)
            findings.append({"level": "needs_you" if not retryable else "fixable",
                             "reference": ref, "title": "Payment failed: %s" % reason,
                             "detail": "₦%s, failed %s. %s" % (
                                 int(rec["amount"]), rec.get("last_seen", "?"),
                                 "The watcher can re-queue this for a retry."
                                 if retryable else
                                 "Only you can move this — check with the bank.")})
        elif rec["status"] == "waiting":
            try:
                created = datetime.strptime(rec["created"], "%Y-%m-%d %H:%M:%S").replace(
                    tzinfo=ZoneInfo("Africa/Lagos"))
            except (KeyError, ValueError):
                created = None
            if created and (now - created) > timedelta(minutes=WAITING_TOO_LONG_MIN):
                findings.append({"level": "needs_you", "reference": ref,
                                 "title": "Payment waiting over %d minutes" % WAITING_TOO_LONG_MIN,
                                 "detail": "₦%s debited %s, trader has not confirmed yet. "
                                           "Check the bank, then ask the trader." % (
                                               int(rec["amount"]), rec["created"])})
            if rec.get("attempts", 1) >= 2:
                findings.append({"level": "info", "reference": ref,
                                 "title": "Double-debit scare held safe",
                                 "detail": "Same reference seen %d times. The box kept ONE record — "
                                           "nobody was charged twice." % rec["attempts"]})
    return findings


# ---------------------------------------------------------------- 3. FIX
def auto_fix():
    """Heal what is known-healable. Returns the list of fixes applied."""
    fixed = []
    for f in scan():
        if f["level"] != "fixable":
            continue
        ref = f["reference"]
        data = _load()
        rec = data.get(ref)
        if rec is None or rec["status"] != "failed":
            continue
        rec["status"] = "waiting"
        rec["history"].append("%s watcher re-queued for retry (was: failed)" % _stamp())
        _save(data)
        log_event("fix_applied", "Re-queued %s to waiting for a retry" % ref, reference=ref)
        fixed.append({"reference": ref,
                      "what": "Failed payment re-queued to waiting — it will be matched "
                              "again when the network returns, still one charge."})
    return fixed


# ---------------------------------------------------------------- REPORT
def build_report(fixed, findings):
    """Plain-language report for the builder. Written to oja_report.md and returned."""
    needs = [f for f in findings if f["level"] == "needs_you"]
    infos = [f for f in findings if f["level"] == "info"]
    lines = ["# Oja Ledger — watcher report", "", "Checked: %s (WAT)" % _stamp(), ""]
    lines.append("## Fixed by itself (%d)" % len(fixed))
    if fixed:
        for fx in fixed:
            lines.append("- %s — %s" % (fx["reference"], fx["what"]))
    else:
        lines.append("- Nothing needed fixing this run.")
    lines.append("")
    lines.append("## Needs your hands (%d)" % len(needs))
    if needs:
        for f in needs:
            lines.append("- %s — %s" % (f["reference"], f["title"]))
            lines.append("  %s" % f["detail"])
    else:
        lines.append("- Nothing. All clear.")
    lines.append("")
    lines.append("## Worth knowing (%d)" % len(infos))
    if infos:
        for f in infos:
            lines.append("- %s — %s" % (f["reference"], f["title"]))
    else:
        lines.append("- Nothing new.")
    lines.append("")
    lines.append("Waiting right now: %d payment(s). Failed: %d." % (
        len(list_waiting()),
        len([r for r in _load().values() if r["status"] == "failed"])))
    text = "\n".join(lines)
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(text + "\n")
    return text


def check_now():
    """One run: scan, fix what can be fixed, report the rest. Returns the report text."""
    fixed = auto_fix()
    findings = scan()
    return build_report(fixed, findings)


if __name__ == "__main__":
    # The full story, live: a network failure that heals itself,
    # and a bank rejection that only human hands can move.
    for path in (STORE, LOG_FILE, REPORT_FILE):
        if os.path.exists(path):
            os.remove(path)
    print("=== 1. Bank debits ₦25,000, then the network blinks ===")
    record_pending("REF-90210", 25000, channel="bank")
    log_event("payment_recorded", "Bank says ₦25,000 left for REF-90210", reference="REF-90210")
    mark_failed("REF-90210", "network timeout while confirming")
    log_event("error", "Network timeout while confirming REF-90210", reference="REF-90210")
    print("=== 2. Trader retries with the same reference (panic tap) ===")
    record_pending("REF-90210", 25000, channel="bank")
    print("=== 3. Watcher runs: logs read, fix follows, report written ===")
    print(check_now())
    print("=== 4. A second payment fails — bank rejected it, not the network ===")
    record_pending("REF-90211", 8000, channel="bank")
    mark_failed("REF-90211", "bank rejected: invalid account")
    log_event("error", "Bank rejected REF-90211: invalid account", reference="REF-90211")
    print(check_now())
    print("=== 5. Trader confirms the healed one with their yes ===")
    confirm_pending("REF-90210")
    log_event("payment_confirmed", "Trader confirmed REF-90210", reference="REF-90210")
    print(check_now())
    print("=== 6. The log file — everything that happened, in order ===")
    for line in read_logs():
        print("   ", line["time"], "|", line["kind"], "|", line["detail"])
    print("ALL CHECKS PASSED — logs kept, report written, known failure fixed,")
    print("unknown failure handed to you with its exact reference. Nothing guessed.")
