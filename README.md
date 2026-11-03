# Oja Ledger 🧺📒

**Talk your sales. We write the book.**

A phone-first ledger for Nigerian market traders. Say a sale in Pidgin, point the camera at a product, and **Meta Muse Spark** does the bookkeeping: sales, purchases, debts, prices and stock.

🔗 **Live app:** https://djebiswags.github.io/oja-ledger/ (open in Chrome on Android, add to home screen)
🏆 Built during the **Meta Global AI Developer Hackathon (Oct 26 – Nov 4, 2026)**

---

## The problem
Millions of traders in Nigerian markets keep their books in their heads or in a torn exercise book. Debts get forgotten, stock runs out without warning, and nobody knows the day's real profit. Most bookkeeping apps expect typing, English and forms. Traders talk.

## What Oja Ledger does
| | Feature | Meta AI |
|---|---|---|
| 🎤 | **Talk it in.** "Mama Ngozi go pay 3k Friday for rice" becomes a DEBT entry with who, what and how much | Muse Spark reads Pidgin or English into a structured entry |
| ✅ | **Confirm in one tap.** Every entry shows a card first, with "Read by Meta Muse". Nothing saves without the trader's OK | |
| 📸 | **Mama's Shelf.** Snap a product; it's named the way traders say it ("Peak Milk 400g", tin, Provisions). Set price and stock | Muse Spark vision |
| 🔍 | **Price Scan.** Point the camera at a product and *her own* price and stock pop up. Sell 1 in a tap, or add an unknown item | Muse Spark vision, live every ~2 s |
| 📉 | **Stock tracks itself.** Sales cut stock, purchases restock, low stock gets a badge | |
| 💬 | **WhatsApp built in.** Send debt reminders, receipts, and a shop price list as one message | |
| 📴 | **Works offline.** Installable PWA; a rule-based parser takes over when there's no network | |

**Every trader keeps her own prices.** Prices in Nigerian markets vary by stall, so there is no shared price board; the AI only recognises the product and shows *her* tag.

## How Meta AI is used
- **Model:** Meta **Muse Spark Open** (`meta/muse-spark-open`), with Muse Spark 1.3 and Muse Glimmer 30B selectable in ⚙️ Settings.
- **Access:** through [Puter.js](https://developer.puter.com/ai/meta/muse-spark-open/), so the trader needs **no API key and no card**. First use shows a one-time free Puter sign-in.
- **Ledger reading:** the prompt gives Muse the trader's shelf names, so "2 peak" matches "Peak Milk 400g". Muse returns JSON (type, item, qty, unit price, total, who), and the app checks the maths before showing the confirm card.
- **Vision:** photos are shrunk on the phone (512 px JPEG) before they're sent, to save data.
- **Other routes:** Groq, Fireworks (Llama 4 Maverick) or any OpenAI-compatible endpoint, such as the Meta Model API, can be plugged in from Settings. Keys stay in the phone's localStorage only.

## Architecture
```
Voice (phone speech-to-text, en-NG) ─┐
Typed text ──────────────────────────┼─► Meta Muse Spark ─► JSON entry ─► Confirm card ─► Ledger + Shelf (localStorage)
                     (offline: rules)┘                                                         │
Camera ─► 512px JPEG ─► Meta Muse Spark vision ─► match trader's shelf ─► her price + stock   └─► WhatsApp share
```
One `index.html`, no build step and no server. Data never leaves the phone except the text or photo sent to the model.

## Try it
1. Open the live app, go to **Shelf** and snap two or three products, giving each a price and stock.
2. On **Book**, tap 🎤 and say "I sell 2 Peak milk", or tap one of the example chips.
3. Tap **Correct!** and watch the totals and stock update.
4. Back on **Shelf**, tap **Price Scan** and point at a product.

Offline brain, for developers:
```bash
python3 oja_brain.py "I sell 3 tuber yam 2k each"
# {"type": "sale", "item": "tuber yam", "qty": 3.0, "unit_price": 2000.0, "total": 6000.0, "status": "needs_confirm"}
```

## Built during the event
- v0 rule-based brain, confirm screen, daily totals
- v2 WhatsApp debt confirmations and receipts, offline PWA
- v3 Mama's Shelf: snap and tag, prices, self-updating stock
- v4 Voice input and WhatsApp price list
- v5 Free Meta Muse Spark via Puter, no key
- v6 Price Scan: live camera, the trader's own price tag
- v7 Muse Spark reads typed and spoken ledger entries, Pidgin included

## Next
- Pidgin-tuned speech recognition (Meta omniASR) for noisy markets
- Weekly profit summary and restock suggestions from Muse
- Shared books for family stalls

## License
MIT
