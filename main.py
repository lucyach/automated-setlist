import os  # Provides functions to interact with the operating system
from mutagen import File  # Import File for handling multiple audio formats
from mutagen.id3 import ID3, TBPM, TKEY  # Classes for handling ID3 tags
import pandas as pd  # Library for data manipulation and analysis
import matplotlib.pyplot as plt  # Library for creating visualizations
import seaborn as sns  # Library for statistical data visualization
import tkinter as tk  # GUI library for creating graphical interfaces
from tkinter import ttk  # Provides themed widgets for tkinter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # Embeds matplotlib plots in tkinter


def extract_metadata(mp3_folder):
    # Extract metadata (BPM and Key) from audio files in the specified folder
    data = []

    for filename in os.listdir(mp3_folder):  # Iterate through all files in the folder
        if filename.lower().endswith((".mp3", ".m4a", ".wav", ".crdownload")):  # Check if the file is an MP3, M4A, WAV, or CRDOWNLOAD
            file_path = os.path.join(mp3_folder, filename)  # Get the full file path
            try:
                audio = File(file_path)  # Use mutagen.File to handle multiple formats
                if audio and audio.tags:  # Ensure the file has tags
                    bpm = audio.tags.get('TBPM')  # Get the BPM tag
                    key = audio.tags.get('TKEY')  # Get the Key tag

                    bpm_value = int(bpm.text[0]) if bpm else None  # Extract BPM value if available
                    key_value = key.text[0] if key else "Unknown"  # Assign "Unknown" if key is missing or None

                    # Append the extracted data to the list
                    data.append({
                        "filename": filename,
                        "bpm": bpm_value,
                        "key": key_value
                    })
            except Exception as e:  # Handle errors during metadata extraction
                print(f"Failed to read {filename}: {e}")

    # Convert the list of data into a pandas DataFrame
    return pd.DataFrame(data)

def visualize_data(df):
    # Create visualizations for BPM and Key distributions
    sns.set(style="whitegrid")  # Set the style for seaborn plots

    # Drop rows with missing BPM or Key for visualization
    df_clean = df.dropna(subset=["bpm", "key"])

    plt.figure(figsize=(14, 6))  # Set the figure size

    # BPM Distribution
    plt.subplot(1, 2, 1)  # Create the first subplot
    sns.histplot(df_clean["bpm"], bins=30, kde=True, color="skyblue")  # Plot BPM histogram
    plt.title("BPM Distribution")  # Set the title
    plt.xlabel("BPM")  # Set the x-axis label
    plt.ylabel("Count")  # Set the y-axis label

    # Key Distribution
    plt.subplot(1, 2, 2)  # Create the second subplot
    sns.countplot(y="key", data=df_clean, order=df_clean["key"].value_counts().index, palette="mako")  # Plot Key count
    plt.title("Key Distribution")  # Set the title
    plt.xlabel("Count")  # Set the x-axis label
    plt.ylabel("Key")  # Set the y-axis label

    plt.tight_layout()  # Adjust layout to prevent overlap
    plt.show()  # Display the plots

def visualize_data_in_frame(df, frame):
    # Embed visualizations into a tkinter frame
    sns.set(style="whitegrid")  # Set the style for seaborn plots
    df_clean = df.dropna(subset=["bpm", "key"])  # Drop rows with missing BPM or Key

    fig, axes = plt.subplots(1, 2, figsize=(10, 4), dpi=100)  # Create subplots for BPM and Key

    # BPM Distribution
    sns.histplot(df_clean["bpm"], bins=30, kde=True, color="skyblue", ax=axes[0])  # Plot BPM histogram
    axes[0].set_title("BPM Distribution")  # Set the title
    axes[0].set_xlabel("BPM")  # Set the x-axis label
    axes[0].set_ylabel("Count")  # Set the y-axis label

    # Key Distribution
    sns.countplot(y="key", data=df_clean, order=df_clean["key"].value_counts().index, hue="key", palette="mako", ax=axes[1], legend=False)  # Plot Key count
    axes[1].set_title("Key Distribution")  # Set the title
    axes[1].set_xlabel("Count")  # Set the x-axis label
    axes[1].set_ylabel("Key")  # Set the y-axis label

    plt.tight_layout()  # Adjust layout to prevent overlap

    # Embed the matplotlib figure into the tkinter frame
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)  # Pack the canvas widget
    canvas.draw()  # Render the plot

def find_closest_songs(df, selected_song):
    # Find songs with the closest BPM to the selected song within ±5 BPM
    selected_bpm = df.loc[df['filename'] == selected_song, 'bpm'].values[0]  # Get the BPM of the selected song
    df['bpm_diff'] = abs(df['bpm'] - selected_bpm)  # Calculate the BPM difference
    closest_songs = df[df['bpm_diff'] <= 5].sort_values('bpm_diff').head(6)  # Filter songs within ±5 BPM
    return closest_songs[['filename', 'bpm']]  # Return the filenames and BPMs of the closest songs

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
        "Eb": "5B", "Ebm": "2A"  # Add missing Ebm mapping
    }
    return key_map.get(key, "")  # Return the Camelot key or an empty string if not found

def find_harmonic_matches(df, selected_song):
    # Find songs that harmonically match the selected song using Camelot keys
    camelot_map = camelot_key_mapping()
    match_types = {
        "Perfect match": "=",
        "Energy boost +": "+",
        "Energy boost ++": "++",
        "Energy boost +++": "+++",
        "Energy drop -": "-",
        "Energy drop --": "--",
        "Energy drop ---": "---",
        "Mood change": "Mood"
    }
    if selected_song in df['filename'].values:  # Ensure the selected song exists
        selected_key = df.loc[df['filename'] == selected_song, 'key'].values[0]  # Get the key of the selected song
        selected_bpm = df.loc[df['filename'] == selected_song, 'bpm'].values[0]  # Get the BPM of the selected song

        if selected_key == "Unknown":  # Handle case where key is unknown
            df['bpm_diff'] = abs(df['bpm'] - selected_bpm)  # Calculate BPM difference
            bpm_matches = df[df['bpm_diff'] <= 5].sort_values('bpm_diff')  # Filter songs within ±5 BPM
            bpm_matches['match_type'] = "BPM match"  # Assign match type for BPM-based matches
            return bpm_matches[['filename', 'bpm', 'match_type']]  # Return filenames, BPMs, and match types

        camelot_key = musical_key_to_camelot(selected_key)  # Convert to Camelot key
        if camelot_key:
            matching_keys = camelot_map.get(camelot_key, [])  # Get matching Camelot keys
            harmonic_matches = df[df['key'].apply(musical_key_to_camelot).isin(matching_keys)]  # Filter harmonic matches

            # Assign match type based on the chart
            harmonic_matches['match_type'] = harmonic_matches['key'].apply(
                lambda key: match_types["Perfect match ="] if musical_key_to_camelot(key) == camelot_key else
                            match_types["Energy boost +++"] if musical_key_to_camelot(key) in camelot_map[camelot_key][:1] else
                            match_types["Energy boost ++"] if musical_key_to_camelot(key) in camelot_map[camelot_key][:2] else
                            match_types["Energy boost +"] if musical_key_to_camelot(key) in camelot_map[camelot_key][2:] else
                            match_types["Energy drop -"] if musical_key_to_camelot(key) in camelot_map[camelot_key][-2:] else
                            match_types["Energy drop --"] if musical_key_to_camelot(key) in camelot_map[camelot_key][-3:] else
                            match_types["Energy drop ---"] if musical_key_to_camelot(key) in camelot_map[camelot_key][-4:] else
                            match_types["Mood change"]
            )

            # If no exact matches, find close matches
            if harmonic_matches.empty:
                key_number = int(camelot_key[:-1])  # Extract numeric part of the Camelot key
                key_letter = camelot_key[-1]       # Extract letter part of the Camelot key
                close_keys = [
                    f"{(key_number - 1) % 12 + 1}{key_letter}",
                    f"{(key_number + 1) % 12 + 1}{key_letter}"
                ]
                harmonic_matches = df[df['key'].apply(musical_key_to_camelot).isin(close_keys)]  # Filter close matches
                harmonic_matches['match_type'] = match_types["Energy drop -"]  # Assign match type for close matches
            
            return harmonic_matches[['filename', 'key', 'match_type']]  # Return filenames, keys, and match types
    return pd.DataFrame(columns=['filename', 'key', 'match_type'])  # Return an empty DataFrame if no matches found

def assign_points_and_sort(df, selected_song):
    # Assign points based on BPM and harmonic match closeness
    selected_bpm = df.loc[df['filename'] == selected_song, 'bpm'].values[0]  # Get the BPM of the selected song
    selected_key = df.loc[df['filename'] == selected_song, 'key'].values[0]  # Get the key of the selected song
    camelot_key = musical_key_to_camelot(selected_key)  # Convert to Camelot key

    if not camelot_key:  # Ensure camelot_key is valid
        print(f"Invalid key for song '{selected_song}': {selected_key}")
        return pd.DataFrame(columns=['filename', 'bpm', 'key', 'match_type', 'total_points', 'percentage'])  # Return an empty DataFrame

    camelot_map = camelot_key_mapping()

    # Calculate BPM difference points
    df['bpm_diff'] = abs(df['bpm'] - selected_bpm)
    df['bpm_points'] = df['bpm_diff'].apply(lambda diff: max(0, 10 - diff))  # Points decrease as BPM difference increases

    # Calculate harmonic match points and assign match type
    def calculate_harmonic_points_and_type(key):
        camelot_key_of_song = musical_key_to_camelot(key)
        if camelot_key_of_song == camelot_key:
            return 20, "="  # Perfect match
        elif camelot_key_of_song in camelot_map.get(camelot_key, [])[:1]:
            return 15, "+++"  # Energy boost +++
        elif camelot_key_of_song in camelot_map.get(camelot_key, [])[:2]:
            return 10, "++"  # Energy boost ++
        elif camelot_key_of_song in camelot_map.get(camelot_key, [])[2:]:
            return 5, "+"  # Energy boost +
        return 0, ""  # No harmonic match

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

    return sorted_df[['filename', 'bpm', 'key', 'match_type', 'total_points', 'percentage']]  # Return sorted DataFrame with relevant columns

def get_best_matches(df, selected_song):
    """
    Takes a song as input and returns the best matches with BPM, key, key match type, and match percentage.
    """
    if selected_song not in df['filename'].values:
        print(f"Song '{selected_song}' not found in the dataset.")
        return pd.DataFrame(columns=['filename', 'bpm', 'key', 'match_type', 'total_points', 'percentage'])

    sorted_matches = assign_points_and_sort(df, selected_song)
    sorted_matches = sorted_matches[sorted_matches['filename'] != selected_song]  # Exclude the selected song
    return sorted_matches[['filename', 'bpm', 'key', 'match_type', 'percentage']]

def create_gui(df):
    """
    Create the GUI for song selection and visualization.
    """
    def on_song_select(event):
        selected_song = song_dropdown.get()
        if selected_song:
            selected_song_data = df[df['filename'] == selected_song].iloc[0]
            selected_song_info.set(f"Title: {selected_song_data['filename']}, BPM: {selected_song_data['bpm']}, Key: {selected_song_data['key']}")

            # Use the new function to get best matches
            best_matches = get_best_matches(df, selected_song)

            # Clear the treeview
            for item in matches_tree.get_children():
                matches_tree.delete(item)

            # Populate the treeview with the best matches
            for _, row in best_matches.iterrows():
                matches_tree.insert("", "end", values=(
                    row['filename'], 
                    row['bpm'], 
                    row['key'], 
                    row['match_type'], 
                    row['percentage']
                ))

    root = tk.Tk()  # Create the main tkinter window
    root.title("Automated Setlist")  # Set the window title
    root.geometry("1400x900")  # Set default window size to be larger

    # Force larger font for dropdown list items
    root.option_add("*TCombobox*Listbox.font", ("Arial", 28))

    # Main frame
    main_frame = tk.Frame(root)  # Create the main frame
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)  # Pack the frame with padding

    # Song selection frame
    selection_frame = tk.Frame(main_frame, width=600, bg="#f0f0f0")  # Create the selection frame with background color
    selection_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)  # Pack the frame at the top

    tk.Label(selection_frame, text="Select a Song:", font=("Arial", 24, "bold"), bg="#f0f0f0").pack(pady=10)  # Label for song selection
    song_dropdown = ttk.Combobox(selection_frame, values=df['filename'].tolist(), font=("Arial", 28), height=10)  # Dropdown with larger font and height
    song_dropdown.pack(pady=20, fill=tk.X)  # Add more padding and ensure it fills horizontally
    song_dropdown.bind("<<ComboboxSelected>>", on_song_select)  # Bind selection event to handler

    # Selected song info
    selected_song_info = tk.StringVar()
    tk.Label(selection_frame, textvariable=selected_song_info, font=("Arial", 20), bg="#f0f0f0").pack(pady=10)  # Display selected song info

    # Matches chart frame
    chart_frame = tk.Frame(main_frame, bg="#f0f0f0", width=int(root.winfo_screenwidth() * 0.66))  # Chart frame takes 66% of the width
    chart_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)  # Pack the frame on the left

    tk.Label(chart_frame, text="Matches Chart:", font=("Arial", 24, "bold"), bg="#f0f0f0").pack(pady=10)  # Label for matches chart

    # Apply custom style to Treeview
    style = ttk.Style()
    style.configure("Treeview", font=("Arial", 18), rowheight=40)  # Set font size and increase row height
    style.configure("Treeview.Heading", font=("Arial", 20, "bold"))  # Set font size for column headings
    style.configure("TCombobox", font=("Arial", 28))  # Set font size for dropdown list items
    style.configure("ComboboxPopdownFrame", font=("Arial", 28))  # Force larger font for the dropdown popup list
    style.map("TCombobox", fieldbackground=[("readonly", "#f0f0f0")], background=[("readonly", "#f0f0f0")])  # Ensure consistent styling

    # Treeview for displaying matches
    columns = ("Song Title", "BPM", "Key", "Key Match Type", "Match Percentage")
    matches_tree = ttk.Treeview(chart_frame, columns=columns, show="headings", height=25, style="Treeview")
    matches_tree.heading("Song Title", text="Song Title")
    matches_tree.heading("BPM", text="BPM")
    matches_tree.heading("Key", text="Key")
    matches_tree.heading("Key Match Type", text="Key Match Type")
    matches_tree.heading("Match Percentage", text=" Match Percentage")
    matches_tree.column("Song Title", anchor="w", width=300)
    matches_tree.column("BPM", anchor="center", width=100)
    matches_tree.column("Key", anchor="center", width=100)
    matches_tree.column("Key Match Type", anchor="center", width=100)
    matches_tree.column("Match Percentage", anchor="center", width=100)
    matches_tree.pack(fill=tk.BOTH, expand=True)

    # Visualization frame
    visualization_frame = tk.Frame(main_frame, bg="#f0f0f0", width=400, height=300)  # Set fixed width and height for the visualization frame
    visualization_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10, pady=10)  # Pack the frame on the right

    visualize_data_in_frame(df, visualization_frame)  # Embed visualizations in the frame

    root.mainloop()  # Start the tkinter main loop

# Usage
folder_path = "tracks"  # Path to the folder containing MP3 files
df = extract_metadata(folder_path)  # Extract metadata from the MP3 files
create_gui(df)  # Create and display the GUI

# Example track for testing
df.loc[len(df)] = {"filename": "TestTrack.mp3", "bpm": 128, "key": "C#m"}  # Add a test track with key "C#m" for testing