import os  # Provides functions to interact with the operating system
from mutagen import File  # Import File for handling multiple audio formats
from mutagen.id3 import ID3, TBPM, TKEY  # Classes for handling ID3 tags
import pandas as pd  # Library for data manipulation and analysis
import matplotlib.pyplot as plt  # Library for creating visualizations
import seaborn as sns  # Library for statistical data visualization
import tkinter as tk  # GUI library for creating graphical interfaces
from tkinter import ttk  # Provides themed widgets for tkinter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # Embeds matplotlib plots in tkinter

def extract_metadata(folder_path):
    """Extract metadata from audio files in the given folder."""
    # Initialize an empty list to store metadata for each file
    metadata = []
    genres_set = set()  # Collect unique genres

    # Iterate over all files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith(".mp3") or filename.endswith(".wav"):  # Check for audio file extensions
            file_path = os.path.join(folder_path, filename)  # Get the full file path
            audio = File(file_path)  # Load the audio file

            # Extract ID3 tag information if available
            if audio and audio.tags:
                bpm = audio.tags.get('TBPM')
                key = audio.tags.get('TKEY')
                genre = audio.tags.get('TCON')
                if genre:
                    genres_set.add(genre.text[0])  # Add genre to the set
            else:
                bpm = key = genre = None

            # Append the metadata as a dictionary to the list
            metadata.append({
                'filename': filename,
                'bpm': bpm.text[0] if bpm else None,
                'key': key.text[0] if key else None,
                'genre': genre.text[0] if genre else None
            })

    # Convert the metadata list to a DataFrame for easier analysis
    return pd.DataFrame(metadata), sorted(genres_set)  # Return metadata and sorted genres

def create_genre_based_gui(df, genres):
    """Create a GUI for genre-based song selection."""
    # Extract unique genres from the song data
    # genres = df['genre'].dropna().unique().tolist()

    def on_genre_select():
        # Filter songs based on selected genres
        selected_genres = [genre for genre, var in genre_vars.items() if var.get()]
        filtered_songs = df[df['genre'].isin(selected_genres)]
        song_dropdown['values'] = filtered_songs['filename'].tolist()

    def on_song_select(event):
        # Display selected song details and top matches
        selected_song = song_dropdown.get()
        if selected_song:
            selected_song_data = df[df['filename'] == selected_song].iloc[0]
            selected_song_info.set(f"Title: {selected_song_data['filename']}, BPM: {selected_song_data['bpm']}, Key: {selected_song_data['key']}")
            
            # Display top matches
            display_top_matches_gui(df, selected_song)

    def display_top_matches_gui(df, selected_song):
        # Clear previous matches
        for widget in matches_frame.winfo_children():
            widget.destroy()

        # Get top matches
        sorted_matches = assign_points_and_sort(df, selected_song)
        sorted_matches = sorted_matches[sorted_matches['filename'] != selected_song].head(5)  # Exclude selected song and get top 5

        tk.Label(matches_frame, text="Top Matches:", font=("Arial", 16, "bold")).pack(anchor="w", pady=5)

        # Create a scrollable canvas for matches
        canvas = tk.Canvas(matches_frame)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(matches_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        matches_list_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=matches_list_frame, anchor="nw")

        for _, row in sorted_matches.iterrows():
            match_text = f"{row['filename']} ({row['percentage']}%)"
            tk.Button(matches_list_frame, text=match_text, font=("Arial", 12), width=40).pack(anchor="w", pady=2)

    root = tk.Tk()
    root.title("Genre-Based Setlist Generator")
    root.geometry("800x600")

    # Main frame
    main_frame = tk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    # Genre selection frame with scrollable canvas
    genre_frame = tk.Frame(main_frame)
    genre_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

    tk.Label(genre_frame, text="Select Genres:", font=("Arial", 16, "bold")).pack(anchor="w", pady=5)

    canvas = tk.Canvas(genre_frame)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = tk.Scrollbar(genre_frame, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    genre_list_frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=genre_list_frame, anchor="nw")

    genre_vars = {genre: tk.BooleanVar() for genre in genres}
    for i, (genre, var) in enumerate(genre_vars.items()):
        tk.Checkbutton(genre_list_frame, text=genre, variable=var, font=("Arial", 8), command=on_genre_select).grid(row=i // 5, column=i % 5, padx=5, pady=5)

    # Song selection frame
    selection_frame = tk.Frame(main_frame)
    selection_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

    tk.Label(selection_frame, text="Select a Song:", font=("Arial", 16, "bold")).pack(anchor="w", pady=5)
    song_dropdown = ttk.Combobox(selection_frame, font=("Arial", 14), height=10)
    song_dropdown.pack(fill=tk.X, pady=5)
    song_dropdown.bind("<<ComboboxSelected>>", on_song_select)

    # Selected song info
    selected_song_info = tk.StringVar()
    tk.Label(selection_frame, textvariable=selected_song_info, font=("Arial", 14)).pack(anchor="w", pady=5)

    # Matches frame
    matches_frame = tk.Frame(main_frame)
    matches_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

    root.mainloop()

def camelot_key_mapping():
    # Define the Camelot mixing wheel for harmonic mixing
    return {
        "1A": ["12A", "2A", "1B"],
        "2A": ["1A", "3A", "2B"],
        "3A": ["2A", "4A", "3B"],
        "4A": ["3A", "5A", "4B"],
        "5A": ["4A", "6A", "5B"],
        "6A": ["5A", "7A", "6B"],
        "7A": ["6A", "8A", "7B"],
        "8A": ["7A", "9A", "8B"],
        "9A": ["8A", "10A", "9B"],
        "10A": ["9A", "11A", "10B"],
        "11A": ["10A", "12A", "11B"],
        "12A": ["11A", "1A", "12B"],
        "1B": ["12B", "2B", "1A"],
        "2B": ["1B", "3B", "2A"],
        "3B": ["2B", "4B", "3A"],
        "4B": ["3B", "5B", "4A"],
        "5B": ["4B", "6B", "5A"],
        "6B": ["5B", "7B", "6A"],
        "7B": ["6B", "8B", "7A"],
        "8B": ["7B", "9B", "8A"],
        "9B": ["8B", "10B", "9A"],
        "10B": ["9B", "11B", "10A"],
        "11B": ["10B", "12B", "11A"],
        "12B": ["11B", "1B", "12A"]
    }

def musical_key_to_camelot(key):
    # Map musical keys to Camelot keys
    key_map = {
        "C": "8B", "Cm": "5A", "C#": "3B", "C#m": "12A",
        "D": "10B", "Dm": "7A", "D#": "5B", "D#m": "2A",
        "E": "12B", "Em": "9A", "F": "7B", "Fm": "4A",
        "F#": "2B", "F#m": "11A", "G": "9B", "Gm": "6A",
        "G#": "4B", "G#m": "1A", "A": "11B", "Am": "8A",
        "A#": "6B", "A#m": "3A", "B": "1B", "Bm": "10A",
        "Db": "3B", "Dbm": "12A", "Ab": "4B", "Abm": "1A", "Bb": "6B", "Bbm": "3A",
        "Eb": "5B", "Ebm": "2A"
    }
    return key_map.get(key, "")

def assign_points_and_sort(df, selected_song):
    # Assign points based on BPM and harmonic match closeness
    df['bpm'] = pd.to_numeric(df['bpm'], errors='coerce')  # Convert BPM to numeric, invalid values become NaN
    selected_bpm = pd.to_numeric(df.loc[df['filename'] == selected_song, 'bpm'].values[0], errors='coerce')
    selected_key = df.loc[df['filename'] == selected_song, 'key'].values[0]
    camelot_key = musical_key_to_camelot(selected_key)

    if pd.isna(selected_bpm) or not camelot_key:
        print(f"Invalid data for song '{selected_song}': BPM={selected_bpm}, Key={selected_key}")
        return pd.DataFrame(columns=['filename', 'bpm', 'key', 'match_type', 'total_points', 'percentage'])

    camelot_map = camelot_key_mapping()

    # Calculate BPM difference points
    df['bpm_diff'] = abs(df['bpm'] - selected_bpm)
    df['bpm_points'] = df['bpm_diff'].apply(lambda diff: max(0, 10 - diff))

    # Calculate harmonic match points and assign match type
    def calculate_harmonic_points_and_type(key):
        camelot_key_of_song = musical_key_to_camelot(key)
        if camelot_key_of_song == camelot_key:
            return 20, "="
        elif camelot_key_of_song in camelot_map.get(camelot_key, [])[:1]:
            return 15, "+++"
        elif camelot_key_of_song in camelot_map.get(camelot_key, [])[:2]:
            return 10, "++"
        elif camelot_key_of_song in camelot_map.get(camelot_key, [])[2:]:
            return 5, "+"
        return 0, ""

    df[['harmonic_points', 'match_type']] = df['key'].apply(
        lambda key: pd.Series(calculate_harmonic_points_and_type(key))
    )

    # Calculate total points
    df['total_points'] = df['bpm_points'] + df['harmonic_points']

    # Calculate percentage based on maximum possible points (20 harmonic + 10 BPM = 30)
    max_points = 30
    df['percentage'] = (df['total_points'] / max_points * 100).round(2)

    # Sort by total points in descending order
    sorted_df = df.sort_values(by='total_points', ascending=False)

    return sorted_df[['filename', 'bpm', 'key', 'match_type', 'total_points', 'percentage']]

def display_top_matches(df, selected_song):
    # Display the top 5 matches for the selected song
    if selected_song not in df['filename'].values:
        print(f"Song '{selected_song}' not found in the dataset.")
        return

    sorted_matches = assign_points_and_sort(df, selected_song)
    sorted_matches = sorted_matches[sorted_matches['filename'] != selected_song]  # Exclude the selected song
    top_matches = sorted_matches.head(5)  # Get the top 5 matches

    print(f"Top 5 matches for '{selected_song}':")
    print(top_matches.to_string(index=False))

# Example usage
folder_path = "tracks"  # Specify your music folder path here
df, genres = extract_metadata(folder_path)  # Extract metadata and genres from the MP3 files
create_genre_based_gui(df, genres)  # Launch the GUI

# df['genre'] = (["Pop", "Rock", "Jazz", "Electronic", "Classical"] * (len(df) // 5 + 1))[:len(df)]  # Ensure exact length match

