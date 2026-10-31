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

## 🛒 Mama's Shelf: snap a product, AI names it, set price, stock tracks itself
Powered by **Meta Muse Spark / Llama 4 via the Meta API, Fireworks, or Groq** (pick one in ⚙️ Settings).

1. 📸 Open the **Shelf** tab and tap **Snap product**. The photo is shrunk on the phone (512px JPEG) before it is sent.
2. 🦙 A vision model names it the way traders say it ("Peak Milk 400g", tin, Provisions). Every product shows which model tagged it.
3. 🏷️ Fix the name if needed, type the price (`1.8k`, `1800` or `N1,800` all work) and how many you have.
4. 📉 When you confirm a sale in the ledger ("I sell 2 peak milk"), the shelf finds the product, fills the price if you didn't say it, and cuts the stock. Purchases add stock back. Low stock (3 or less) gets a badge.
5. 📊 **Today on the shelf** shows items sold, money in and what needs restocking.

| Provider | Default model | Key |
|---|---|---|
| Groq (default, free, no card) | `qwen/qwen3.8-27b` stand-in; switch to Meta `meta-models/muse-spark-open` once Groq grants access | [console.groq.com/keys](https://console.groq.com/keys) |
| Fireworks | Meta Llama 4 Maverick (`accounts/fireworks/models/llama4-maverick-instruct-basic`) | [fireworks.ai](https://fireworks.ai/account/api-keys) |
| Custom | Any OpenAI-compatible base URL + model, e.g. the Meta Model API (Muse Spark) | from your provider |

🔒 Keys are saved only in the phone's browser (localStorage), one per provider, and go straight to the provider you pick. No key, or no network? You type the name yourself and everything still works offline.

## Roadmap
- [x] Text → ledger entry (rule-based v0)
- [x] Confirm screen + today's totals
- [x] Send on WhatsApp: debt confirmations and receipts
- [x] Installable app that works offline (no network in the market? no wahala)
- [x] Mama's Shelf: snap-and-tag products, prices and self-updating stock
- [ ] Voice → text with omniASR
- [ ] Llama upgrade for messy, real-world sentences


## Free Meta model, no key (v5)
Mama's Shelf now defaults to **Meta Muse Spark Open** through [Puter.js](https://developer.puter.com/ai/meta/muse-spark-open/) (`meta/muse-spark-open`). No API key or card: the first snap shows a one-time free Puter sign-in. Groq, Fireworks and a custom OpenAI-compatible endpoint (e.g. the Meta Model API) are still in Settings.

Voice: tap 🎤 on the Book tab; it uses the phone's built-in speech recognition (en-NG) and fills the entry for confirmation.
