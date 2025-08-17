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

# 🏆 Competizioni da Soccerway
COMPETITIONS = {
    "Serie A": "https://int.soccerway.com/national/italy/serie-a/2025-2026/regular-season/",
    "Premier League": "https://int.soccerway.com/national/england/premier-league/2025-2026/regular-season/",
}

def trova_link_giornata(base_url):
    try:
        response = requests.get(base_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        for link in soup.select('.rounds .round a'):
            href = link.get('href')
            if href and '/matches/' in href:
                return "https://int.soccerway.com" + href
    except Exception as e:
        print(f"[ERRORE] Link giornata: {e}")
    return None

def get_partite_da_soccerway(url, nome_competizione):
    partite = []
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        oggi = datetime.now().strftime("%d/%m/%Y")
        domani = (datetime.now() + timedelta(days=1)).strftime("%d/%m/%Y")
        dopodomani = (datetime.now() + timedelta(days=2)).strftime("%d/%m/%Y")
        giorni_validi = [oggi, domani, dopodomani]

        for row in soup.select('.matches .match'):
            teams = row.select('.team')
            time_tag = row.select_one('.scoretime .time')
            date_tag = row.select_one('.scoretime .date')

            if len(teams) == 2 and time_tag and date_tag:
                home = teams[0].text.strip()
                away = teams[1].text.strip()
                orario = time_tag.text.strip()
                data = date_tag.text.strip()

                if data in giorni_validi:
                    esito = random.choice(["1", "X", "2"])
                    partite.append((data, orario, home, away, nome_competizione, esito))
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
    tutte_le_partite = []
    for nome, base_url in COMPETITIONS.items():
        print(f"🔍 Cerco partite per {nome}")
        url = trova_link_giornata(base_url)
        print(f"🌐 Link giornata: {url}")
        if url:
            partite = get_partite_da_soccerway(url, nome)
            print(f"📊 Partite trovate: {len(partite)}")
            tutte_le_partite.extend(partite)

    if tutte_le_partite:
        messaggio = formatta_schedina(tutte_le_partite)
    else:
        messaggio = "⚠️ Nessuna partita trovata per oggi, domani o dopodomani."

    print("📨 Messaggio:\n", messaggio)
    asyncio.run(invia_schedina_telegram(messaggio))

if __name__ == "__main__":
    main()
