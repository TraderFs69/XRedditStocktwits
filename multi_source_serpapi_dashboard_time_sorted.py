import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import pytz

st.set_page_config(page_title="Filtrage multi-sources (X, Reddit, Stocktwits)", layout="wide")
st.title("📰 Dashboard de nouvelles boursières (X, Reddit, Stocktwits)")

def convert_to_local_time(utc_string):
    utc_time = datetime.strptime(utc_string, "%Y-%m-%dT%H:%M:%SZ")
    local_tz = pytz.timezone("America/Toronto")
    return utc_time.replace(tzinfo=pytz.utc).astimezone(local_tz)

query = st.text_input("🔍 Entrez un mot-clé ou un ticker (ex: Apple ou $AAPL)")

if query:
    all_data = []

    # SerpAPI KEY (assumée définie via environnement ou st.secrets)
    SERPAPI_KEY = st.secrets["SERPAPI_KEY"] if "SERPAPI_KEY" in st.secrets else "YOUR_API_KEY"

    def fetch_serpapi_data(source):
        url = f"https://serpapi.com/search.json?engine={source}&q={query}&api_key={SERPAPI_KEY}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        return None

    # X (Twitter)
    tw_data = fetch_serpapi_data("twitter")
    if tw_data and "tweets" in tw_data:
        for tweet in tw_data["tweets"]:
            all_data.append({
                "Plateforme": "X",
                "Auteur": tweet.get("username", ""),
                "Contenu": tweet.get("text", ""),
                "Date": convert_to_local_time(tweet.get("date", "")) if tweet.get("date") else "",
                "Lien": tweet.get("link", "")
            })

    # Reddit
    reddit_data = fetch_serpapi_data("reddit")
    if reddit_data and "posts" in reddit_data:
        for post in reddit_data["posts"]:
            all_data.append({
                "Plateforme": "Reddit",
                "Auteur": post.get("author", ""),
                "Contenu": post.get("title", "") + " " + post.get("text", ""),
                "Date": convert_to_local_time(post.get("date", "")) if post.get("date") else "",
                "Lien": post.get("link", "")
            })

    # Stocktwits
    stw_data = fetch_serpapi_data("stocktwits")
    if stw_data and "messages" in stw_data:
        for msg in stw_data["messages"]:
            all_data.append({
                "Plateforme": "Stocktwits",
                "Auteur": msg.get("author", {}).get("username", ""),
                "Contenu": msg.get("body", ""),
                "Date": convert_to_local_time(msg.get("created_at", "")) if msg.get("created_at") else "",
                "Lien": msg.get("link", "")
            })

    if all_data:
        df = pd.DataFrame(all_data)
        df = df.sort_values(by="Date", ascending=False)
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("Aucun résultat trouvé pour ce mot-clé.")
