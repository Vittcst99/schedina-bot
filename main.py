from flask import Flask
import requests
import os  # 🔐 Per leggere le variabili d'ambiente

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot attivo su Render", 200

@app.route('/health')
def health():
    return "OK", 200

# 🔔 Rotta /segnali per invio Telegram
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

@app.route('/segnali')
def segnali():
    messaggio = "📈 Nuovo segnale: controlla subito la schedina!"
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': messaggio
    }
    r = requests.post(url, data=payload)
    return "Segnale inviato", r.status_code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
