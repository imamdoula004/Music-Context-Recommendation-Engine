# Spotify-Context-Recommendation-Engine 

---
# overview: 
  Spotify Context Recommendation Engine is a local, desktop-based, context-aware music recommendation system. It analyzes time of day, voice-based sentiment, a short mood question, weather conditions, and audio features to recommend relevant and recent tracks from a large Spotify dataset.

# dataset:
  name: "Spotify Dataset (1921–2020) — 600K+ Tracks 
  platform: "Kaggle"
  link: "https://www.kaggle.com/datasets/yamaerenay/spotify-dataset-19212020-600k-tracks"
  description: 
    The dataset contains over 600,000 Spotify tracks with
    audio features (energy, tempo, valence, danceability,
    acousticness), popularity scores, and release dates.
  usage_policy: 
    The dataset is NOT included in this repository due to
    size and licensing restrictions. Users must download
    the dataset directly from Kaggle.

# download_instructions: 
  1. Go to the Kaggle dataset link above.
  2. Log in or create a free Kaggle account.
  3. Download the dataset ZIP file.
  4. Extract the CSV file to any location on your system.
  5. When running the app, select the CSV file using the
     file selection dialog.

     # dependencies:
  description: 
    This project runs directly in your local Python environment.
    No virtual environment and no requirements.txt are used.
    You must manually install the following packages:
  install_command: 
    ` pip install pandas numpy scikit-learn pillow requests sounddevice scipy SpeechRecognition textblob `
  notes: 
    • tkinter is included with most Python installations.
    • Use pip3 or python -m pip if needed.

# execution:
  python_environment: 
    This project is designed to run directly on your
    existing local Python installation.
    • No virtual environment is required.
    • No requirements.txt is provided.
    • Users are free to manage dependencies in their own way.
 # run_command: 
    python main.py

# workflow:
  - "Launch the application using main.py"
  - "Select the Spotify CSV dataset when prompted"
  - "Answer a short mood question"
  - "Provide a 10-second voice input"
  - "Weather and time-of-day context are applied automatically"
  - "Scroll through personalized music recommendations"

# recommendation_logic:
  
  inputs:
  - "Audio features (energy, tempo, valence, danceability, acousticness)"
  - "Voice sentiment analysis"
  - "User-declared mood"
  - "Local weather conditions"
  - "Time of day"
  - "Track popularity"
  - "Track release recency"
  scoring_strategy: 
    Recommendations are ranked using a weighted combination
    of *cosine similarity*, *contextual bias (mood/time/weather)*,
    *popularity normalization*, and *controlled randomness* to
    preserve diversity while prioritizing relevance.

# features:
  - "Context-aware recommendation engine"
  - "Voice-based mood detection"
  - "Weather-informed music selection"
  - "Recency filtering (last ~10 years)"
  - "Popularity-aware ranking"
  - "Scrollable Tkinter UI"
  - "Album art placeholders for visual clarity"

# configuration:
  required_api_key: 
    *OpenWeatherMap API Key*
    Obtain from: https://openweathermap.org/api
  configurable_constants:
    - CITY_NAME (for weather context)
    - MAX_TRACK_AGE (default: 10 years)

# repository_structure:
  - main.py: "Single entry point for the entire application"
  - README.txt: "Project documentation"
  - .gitignore: |
      *.csv
      data/

# notes: 
  • This project intentionally avoids packaged environments
    to keep experimentation flexible and transparent.
  • The system is designed as a foundation for a larger
    Personal Context Engine and future research work.
  • Results may vary depending on dataset version and
    user environment configuration.

# license: |
MIT

# acknowledgements: |
  Kaggle user 'yamaerenay' for the Spotify 600K+ dataset.
---

