from flask import Flask
import requests  # aggiunto per inviare messaggi Telegram

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot attivo su Railway", 200

@app.route('/health')
def health():
    return "OK", 200

# 🔔 Nuova rotta /segnali per invio Telegram
TELEGRAM_TOKEN = '7648194737:AAGl1yvBvHUUZB-WbF-3vVCGB-IDYGLUnOs'
TELEGRAM_CHAT_ID = '810945111'

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
