from flask import Flask
import requests
import os
import random
from datetime import datetime, timedelta

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
def get_partite_da_campionato(league_id):
    url = f"https://v3.football.api-sports.io/fixtures?league={league_id}&next=10"
    headers = {"x-apisports-key": API_FOOTBALL_KEY}
    response = requests.get(url, headers=headers)
    data = response.json()

    partite = []
    for match in data.get("response", []):
        home = match["teams"]["home"]["name"]
        away = match["teams"]["away"]["name"]
        partite.append((home, away))
    print(f"📊 {league_id} → {len(partite)} partite trovate")
    return partite

# 🧠 Funzione per ottenere partite di Coppa Italia di oggi e domani
def get_partite_coppa_italia_oggi():
   url = "https://v3.football.api-sports.io/fixtures?league=137&next=10"
    headers = {"x-apisports-key": API_FOOTBALL_KEY}
    response = requests.get(url, headers=headers)
    data = response.json()

    partite = []
    for match in data.get("response", []):
        home = match["teams"]["home"]["name"]
        away = match["teams"]["away"]["name"]
        partite.append((home, away))
    print(f"🎯 Coppa Italia (next=10) → {len(partite)} partite trovate")
    return partite

# 🧾 Funzione per generare la schedina
def genera_schedina():
    LEAGUES = {
        "Serie A": 135,
        "Premier League": 39,
        "Liga": 140,
        "Bundesliga": 78,
        "Ligue 1": 61,
        "Serie B": 136
    }

    tutte_le_partite = []

    for nome, league_id in LEAGUES.items():
        partite = get_partite_da_campionato(league_id)
        for match in partite:
            esito = random.choice(["1", "X", "2"])
            tutte_le_partite.append(f"{match[0]} - {match[1]} ({nome}) → {esito}")

    coppa_partite = get_partite_coppa_italia_oggi()
    for match in coppa_partite:
        esito = random.choice(["1", "X", "2"])
        tutte_le_partite.append(f"{match[0]} - {match[1]} (Coppa Italia) → {esito}")

    print(f"🔍 Totale partite disponibili: {len(tutte_le_partite)}")
    return tutte_le_partite

# 📤 Rotta /segnali che ora invia anche la schedina
@app.route('/segnali')
def segnali():
    schedina = genera_schedina()

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

# 🧪 Rotta di debug per Coppa Italia
@app.route('/debug-coppa')
def debug_coppa():
    oggi = datetime.utcnow().strftime("%Y-%m-%d")
    domani = (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d")
    url = f"https://v3.football.api-sports.io/fixtures?league=137&from={oggi}&to={domani}"
    headers = {"x-apisports-key": API_FOOTBALL_KEY}
    response = requests.get(url, headers=headers)
    data = response.json()

    if not data.get("response"):
        return f"Nessuna partita trovata per Coppa Italia tra {oggi} e {domani}", 200

    partite = []
    for match in data["response"]:
        home = match["teams"]["home"]["name"]
        away = match["teams"]["away"]["name"]
        partite.append(f"{home} - {away}")

    return "<br>".join(partite), 200

# 🧪 Rotta di debug JSON grezzo
@app.route('/debug-json')
def debug_json():
    oggi = datetime.utcnow().strftime("%Y-%m-%d")
    domani = (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d")
    url = f"https://v3.football.api-sports.io/fixtures?league=137&from={oggi}&to={domani}"
    headers = {"x-apisports-key": API_FOOTBALL_KEY}
    response = requests.get(url, headers=headers)
    return response.text, 200

# 🧪 Rotta per visualizzare la schedina nel browser
@app.route('/debug-schedina')
def debug_schedina():
    schedina = genera_schedina()
    if not schedina:
        return "⚠️ Nessuna schedina disponibile.", 200
    return "<br>".join(f"{i+1}. {riga}" for i, riga in enumerate(schedina)), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
