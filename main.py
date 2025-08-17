import os
import requests
from bs4 import BeautifulSoup
import random
from datetime import datetime, timedelta
import asyncio
from telegram import Bot

# 🔐 Leggi variabili ambiente
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID"))

# 🎯 Competizioni da filtrare
COMPETITIONS_DESIDERATE = ["Serie A", "Premier League"]

def get_partite_per_data(data_obj):
    url = f"https://int.soccerway.com/matches/{data_obj.year}/{data_obj.month:02}/{data_obj.day:02}/"
    print(f"🔗 Cerco partite da: {url}")
    partite = []

    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        for row in soup.select('.matches .match'):
            teams = row.select('.team')
            time_tag = row.select_one('.scoretime .time')
            competition_tag = row.select_one('.competition')

            if len(teams) == 2 and time_tag and competition_tag:
                home = teams[0].text.strip()
                away = teams[1].text.strip()
                orario = time_tag.text.strip()
                competizione = competition_tag.text.strip()

                if competizione in COMPETITIONS_DESIDERATE:
                    esito = random.choice(["1", "X", "2"])
                    partite.append((data_obj.strftime("%d/%m/%Y"), orario, home, away, competizione, esito))
    except Exception as e:
        print(f"[ERRORE] Parsing partite: {e}")

    return partite

def formatta_schedina(partite):
    giorni = {
        datetime.now().strftime("%d/%m/%Y"): "📅 *Oggi*",
        (datetime.now() + timedelta(days=1)).strftime("%d/%m/%Y"): "📅 *Domani*",
        (datetime.now() + timedelta(days=2)).strftime("%d/%m/%Y"): "📅 *Dopodomani*"
    }

    sezioni = {g: [] for g in giorni}
    for data, orario, home, away, competizione, esito in partite:
        sezioni[data].append(f"🕒 {orario} → {home} - {away} ({competizione}) → {esito}")

    messaggio = "📋 *Schedina*\n\n"
    for data in giorni:
        if sezioni[data]:
            sezioni[data].sort()
            messaggio += f"{giorni[data]}\n" + "\n".join(sezioni[data]) + "\n\n"

    if len(messaggio) > 4000:
        messaggio = messaggio[:3990] + "\n\n✂️ Messaggio troncato"
    return messaggio

async def invia_schedina_telegram(messaggio):
    try:
        bot = Bot(token=TOKEN)
        await bot.send_message(chat_id=CHAT_ID, text=messaggio, parse_mode="Markdown")
        print("[OK] Messaggio Telegram inviato.")
    except Exception as e:
        print(f"[ERRORE] Invio Telegram: {e}")

def main():
    print("🚀 Avvio bot...")
    oggi = datetime.now().date()
    domani = oggi + timedelta(days=1)
    dopodomani = oggi + timedelta(days=2)

    tutte_le_partite = []
    for giorno in [oggi, domani, dopodomani]:
        partite = get_partite_per_data(giorno)
        print(f"📊 Partite trovate per {giorno}: {len(partite)}")
        tutte_le_partite.extend(partite)

    if tutte_le_partite:
        messaggio = formatta_schedina(tutte_le_partite)
    else:
        messaggio = "⚠️ Nessuna partita trovata per oggi, domani o dopodomani."

    print("📨 Messaggio:\n", messaggio)
    asyncio.run(invia_schedina_telegram(messaggio))

if __name__ == "__main__":
    main()
