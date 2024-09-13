import logging
import mido
from tkinter import Tk, filedialog

# Hide the root window
root = Tk()
root.withdraw()

# Open a file dialog to select a .mid file
midi_file_path = filedialog.askopenfilename(
    title="Select a MIDI file",
    filetypes=[("MIDI files", "*.mid"), ("All files", "*.*")]
)

# Check if a file was selected
if not midi_file_path:
    print("No file selected. Exiting.")
    exit()

# Load the selected MIDI file
midi = mido.MidiFile(midi_file_path)

# Function to calculate the length of each track
def calculate_track_length(track):
    total_time = 0
    for msg in track:
        total_time += msg.time
        if msg.type == 'end_of_track':
            break
    return total_time

# Calculate the length of each track and find the longest one
longest_track_length = 0
longest_track_index = -1

for i, track in enumerate(midi.tracks):
    track_length = calculate_track_length(track)
    if track_length > longest_track_length:
        longest_track_length = track_length
        longest_track_index = i

# Ensure the tempo is defined
tempo = 500000  # Default tempo (120 BPM) in microseconds per beat
for msg in midi.tracks[0]:
    if msg.type == 'set_tempo':
        tempo = msg.tempo
        break

# Convert the longest track length from ticks to seconds
longest_track_length_seconds = mido.tick2second(longest_track_length, midi.ticks_per_beat, tempo)

print(f"The longest track is Track {longest_track_index} with a length of {longest_track_length_seconds:.2f} seconds.")