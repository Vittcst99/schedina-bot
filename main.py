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
    return partite

# 🧠 Funzione per ottenere partite di Coppa Italia di oggi e domani
def get_partite_coppa_italia_oggi():
    oggi = datetime.utcnow().strftime("%Y-%m-%d")
    domani = (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d")
    url = f"https://v3.football.api-sports.io/fixtures?league=137&from={oggi}&to={domani}"
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
        "Serie B": 136
    }

    tutte_le_partite = []

    for nome, league_id in LEAGUES.items():
        partite = get_partite_da_campionato(league_id)
        for match in partite:
            esito = random.choice(["1", "X", "2"])
            tutte_le_partite.append(f"{match[0]} - {match[1]} ({nome}) → {esito}")

    # Aggiungi partite di Coppa Italia
    coppa_partite = get_partite_coppa_italia_oggi()
    for match in coppa_partite:
        esito = random.choice(["1", "X", "2"])
        tutte_le_partite.append(f"{match[0]} - {match[1]} (Coppa Italia) → {esito}")

    # Se ci sono almeno 13 partite, scegli 13 casuali
    if len(tutte_le_partite) >= 13:
        return random.sample(tutte_le_partite, 13)
    else:
        return []

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
