import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

COMPETITIONS = {
    "Serie A": "https://int.soccerway.com/national/italy/serie-a/2025-2026/regular-season/",
    "Premier League": "https://int.soccerway.com/national/england/premier-league/2025-2026/regular-season/",
}

def trova_link_giornata(base_url):
    print(f"\n🔍 Cerco giornata per: {base_url}")
    try:
        response = requests.get(base_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        for link in soup.select('.rounds .round a'):
            href = link.get('href')
            if href and '/matches/' in href:
                full_link = "https://int.soccerway.com" + href
                print(f"✅ Link giornata trovato: {full_link}")
                return full_link
        print("⚠️ Nessun link giornata trovato.")
    except Exception as e:
        print(f"[ERRORE] durante il parsing della giornata: {e}")
    return None

def get_partite_da_soccerway(url, nome_competizione):
    print(f"\n📥 Parsing partite da: {url}")
    partite = []
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        print("📄 Anteprima HTML ricevuto:")
        print(soup.prettify()[:1000])  # Mostra i primi 1000 caratteri

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

                print(f"📆 Partita trovata: {data} {orario} → {home} vs {away}")

                if data in giorni_validi:
                    partite.append((data, orario, home, away, nome_competizione))
        print(f"✅ Partite valide trovate: {len(partite)}")
    except Exception as e:
        print(f"[ERRORE] durante il parsing delle partite: {e}")
    return partite

def main():
    print("🚀 Avvio debug bot...\n")
    tutte_le_partite = []
    for nome, base_url in COMPETITIONS.items():
        url = trova_link_giornata(base_url)
        if url:
            partite = get_partite_da_soccerway(url, nome)
            tutte_le_partite.extend(partite)

    if tutte_le_partite:
        print("\n📋 Partite totali trovate:")
        for p in tutte_le_partite:
            print(f"🕒 {p[1]} → {p[2]} - {p[3]} ({p[4]})")
    else:
        print("\n⚠️ Nessuna partita trovata per oggi, domani o dopodomani.")

if __name__ == "__main__":
    main()
