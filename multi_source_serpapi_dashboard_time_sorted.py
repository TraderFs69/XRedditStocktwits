
import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="🔍 Multi-Recherche avec Dates", layout="centered")
st.title("🔍 Recherche SerpAPI : Twitter, Reddit, Stocktwits (triés + heure)")

# Entrée API
api_key = st.text_input("🔑 Entrez votre clé SerpAPI (gratuite)", type="password")

# Mot-clé
query = st.text_input("🔍 Entrez un mot-clé ou symbole (ex: $AAPL, Apple)", value="$AAPL")

# Date de début et fin
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("📅 Date de début", value=datetime.today() - timedelta(days=1))
with col2:
    end_date = st.date_input("📅 Date de fin", value=datetime.today())

# Nombre de résultats
num_results = st.slider("🔢 Nombre de résultats à afficher (par plateforme)", min_value=5, max_value=50, value=10)

# Plateformes
platforms = st.multiselect("🌐 Plateformes à inclure", ["Twitter", "Reddit", "Stocktwits"], default=["Twitter", "Reddit", "Stocktwits"])

def build_search_url(site, keyword, start_date, end_date):
    return f"site:{site} {keyword} after:{start_date} before:{end_date + timedelta(days=1)}"

if api_key and query and platforms:
    all_results = []
    for platform in platforms:
        if platform == "Twitter":
            site = "twitter.com"
        elif platform == "Reddit":
            site = "reddit.com"
        elif platform == "Stocktwits":
            site = "stocktwits.com"
        else:
            continue

        st.subheader(f"🔍 Résultats pour {platform}")
        with st.spinner(f"Recherche sur {platform}..."):
            params = {
                "engine": "google",
                "q": build_search_url(site, query, start_date, end_date),
                "api_key": api_key,
                "num": num_results,
            }
            response = requests.get("https://serpapi.com/search", params=params)
            if response.status_code == 200:
                results = response.json().get("organic_results", [])
                for r in results:
                    date_str = r.get("date", "")
                    try:
                        parsed_date = datetime.strptime(date_str, '%b %d, %Y')
                    except:
                        parsed_date = datetime.utcnow()

                    all_results.append({
                        "Plateforme": platform,
                        "Titre": r.get("title", ""),
                        "Lien": r.get("link", ""),
                        "Aperçu": r.get("snippet", ""),
                        "Date": parsed_date,
                        "Source": site
                    })
            else:
                st.error(f"Erreur API {platform} : {response.status_code} - {response.text}")

    if all_results:
        df = pd.DataFrame(all_results)
        df.sort_values(by="Date", ascending=False, inplace=True)

        for index, row in df.iterrows():
            st.markdown(f"""
            ---
            🌍 **{row['Plateforme']}**  
            🕒 **{row['Date'].strftime('%Y-%m-%d %H:%M:%S')}**  
            🔗 **[{row['Titre']}]({row['Lien']})**  
            💬 _{row['Aperçu']}_  
            """)

        st.download_button("📥 Télécharger tout en CSV", df.to_csv(index=False).encode("utf-8"), "multi_source_results.csv", "text/csv")
else:
    if not api_key:
        st.info("🔐 Entrez votre clé SerpAPI pour démarrer.")
    elif not platforms:
        st.warning("❗ Sélectionnez au moins une plateforme à interroger.")
