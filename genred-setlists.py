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
        # Display selected song details
        selected_song = song_dropdown.get()
        if selected_song:
            selected_song_data = df[df['filename'] == selected_song].iloc[0]
            selected_song_info.set(f"Title: {selected_song_data['filename']}, BPM: {selected_song_data['bpm']}, Key: {selected_song_data['key']}")

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

    root.mainloop()

# Example usage
folder_path = "tracks"  # Specify your music folder path herefolder_path = "tracks"  # Path to the folder containing MP3 files
df, genres = extract_metadata(folder_path)  # Extract metadata and genres from the MP3 filesdf, genres = extract_metadata(folder_path)  # Extract metadata from the MP3 files



create_genre_based_gui(df, genres)  # Create and display the GUI# df['genre'] = (["Pop", "Rock", "Jazz", "Electronic", "Classical"] * (len(df) // 5 + 1))[:len(df)]  # Ensure exact length match

