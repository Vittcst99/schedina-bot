import os
import requests
from bs4 import BeautifulSoup
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

# 🔍 Estrai partite dal sito Lega Serie A
def get_partite_lega():
    url = "https://www.legaseriea.it/it/serie-a/calendario"
    print(f"🔗 Cerco partite da: {url}")
    partite = []

    try:
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        match_blocks = soup.select(".match")

        date_list = get_date_list()
        date_strs = [d.strftime("%d/%m/%Y") for d in date_list]

        for block in match_blocks:
            date_tag = block.select_one(".match-date")
            time_tag = block.select_one(".match-time")
            home_tag = block.select_one(".team-home")
            away_tag = block.select_one(".team-away")

            if date_tag and time_tag and home_tag and away_tag:
                data = date_tag.text.strip()
                orario = time_tag.text.strip()
                home = home_tag.text.strip()
                away = away_tag.text.strip()

                if data in date_strs:
                    esito = random.choice(["1", "X", "2"])
                    partite.append((data, orario, home, away, "Serie A", esito))
    except Exception as e:
        print(f"[ERRORE] Parsing Lega Serie A: {e}")

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
    print("🚀 Avvio bot Serie A...")
    partite = get_partite_lega()

    if partite:
        messaggio = formatta_schedina(partite)
    else:
        messaggio = "⚠️ Nessuna partita trovata per oggi, domani o dopodomani."

    print("📨 Messaggio:\n", messaggio)
    asyncio.run(invia_schedina_telegram(messaggio))

if __name__ == "__main__":
    main()
