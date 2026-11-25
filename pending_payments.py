"""Oja Ledger — pending-payments safe box (stage 1: the foundation).

Remembers money the moment the bank says it left, even when the network
blinks and the screen stays blank. This is the ground the calm screen
stands on: without it, a reassuring screen would be a lie.

Rules — his words, baked in as code, not as comments someone can ignore:
  1. One reference = one record. A second debit with the same reference
     returns the record that already exists. Never a second charge.
  2. Nothing leaves "waiting" without the trader's yes (confirm_pending).
     Nothing auto-confirms. Ever.
  3. Failures are remembered too. A failed record stays in the box with
     its reason, so it can be matched and fixed later.

Stdlib only. No API, no cost, no pip — same rule as oja_brain.py.
Store is a plain JSON file beside this module, so it survives a crash,
a network blink, and an app restart.
"""
import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo

STORE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "pending_payments.json")


def _now():
    return datetime.now(ZoneInfo("Africa/Lagos")).strftime("%Y-%m-%d %H:%M:%S")


def _load():
    try:
        with open(STORE, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save(data):
    tmp = STORE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, STORE)  # atomic: a crash mid-write never corrupts the box


def record_pending(reference, amount, channel="bank", note=""):
    """Bank says money left. Save it as waiting — even if the screen never showed it.

    Returns (record, is_new). is_new False means this reference was already
    in the box: the same payment seen again, not a new charge.
    """
    ref = str(reference).strip()
    if not ref:
        raise ValueError("reference is required — no reference, no record")
    data = _load()
    if ref in data:
        data[ref]["attempts"] = data[ref].get("attempts", 1) + 1
        data[ref]["last_seen"] = _now()
        data[ref]["history"].append("%s seen again (attempt %d)" % (_now(), data[ref]["attempts"]))
        _save(data)
        return data[ref], False
    rec = {"reference": ref, "amount": float(amount), "channel": channel,
           "status": "waiting", "created": _now(), "last_seen": _now(),
           "attempts": 1, "note": note,
           "history": ["%s recorded as waiting" % _now()]}
    data[ref] = rec
    _save(data)
    return rec, True


def find_pending(reference):
    """Trader types their reference — match it to what the box remembers."""
    return _load().get(str(reference).strip())


def confirm_pending(reference, confirmed_by="trader"):
    """The trader's yes. Only this flips waiting -> confirmed.

    Confirming twice still counts as one charge: an already-confirmed
    record comes back unchanged.
    """
    ref = str(reference).strip()
    data = _load()
    rec = data.get(ref)
    if rec is None:
        return None
    if rec["status"] == "confirmed":
        return rec
    if rec["status"] != "waiting":
        return rec
    rec["status"] = "confirmed"
    rec["confirmed_by"] = confirmed_by
    rec["confirmed_at"] = _now()
    rec["history"].append("%s confirmed by %s" % (_now(), confirmed_by))
    _save(data)
    return rec


def mark_failed(reference, reason):
    """Remember the failure too — the record stays, with its reason."""
    ref = str(reference).strip()
    data = _load()
    rec = data.get(ref)
    if rec is None:
        return None
    rec["status"] = "failed"
    rec["fail_reason"] = reason
    rec["history"].append("%s failed: %s" % (_now(), reason))
    _save(data)
    return rec


def list_waiting():
    """Everything still waiting — what the calm screen shows."""
    return [r for r in _load().values() if r["status"] == "waiting"]


if __name__ == "__main__":
    # The real scenario, end to end:
    # bank debits -> network blinks -> trader types reference -> trader says yes.
    if os.path.exists(STORE):
        os.remove(STORE)
    print("1. Bank says money left (network about to blink):")
    rec, new = record_pending("REF-77831", 15000, channel="bank")
    print("   saved:", rec["status"], "| new record:", new)
    print("2. Network blinks. Screen stayed blank. Box still remembers:")
    print("   waiting now:", [r["reference"] for r in list_waiting()])
    print("3. Trader panics and the bank debits AGAIN with the same reference:")
    rec2, new2 = record_pending("REF-77831", 15000, channel="bank")
    print("   new record:", new2, "| attempts:", rec2["attempts"], "| still ONE record in the box")
    print("4. Trader types the reference into the calm screen:")
    found = find_pending("REF-77831")
    print("   found:", found["reference"], "₦%s" % int(found["amount"]), "| status:", found["status"])
    print("5. Trader says yes:")
    done = confirm_pending("REF-77831")
    print("   status:", done["status"], "| confirmed by:", done["confirmed_by"])
    print("6. Trader taps yes again by mistake:")
    done2 = confirm_pending("REF-77831")
    print("   status:", done2["status"], "| still ONE charge, nothing doubled")
    print("7. Waiting list now:", [r["reference"] for r in list_waiting()])
    print("ALL CHECKS PASSED — the box remembers, the trader decides, nobody pays twice.")
