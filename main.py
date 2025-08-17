import os
import requests
from datetime import datetime, timedelta
import random
import asyncio
from telegram import Bot

# 🔐 Variabili ambiente
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID"))

# 📅 Date da controllare
def get_date_list():
    today = datetime.now().date()
    return [today, today + timedelta(days=1), today + timedelta(days=2)]

# 🔍 Estrai partite dalla API JSON della Lega Serie A
def get_partite_lega_json():
    url = "https://www.legaseriea.it/api/season-calendar?season_id=2025"
    print(f"🔗 Chiamata API: {url}")
    partite = []

    try:
        res = requests.get(url)
        data = res.json()
        date_list = get_date_list()

        for match in data.get("matches", []):
            date_str = match.get("date")
            home = match.get("home_team", {}).get("name", "").strip()
            away = match.get("away_team", {}).get("name", "").strip()
            time_str = match.get("hour", "00:00").strip()

            if not date_str or not home or not away:
                continue

            match_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            if match_date in date_list:
                esito = random.choice(["1", "X", "2"])
                partite.append((match_date.strftime("%d/%m/%Y"), time_str, home, away, "Serie A", esito))
    except Exception as e:
        print(f"[ERRORE] Parsing JSON Lega Serie A: {e}")

    return partite

# 📋 Formatta la schedina
def formatta_schedina(partite):
    giorni = {
        datetime.now().strftime("%d/%m/%Y"): "📅 *Oggi*",
        (datetime.now() + timedelta(days=1)).strftime("%d/%m/%Y"): "📅 *Domani*",
        (datetime.now() + timedelta(days=2)).strftime("%d/%m/%Y"): "📅 *Dopodomani*"
    }

    sezioni = {g: [] for g in giorni}
    for data, orario, home, away, competizione, esito in partite:
        sezioni[data].append(f"🕒 {orario} → {home} - {away} ({competizione}) → {esito}")

    messaggio = "📋 *Schedina Serie A*\n\n"
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
    print("🚀 Avvio bot Serie A JSON...")
    partite = get_partite_lega_json()

    if partite:
        messaggio = formatta_schedina(partite)
    else:
        messaggio = "⚠️ Nessuna partita trovata per oggi, domani o dopodomani."

    print("📨 Messaggio:\n", messaggio)
    asyncio.run(invia_schedina_telegram(messaggio))

if __name__ == "__main__":
    main()
