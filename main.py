from dotenv import load_dotenv
import os
import streamlit as st
import pandas as pd
import numpy as np
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv()
# Spotify authentication
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

if not CLIENT_ID or not CLIENT_SECRET:
    st.error("Spotify API credentials not found. Please set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in a .env file.")
    st.stop()

auth_manager = SpotifyClientCredentials(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
)
sp = spotipy.Spotify(auth_manager=auth_manager)


# Streamlit page setup
st.set_page_config(page_title="Music Genre Explorer", layout="wide")
st.title("Spotify Music Genre Explorer")
st.subheader("Discover tracks, artists, and audio features by genre.")

# Sidebar controls
username = st.sidebar.text_input("Your Name (optional)")
view_mode = st.sidebar.radio("Choose view mode:", ["Columns View", "Table View"])
genres = ["rock", "pop", "jazz", "classical", "hip-hop", "edm", "country", "metal", "indie", "r&b"]
genre = st.sidebar.selectbox("Choose a genre:", genres)
limit = st.sidebar.slider("Number of tracks:", 5, 50, 15)
show_map = st.sidebar.checkbox("Show Random Artist Map (Demo)")
show_artist_chart = st.sidebar.checkbox("Show Artist Popularity Chart")

if username:
    st.info(f"Welcome, {username}! Exploring the genre: {genre}")

# Fetch tracks function
def get_tracks_by_genre(genre, limit):
    results = sp.search(q=f"genre:{genre}", type="track", limit=limit)
    return results["tracks"]["items"]

# Main button
if st.button("Explore Genre"):
    st.info("Fetching data from Spotify...")
    try:
        tracks = get_tracks_by_genre(genre, limit)

        if not tracks:
            st.warning("No tracks found for this genre.")
        else:
            st.success(f"Showing top {len(tracks)} tracks for: {genre}")

            # Prepare DataFrame
            df = pd.DataFrame([{
                "Track": t["name"],
                "Artist": t["artists"][0]["name"],
                "Album": t["album"]["name"],
                "Popularity": t["popularity"],
                "Duration": f"{t['duration_ms']//60000}:{(t['duration_ms']//1000)%60:02d}",
                "Spotify Link": t["external_urls"]["spotify"],
                "Album Art": t["album"]["images"][0]["url"] if t["album"]["images"] else None
            } for t in tracks])

            # Display tracks in columns
            if view_mode == "Columns View":
                st.subheader("Track Details with Album Art & Previews")
                for t in tracks:
                    cols = st.columns([1, 3, 2, 1, 1])
                    # Album art
                    with cols[0]:
                        if t["album"]["images"]:
                            st.image(t["album"]["images"][0]["url"], width=60)
                        else:
                            st.write("No image")
                    # Track info.
                    with cols[1]:
                        st.markdown(
                            f"**Track:** {t['name']}  \n"
                            f"**Artist:** {t['artists'][0]['name']}  \n"
                            f"**Album:** {t['album']['name']}"
                        )
                    # Popularity
                    with cols[2]:
                        st.write(f"Popularity: {t['popularity']}")
                    # Duration
                    with cols[3]:
                        mins = t['duration_ms']//60000
                        secs = (t['duration_ms']//1000)%60
                        st.write(f"Duration: {mins}:{secs:02d}")
                    # Spotify link
                    with cols[4]:
                        if t["preview_url"]:
                            st.audio(t["preview_url"], format="audio/mp3")
                        st.markdown(f"[Listen on Spotify]({t['external_urls']['spotify']})")
                    st.markdown("---")

            # Display tracks in table
            elif view_mode == "Table View":
                st.subheader("Track Table")
                df_display = df.copy()
                df_display["Spotify Link"] = df_display["Spotify Link"].apply(lambda x: f"[Listen]({x})")
                st.dataframe(df_display[["Track", "Artist", "Album", "Popularity", "Duration", "Spotify Link"]])

            # Artist popularity chart
            if show_artist_chart:
                st.subheader("Artist Popularity Chart")

                try:
                    artist_names = []
                    artist_popularity = []

                    for t in tracks:
                        artist_id = t["artists"][0]["id"]
                        artist_data = sp.artist(artist_id)

                        artist_names.append(t["artists"][0]["name"])
                        artist_popularity.append(artist_data.get("popularity", 0))

                    artist_df = pd.DataFrame({
                        "Artist": artist_names,
                        "Popularity": artist_popularity
                    })

                    st.bar_chart(artist_df.set_index("Artist"))

                except Exception as e:
                    st.warning("Unable to retrieve artist popularity data.")
                    st.exception(e)

            # Random artist map
            if show_map:
                st.subheader("Artist Location Map (Demo)")
                map_df = pd.DataFrame({
                    "lat": np.random.uniform(-50, 50, 10),
                    "lon": np.random.uniform(-100, 100, 10)
                })
                st.map(map_df)

    except Exception as e:
        st.error("Error fetching data from Spotify.")
        st.exception(e)

# About
with st.expander("About This App"):
    st.write("""
        This Music Genre Explorer uses the **Spotify API** to retrieve real-time music data, including:
        - Track names
        - Album art
        - Audio previews
        - Popularity

        Features:
        - Columns or Table view with clickable Spotify links
        - Bar chart of artist popularity
        - Random artist map demo
        - Interactive widgets: radio button, selectbox, slider, checkbox, text input
    """)
