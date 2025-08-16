from flask import Flask
import requests
import os
import random
from bs4 import BeautifulSoup

app = Flask(__name__)

# 🔐 Variabili d'ambiente
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# 🌍 URL Soccerway per ogni competizione
COMPETITIONS = {
    "Serie A": "https://int.soccerway.com/national/italy/serie-a/20252026/schedule/",
    "Serie B": "https://int.soccerway.com/national/italy/serie-b/20252026/schedule/",
    "Coppa Italia": "https://int.soccerway.com/national/italy/coppa-italia/20252026/schedule/",
    "Premier League": "https://int.soccerway.com/national/england/premier-league/20252026/schedule/",
    "Liga": "https://int.soccerway.com/national/spain/primera-division/20252026/schedule/",
    "Bundesliga": "https://int.soccerway.com/national/germany/bundesliga/20252026/schedule/",
    "Ligue 1": "https://int.soccerway.com/national/france/ligue-1/20252026/schedule/"
}

@app.route('/')
def home():
    return "Bot attivo su Render", 200

@app.route('/health')
def health():
    return "OK", 200

# 🧠 Scraping da Soccerway
def get_partite_da_soccerway(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    partite = []
    for row in soup.select('.matches .match'):
        teams = row.select('.team')
        if len(teams) == 2:
            home = teams[0].text.strip()
            away = teams[1].text.strip()
            partite.append((home, away))
    return partite

# 🧾 Genera schedina
def genera_schedina_soccerway():
    tutte_le_partite = []

    for nome, url in COMPETITIONS.items():
        partite = get_partite_da_soccerway(url)
        for match in partite:
            esito = random.choice(["1", "X", "2"])
            tutte_le_partite.append(f"{match[0]} - {match[1]} ({nome}) → {esito}")

    print(f"🔍 Totale partite trovate: {len(tutte_le_partite)}")
    return tutte_le_partite

# 📤 Invio su Telegram
@app.route('/segnali')
def segnali():
    schedina = genera_schedina_soccerway()

    if not schedina:
        messaggio = "⚠️ Nessuna schedina disponibile al momento: non ci sono partite nei campionati selezionati."
    else:
        messaggio = "📈 Nuovo segnale ricevuto!\n\n🧾 *Schedina del giorno:*\n\n" + "\n".join(f"{i+1}. {riga}" for i, riga in enumerate(schedina))

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': messaggio,
        'parse_mode': 'Markdown'
    }
    r = requests.post(url, data=payload)
    return "Segnale + schedina inviata", r.status_code

# 🧪 Rotta di debug per visualizzare la schedina
@app.route('/debug-schedina')
def debug_schedina():
    schedina = genera_schedina_soccerway()
    if not schedina:
        return "⚠️ Nessuna schedina disponibile.", 200
    return "<br>".join(f"{i+1}. {riga}" for i, riga in enumerate(schedina)), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
