import requests
from datetime import datetime

# 🔐 Chiavi e ID
API_KEY = "123"  # tua API key da TheSportsDB
SERIE_A_ID = "4335"  # ID della Serie A
TELEGRAM_TOKEN = "INSERISCI_IL_TUO_TOKEN"
TELEGRAM_CHAT_ID = "INSERISCI_IL_TUO_CHAT_ID"

def get_partite_serie_a():
    url = f"https://www.thesportsdb.com/api/v1/json/{API_KEY}/eventsnextleague.php?id={SERIE_A_ID}"
    response = requests.get(url)
    if response.status_code != 200:
        print("[ERRORE] API non raggiungibile")
        return []

    data = response.json()
    partite = []

    for evento in data.get("events", []):
        squadra1 = evento["strHomeTeam"]
        squadra2 = evento["strAwayTeam"]
        data_match = evento["dateEvent"]
        ora_match = evento["strTime"]
        giorno = datetime.strptime(data_match, "%Y-%m-%d").strftime("%d/%m")
        pronostico = genera_pronostico()
        partite.append(f"🕒 {giorno} {ora_match} → {squadra1} - {squadra2} → {pronostico}")

    return partite

def genera_pronostico():
    # Pronostico casuale per ora (puoi migliorarlo con logica reale)
    import random
    return random.choice(["1", "X", "2"])

def invia_su_telegram(messaggio):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": messaggio,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print("[OK] Messaggio Telegram inviato.")
    else:
        print("[ERRORE] Invio fallito:", response.text)

def main():
    print("🚀 Avvio bot Serie A reale...")
    partite = get_partite_serie_a()

    if not partite:
        messaggio = "⚠️ Nessuna partita trovata per i prossimi giorni."
    else:
        messaggio = "📋 *Schedina Serie A*\n\n" + "\n".join(partite)

    invia_su_telegram(messaggio)

if __name__ == "__main__":
    main()
