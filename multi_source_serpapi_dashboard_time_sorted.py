import re
import os
import json
import datetime
import pytz
import pandas as pd
import requests
import streamlit as st

# Heure locale
def convert_to_local(utc_str):
    utc_dt = datetime.datetime.strptime(utc_str, '%Y-%m-%dT%H:%M:%SZ')
    utc_dt = utc_dt.replace(tzinfo=datetime.timezone.utc)
    local_dt = utc_dt.astimezone(pytz.timezone('America/Toronto'))
    return local_dt.strftime('%Y-%m-%d %H:%M:%S')

# Fonction pour extraire et filtrer les résultats d’une source
def extract_articles(source, query, api_key, limit=10):
    url = f"https://serpapi.com/search.json?q={query}&hl=en&gl=us&source={source}&api_key={api_key}&num={limit}"
    response = requests.get(url)

    if response.status_code != 200:
        return [{"source": source, "title": f"Erreur API ({response.status_code})", "date": "", "content": "", "link": ""}]

    data = response.json()
    articles = []

    if "news_results" in data:
        for result in data["news_results"]:
            title = result.get("title", "")
            snippet = result.get("snippet", "")
            link = result.get("link", "")
            date = result.get("date", "")
            if f"${query.upper()}" in title or f"${query.upper()}" in snippet:
                articles.append({
                    "source": source,
                    "title": title,
                    "date": date,
                    "content": snippet,
                    "link": link
                })
    elif "organic_results" in data:
        for result in data["organic_results"]:
            title = result.get("title", "")
            snippet = result.get("snippet", "")
            link = result.get("link", "")
            date = result.get("date", "")
            if f"${query.upper()}" in title or f"${query.upper()}" in snippet:
                articles.append({
                    "source": source,
                    "title": title,
                    "date": date,
                    "content": snippet,
                    "link": link
                })

    return articles

# Interface Streamlit
st.set_page_config(page_title="🔍 Cashtag Search", layout="wide")
st.title("📊 Multi-Source Cashtag News Scraper")

api_key = st.text_input("🔑 Entrez votre clé SerpAPI :", type="password")
query = st.text_input("🔎 Cashtag (ex. EQT)", value="EQT")

selected_sources = st.multiselect(
    "📰 Sources à interroger",
    ["reddit", "stocktwits", "twitter"],
    default=["reddit", "stocktwits", "twitter"]
)

if st.button("Rechercher") and api_key and query:
    all_results = []
    with st.spinner("Recherche en cours..."):
        for source in selected_sources:
            results = extract_articles(source, query, api_key)
            for article in results:
                if article["date"]:
                    try:
                        article["date"] = convert_to_local(article["date"])
                    except:
                        pass
                all_results.append(article)

    df = pd.DataFrame(all_results)
    if not df.empty:
        df.sort_values(by="date", ascending=False, inplace=True)
        st.dataframe(df[["date", "source", "title", "content", "link"]], use_container_width=True)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Télécharger CSV", csv, "cashtag_results.csv", "text/csv")
    else:
        st.warning("Aucun résultat trouvé.")
