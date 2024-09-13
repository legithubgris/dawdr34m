import os
import logging
from mido import MidiFile
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

# Get the log file path
log_file_path = os.path.splitext(midi_file_path)[0] + '.log'

# Configure logging
logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(message)s')

# Load the selected MIDI file
midi = MidiFile(midi_file_path)

for i, track in enumerate(midi.tracks):
    logging.info('Track {}: {}'.format(i, track.name))
    for msg in track:
        logging.info(msg)