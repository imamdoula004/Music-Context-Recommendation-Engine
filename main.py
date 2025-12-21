import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
import datetime
import io
import requests
import sounddevice as sd
from scipy.io.wavfile import write
import tempfile
import speech_recognition as sr
from textblob import TextBlob

# ---------------- FEATURE CONFIG ----------------
FEATURE_COLS = ["energy", "tempo", "valence", "danceability", "acousticness"]

# ---------------- WEATHER CONFIG ----------------
OPENWEATHER_API_KEY = "YOUR_API_KEY_HERE"  # <-- Replace with your OpenWeatherMap API key
CITY_NAME = "Dhaka"  # Change to your city
MAX_TRACK_AGE = 10  # Only recommend tracks from the last 10 years

# ---------------- UTILS ----------------
def get_time_context():
    hour = datetime.datetime.now().hour
    if hour < 6:
        return "Night"
    elif hour < 12:
        return "Morning"
    elif hour < 18:
        return "Afternoon"
    else:
        return "Evening"

def album_art_placeholder(artist, album):
    seed = f"{artist}-{album}".replace(" ", "_")
    return f"https://picsum.photos/seed/{seed}/150/150"

def get_weather_mood():
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY_NAME}&appid={OPENWEATHER_API_KEY}"
        response = requests.get(url).json()
        weather = response["weather"][0]["main"].lower()
        if "sun" in weather or "clear" in weather:
            return "Energetic"
        elif "rain" in weather or "drizzle" in weather:
            return "Calm"
        else:
            return "Neutral"
    except:
        return "Neutral"

# ---------------- VOICE RECORDING & ANALYSIS ----------------
def record_voice(duration=10, fs=44100):
    messagebox.showinfo("Voice Input", f"Recording for {duration} seconds. Speak now!")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    write(tmpfile.name, fs, recording)
    return tmpfile.name

def analyze_voice_mood(wav_path):
    r = sr.Recognizer()
    with sr.AudioFile(wav_path) as source:
        audio = r.record(source)
    try:
        text = r.recognize_google(audio)
        sentiment = TextBlob(text).sentiment.polarity
        if sentiment > 0.2:
            return "Energetic"
        elif sentiment < -0.2:
            return "Calm"
        else:
            return "Neutral"
    except:
        return "Neutral"

# ---------------- RECOMMENDATION ENGINE ----------------
def recommend(file_path, mood="Neutral"):
    try:
        df = pd.read_csv(file_path)

        # Handle column name variations
        if "artists" not in df.columns and "artist_name" in df.columns:
            df.rename(columns={"artist_name": "artists"}, inplace=True)
        if "track_name" not in df.columns and "name" in df.columns:
            df.rename(columns={"name": "track_name"}, inplace=True)
        if "album_name" not in df.columns and "album" in df.columns:
            df.rename(columns={"album": "album_name"}, inplace=True)

        df = df.dropna(subset=FEATURE_COLS)

        # ---------------- Release date filtering ----------------
        if 'release_date' in df.columns:
            df['release_year'] = pd.to_datetime(df['release_date'], errors='coerce').dt.year
            current_year = datetime.datetime.now().year
            df = df[df['release_year'] >= current_year - MAX_TRACK_AGE]

        scaler = StandardScaler()
        X = scaler.fit_transform(df[FEATURE_COLS])
        df["vector"] = list(X)

        # ---------------- Context Filtering ----------------
        if mood == "Calm":
            df_context = df[df["energy"] <= 0.5]
        elif mood == "Energetic":
            df_context = df[df["energy"] >= 0.6]
        else:
            df_context = df.copy()  # Neutral

        # Time-of-day adjustment
        hour = datetime.datetime.now().hour
        if hour < 6 or hour >= 20:
            df_context = df_context[df_context["energy"] <= 0.6]
        elif 6 <= hour < 12:
            df_context = df_context[df_context["energy"] >= 0.4]

        if len(df_context) < 10:
            df_context = df.copy()  # fallback

        # ---------------- Context Vector ----------------
        context_vector = np.mean(np.vstack(df_context["vector"].values), axis=0).reshape(1, -1)
        vectors = np.vstack(df_context["vector"].values)
        similarity = cosine_similarity(vectors, context_vector).flatten()

        # ---------------- Bias ----------------
        bias = np.zeros(len(df_context))
        if mood == "Calm":
            bias += (1 - df_context["energy"].values)
        elif mood == "Energetic":
            bias += df_context["energy"].values
        else:
            bias += 0.5

        if hour < 6 or hour >= 20:
            bias += (1 - df_context["energy"].values) * 0.5
        elif 6 <= hour < 12:
            bias += df_context["energy"].values * 0.5

        # ---------------- Popularity weighting ----------------
        if 'popularity' in df_context.columns:
            bias += df_context['popularity'].values / 100  # normalize 0–1

        # ---------------- Final Score ----------------
        score = 0.4 * similarity + 0.3 * bias
        score += np.random.uniform(0, 0.05, len(score))  # small randomness
        df_context["score"] = score

        return df_context.sort_values("score", ascending=False).head(30)

    except Exception as e:
        messagebox.showerror("Error", str(e))
        return pd.DataFrame()

# ---------------- TKINTER UI ----------------
def browse_file():
    file_path = filedialog.askopenfilename(
        title="Select Spotify CSV",
        filetypes=(("CSV files", "*.csv"), ("All files", "*.*"))
    )
    if file_path:
        file_label.config(text=file_path)
        get_mood_and_recommend(file_path)

def get_mood_and_recommend(file_path):
    mood_question = simpledialog.askstring("Mood Question", "How do you feel right now in one word?")
    mood_question = mood_question.capitalize() if mood_question else "Neutral"

    wav_path = record_voice(duration=10)
    voice_mood = analyze_voice_mood(wav_path)

    weather_mood = get_weather_mood()

    moods = {"Calm":0, "Neutral":1, "Energetic":2}
    combined_index = int(round((moods.get(voice_mood,1)+moods.get(mood_question,1)+moods.get(weather_mood,1))/3))
    inv_moods = {v:k for k,v in moods.items()}
    final_mood = inv_moods[combined_index]

    results = recommend(file_path, final_mood)
    display_results(results)

def display_results(df):
    for widget in canvas_frame.winfo_children():
        widget.destroy()

    if df.empty:
        tk.Label(canvas_frame, text="No recommendations available").pack()
        return

    for idx, row in df.iterrows():
        frame = tk.Frame(canvas_frame, relief=tk.RAISED, borderwidth=1, padx=5, pady=5)
        frame.pack(fill=tk.X, pady=5)

        try:
            url = album_art_placeholder(row["artists"], row.get("album_name", row["track_name"]))
            response = requests.get(url)
            img = Image.open(io.BytesIO(response.content))
            img = img.resize((80,80))
            photo = ImageTk.PhotoImage(img)
            label_img = tk.Label(frame, image=photo)
            label_img.image = photo  # keep reference
            label_img.pack(side=tk.LEFT, padx=5)
        except:
            pass

        info = f"{row['track_name']} \nby {row['artists']}"
        tk.Label(frame, text=info, justify=tk.LEFT, font=("Arial",10,"bold")).pack(side=tk.LEFT, padx=5)

# ---------------- MAIN WINDOW ----------------
root = tk.Tk()
root.title("Spotify Context Music Engine")

top_frame = tk.Frame(root)
top_frame.pack(pady=10)

browse_btn = tk.Button(top_frame, text="Select CSV File", command=browse_file)
browse_btn.pack(side=tk.LEFT, padx=5)

file_label = tk.Label(top_frame, text="No file selected", wraplength=400)
file_label.pack(side=tk.LEFT, padx=5)

# Scrollable canvas for results
results_container = tk.Frame(root)
results_container.pack(fill=tk.BOTH, expand=True)

canvas = tk.Canvas(results_container)
scrollbar = tk.Scrollbar(results_container, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)

scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

canvas_frame = tk.Frame(canvas)
canvas.create_window((0,0), window=canvas_frame, anchor="nw")

def on_frame_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

canvas_frame.bind("<Configure>", on_frame_configure)

root.mainloop()
