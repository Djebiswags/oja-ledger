# Oja Ledger 🧺📒

**Talk your sales. We write the book.**

Oja Ledger turns a market trader's Pidgin voice note into a clean, confirmed ledger entry.
Built during the **Meta Global AI Developer Hackathon (Oct 26 – Nov 4, 2026)**.

## How it works
1. 🎙️ Trader records a voice note in Nigerian Pidgin
2. 📝 Meta **omniASR** turns speech into text
3. 🧠 The Oja brain (rules now, **Llama** next) pulls out type, item, quantity, price and total
4. ✅ Trader taps **Confirm**, and the entry lands in the ledger

## Try the brain
```bash
python3 oja_brain.py "I sell 3 tuber yam 2k each"
```
```json
{"type": "sale", "item": "tuber yam", "qty": 3.0, "unit_price": 2000.0, "total": 6000.0, "status": "needs_confirm"}
```

It understands sales ("Mama Chidi buy 2 bag rice for 90000"), purchases ("I don buy 5 crate egg for 25k") and debts ("Emeka owe me 1500 for pepper").

## Roadmap
- [x] Text → ledger entry (rule-based v0)
- [ ] Voice → text with omniASR
- [ ] Llama upgrade for messy, real-world sentences
- [ ] Simple confirm screen + daily totals
