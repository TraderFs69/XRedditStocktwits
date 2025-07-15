import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from datetime import timedelta
import pytz
import re

st.set_page_config(page_title="Multi‑Sources SerpAPI – Cashtag exact", layout="wide")
st.title("🔍 Recherche Twitter / Reddit / Stocktwits (cashtag exact)")

# --- fonctions utilitaires --------------------------------------------------
local_tz = pytz.timezone("America/Toronto")

def to_local(dt_str):
    try:
        utc_dt = datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=pytz.utc)
        return utc_dt.astimezone(local_tz)
    except ValueError:
        return datetime.now(tz=local_tz)

def make_regex(ticker):
    # supprime le $ éventuel et rend le tout insensible à la casse
    core = re.escape(ticker.lstrip("$").upper())
    return re.compile(rf"\b\$?{core}\b", re.IGNORECASE)

# --- interface utilisateur ---------------------------------------------------
api_key = st.text_input("🔑 Clé SerpAPI", type="password")
query_input = st.text_input("🔎 Mot‑clé / Cashtag (ex: $EQT)", value="$EQT")
num = st.slider("🔢 Nb résultats par plateforme", 5, 50, 10)
platforms = st.multiselect("🌐 Plateformes", ["Twitter", "Reddit", "Stocktwits"], default=["Twitter","Reddit","Stocktwits"])

if api_key and query_input and platforms:
    cashtag_pattern = make_regex(query_input)
    all_rows = []

    def search_site(site, label):
        params = {
            "engine":"google",
            "q": f"site:{site} {query_input}",
            "api_key": api_key,
            "num": num
        }
        r = requests.get("https://serpapi.com/search", params=params)
        if r.status_code==200:
            for res in r.json().get("organic_results", []):
                text_blob = (res.get("title","") or "") + " " + (res.get("snippet","") or "")
                if cashtag_pattern.search(text_blob):
                    all_rows.append({
                        "Plateforme": label,
                        "Titre": res.get("title",""),
                        "Lien": res.get("link",""),
                        "Aperçu": res.get("snippet",""),
                        "Date": to_local(res.get("date","")) if res.get("date") else ""
                    })
        else:
            st.error(f"Erreur SerpAPI {label}: {r.status_code}")

    if "Twitter" in platforms:
        search_site("twitter.com", "X")
    if "Reddit" in platforms:
        search_site("reddit.com", "Reddit")
    if "Stocktwits" in platforms:
        search_site("stocktwits.com", "Stocktwits")

    if all_rows:
        df = pd.DataFrame(all_rows).sort_values("Date", ascending=False)
        st.dataframe(df, use_container_width=True)
        st.download_button("📥 CSV", df.to_csv(index=False).encode("utf-8"), "results.csv","text/csv")
    else:
        st.warning("Aucun résultat correspondant au cashtag exact.")
else:
    st.info("Entrez la clé SerpAPI et le cashtag pour commencer.")

