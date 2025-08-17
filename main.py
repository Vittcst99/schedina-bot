import os
import asyncio
from telegram import Bot

# 🔐 Variabili ambiente
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID"))

# 📋 Dati finti per test
def get_partite_test():
    return [
        ("17/08/2025", "20:45", "Milan", "Roma", "Serie A", "1"),
        ("17/08/2025", "18:00", "Napoli", "Juventus", "Serie A", "X"),
        ("18/08/2025", "21:00", "Inter", "Lazio", "Serie A", "2")
    ]

# 📋 Formatta la schedina
def formatta_schedina(partite):
    giorni = {
        "17/08/2025": "📅 *Oggi*",
        "18/08/2025": "📅 *Domani*",
        "19/08/2025": "📅 *Dopodomani*"
    }

    sezioni = {g: [] for g in giorni}
    for data, orario, home, away, competizione, esito in partite:
        if data in sezioni:
            sezioni[data].append(f"🕒 {orario} → {home} - {away} ({competizione}) → {esito}")

    messaggio = "📋 *Schedina Test*\n\n"
    for data in giorni:
        if sezioni[data]:
            sezioni[data].sort()
            messaggio += f"{giorni[data]}\n" + "\n".join(sezioni[data]) + "\n\n"

    if len(messaggio) > 4000:
        messaggio = messaggio[:3990] + "\n\n✂️ Messaggio troncato"
    return messaggio

# 📤 Invia su Telegram
async def invia_schedina_telegram(messaggio):
    try:
        bot = Bot(token=TOKEN)
        await bot.send_message(chat_id=CHAT_ID, text=messaggio, parse_mode="Markdown")
        print("[OK] Messaggio Telegram inviato.")
    except Exception as e:
        print(f"[ERRORE] Invio Telegram: {e}")

# 🚀 Main
def main():
    print("🚀 Avvio bot TEST...")
    partite = get_partite_test()
    messaggio = formatta_schedina(partite)
    print("📨 Messaggio da inviare:\n", messaggio)
    asyncio.run(invia_schedina_telegram(messaggio))

if __name__ == "__main__":
    main()
