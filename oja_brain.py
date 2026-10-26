"""Oja Ledger brain: turn a Pidgin/English market sentence into a ledger entry.
Rule-based v0 (no API, no cost). Llama will replace/boost this later."""
import json, re, sys
from datetime import datetime
from zoneinfo import ZoneInfo

SELL = ["sell", "sold", "don sell", "customer buy", "person buy", "buy from me"]
BUY = [" i buy", " i don buy", "bought", "restock", "i collect", "market buy", "pay for goods"]
OWE = ["owe", "credit", "go pay later", "never pay", "dey owe"]

NUM_WORDS = {"one":1,"two":2,"three":3,"four":4,"five":5,"six":6,"seven":7,"eight":8,
             "nine":9,"ten":10,"eleven":11,"twelve":12,"half":0.5,"dozen":12}

def money(tok):
    t = tok.lower().replace(",", "").replace("₦", "").replace("naira", "").strip()
    m = re.fullmatch(r"(\d+(?:\.\d+)?)(k)?", t)
    if not m: return None
    v = float(m.group(1)); return v * 1000 if m.group(2) else v

def parse(text):
    low = " " + text.lower() + " "
    kind = "sale"
    if any(w in low for w in OWE): kind = "debt"
    elif any(w in low for w in BUY): kind = "purchase"
    # "Mama Chidi buy..." = a customer bought from me = sale
    elif " buy " in low: kind = "sale"

    # price: "2k each", "for 1500", "₦2,000", "at 500"
    price, each = None, False
    pm = re.search(r"(?:for|at|₦|n)\s*([\d,\.]+k?)|([\d,\.]+k)\b|([\d,]+)\s*naira", low)
    if pm:
        price = money(next(g for g in pm.groups() if g))
        each = bool(re.search(r"\b(each|per|one one|apiece)\b", low[pm.end():pm.end()+15]))
    if price is None:  # bare amount like "owe me 1500"
        nums = [money(n) for n in re.findall(r"\b\d[\d,]*k?\b", low)]
        nums = [n for n in nums if n and n >= 100]
        if nums: price = max(nums)
    # quantity: first number (digit or word) that isn't the price
    qty = None
    for tok in re.findall(r"[a-z]+|\d+(?:\.\d+)?k?", low):
        v = NUM_WORDS.get(tok) if tok in NUM_WORDS else (float(tok) if re.fullmatch(r"\d+(?:\.\d+)?", tok) else None)
        if v is not None and (price is None or v != price):
            qty = v; break
    qty = qty or 1
    # item: words after the quantity, before the price
    item = None
    im = re.search(r"(?:\d+|" + "|".join(NUM_WORDS) + r")\s+((?:[a-z]+\s?){1,3}?)(?=\s*(?:for|at|₦|\d|each|per|$))", low)
    if im: item = im.group(1).strip()
    if kind == "debt":
        dm = re.search(r"\bfor\s+([a-z]+(?:\s[a-z]+)?)", low)
        item = dm.group(1) if dm else item
        who = re.match(r"\s*([a-z]+(?:\s[a-z]+)?)\s+(?:dey\s+)?owe", low)
        qty = 1
        out_who = who.group(1).title() if who else None
    total = (price * qty if each else price) if price is not None else None
    unit = (price if each else (round(price/qty, 2) if price and qty else None)) if price is not None else None
    return {"time": datetime.now(ZoneInfo("Africa/Lagos")).strftime("%Y-%m-%d %H:%M"), "type": kind, "item": item,
            "qty": qty, "unit_price": unit, "total": total, "heard": text,
            "status": "needs_confirm", **({"who": out_who} if kind == "debt" else {})}

if __name__ == "__main__":
    tests = sys.argv[1:] or ["I sell 3 tuber yam 2k each", "Mama Chidi buy 2 bag rice for 90000",
             "I don buy 5 crate egg for 25k", "Emeka owe me 1500 for pepper"]
    for t in tests: print(json.dumps(parse(t), ensure_ascii=False))
