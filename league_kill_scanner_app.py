import streamlit as st
import requests
import urllib.parse
import time
import json
from datetime import datetime

# Riot API setup
REGION = 'europe'
PLATFORM = 'euw1'

# Load PUUID cache
PUUID_CACHE_FILE = "puuid_cache.json"

def load_puuid_cache():
    try:
        with open(PUUID_CACHE_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_puuid_cache(cache):
    with open(PUUID_CACHE_FILE, "w") as f:
        json.dump(cache, f)

def get_puuid(riot_id, api_key):
    if '#' not in riot_id:
        return None

    cache = load_puuid_cache()
    if riot_id in cache:
        return cache[riot_id]

    game_name, tag_line = riot_id.split('#')
    url = f"https://{REGION}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{urllib.parse.quote(game_name)}/{urllib.parse.quote(tag_line)}"
    headers = {"X-Riot-Token": api_key}

    for attempt in range(2):
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            puuid = response.json().get("puuid")
            cache[riot_id] = puuid
            save_puuid_cache(cache)
            return puuid
        elif response.status_code == 404:
            return None
        else:
            time.sleep(0.5)

    return "API_ERROR"

# Streamlit UI
st.title("💠 League Kill Scanner (Web Edition)")

api_key = st.text_input("🔑 Riot API Key", type="password")
riot_ids_input = st.text_area("🧾 Riot IDs (one per line)")
min_kills = st.number_input("Minimum Kills", min_value=1, value=3)
time_limit = st.number_input("Time Window (minutes)", min_value=1, value=3)
after_date = st.date_input("Only Matches After", value=datetime(2024, 1, 1))

if st.button("🚀 Start Scan"):
    if not api_key or not riot_ids_input:
        st.warning("Please enter your API key and at least one Riot ID.")
    else:
        riot_ids = riot_ids_input.strip().splitlines()
        st.write(f"Scanning {len(riot_ids)} Riot IDs...")
        for idx, riot_id in enumerate(riot_ids, start=1):
            puuid = get_puuid(riot_id, api_key)
            if puuid == "API_ERROR":
                st.error(f"[{idx}] {riot_id} — ⚠️ API error or cooldown.")
            elif not puuid:
                st.warning(f"[{idx}] {riot_id} — ❌ Riot ID not found.")
            else:
                st.success(f"[{idx}] {riot_id} — ✅ PUUID: {puuid}")
