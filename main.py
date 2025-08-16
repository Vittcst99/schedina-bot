import requests
from bs4 import BeautifulSoup
import random
from datetime import datetime, timedelta
import asyncio
from telegram import Bot

# 🔧 Configura il tuo token Telegram
TOKEN = "7648194737:AAGl1yvBvHUUZB-WbF-3vVCGB-IDYGLUnOs"
CHAT_ID = 810945111  # chat ID come intero, non stringa

# 🏆 Competizioni da Soccerway
COMPETITIONS = {
    "Serie A": "https://int.soccerway.com/national/italy/serie-a/2025-2026/regular-season/r12345/matches/",
    "Premier League": "https://int.soccerway.com/national/england/premier-league/2025-2026/regular-season/r12345/matches/",
    # Aggiungi altre competizioni se vuoi
}

def get_partite_da_soccerway(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    partite = []

    oggi = datetime.now().strftime("%d/%m/%Y")
    domani = (datetime.now() + timedelta(days=1)).strftime("%d/%m/%Y")

    for row in soup.select('.matches .match'):
        teams = row.select('.team')
        time_tag = row.select_one('.scoretime .time')
        date_tag = row.select_one('.scoretime .date')
        
        if len(teams) == 2 and time_tag and date_tag:
            home = teams[0].text.strip()
            away = teams[1].text.strip()
            orario = time_tag.text.strip()
            data = date_tag.text.strip()

            # 🎯 Filtra partite di oggi e domani
            if data in [oggi, domani]:
                partite.append((home, away, orario))
    return partite

def genera_schedina_soccerway():
    tutte_le_partite = []

    for nome, url in COMPETITIONS.items():
        partite = get_partite_da_soccerway(url)
        for match in partite:
            esito = random.choice(["1", "X", "2"])
            home, away, orario = match
            tutte_le_partite.append(f"{orario} → {home} - {away} ({nome}) → {esito}")

    return tutte_le_partite

async def invia_schedina_telegram(partite):
    bot = Bot(token=TOKEN)
    if partite:
        messaggio = "📋 *Schedina per oggi e domani*\n\n" + "\n".join(partite)
    else:
        messaggio = "⚠️ Nessuna schedina disponibile per oggi e domani."

    await bot.send_message(chat_id=CHAT_ID, text=messaggio, parse_mode="Markdown")

if __name__ == "__main__":
    schedina = genera_schedina_soccerway()
    asyncio.run(invia_schedina_telegram(schedina))
