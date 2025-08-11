from flask import Flask
import requests
import os
import random

app = Flask(__name__)

# 🔐 Variabili d'ambiente
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
API_FOOTBALL_KEY = os.getenv('API_FOOTBALL_KEY')

@app.route('/')
def home():
    return "Bot attivo su Render", 200

@app.route('/health')
def health():
    return "OK", 200

# 🧠 Funzione per ottenere partite da un campionato
def get_partite_da_campionato(league_id, season="2025"):
    url = f"https://v3.football.api-sports.io/fixtures?league={league_id}&season={season}&next=10"
    headers = {"x-apisports-key": API_FOOTBALL_KEY}
    response = requests.get(url, headers=headers)
    data = response.json()

    partite = []
    for match in data.get("response", []):
        home = match["teams"]["home"]["name"]
        away = match["teams"]["away"]["name"]
        partite.append((home, away))
    return partite

# 🧾 Funzione per generare la schedina
def genera_schedina():
    LEAGUES = {
        "Serie A": 135,
        "Premier League": 39,
        "Liga": 140,
        "Bundesliga": 78,
        "Ligue 1": 61,
        "Serie B": 136,
        "Coppa Italia": 137
    }

    schedina = []
    campionati = list(LEAGUES.items())
    random.shuffle(campionati)

    tentativi = 0
    max_tentativi = 30

    while len(schedina) < 13 and tentativi < max_tentativi:
        nome, league_id = random.choice(campionati)
        partite = get_partite_da_campionato(league_id)
        if partite:
            match = random.choice(partite)
            esito = random.choice(["1", "X", "2"])
            schedina.append(f"{match[0]} - {match[1]} ({nome}) → {esito}")
        tentativi += 1

    return schedina

# 📤 Rotta /segnali che ora invia anche la schedina
@app.route('/segnali')
def segnali():
    schedina = genera_schedina()

    if len(schedina) < 13:
        messaggio = "⚠️ Nessuna schedina disponibile al momento: non ci sono abbastanza partite nei campionati selezionati. Riprova più tardi!"
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
