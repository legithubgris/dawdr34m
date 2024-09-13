import os
from mido import MidiFile

# Get the path of the assets folder relative to the script
assets_folder = os.path.join(os.path.dirname(__file__), 'assets')

midi_file_path = os.path.join(assets_folder, 'OpenSaurceVSTTest.mid')
midi = MidiFile(midi_file_path)

for i, track in enumerate(midi.tracks):
    print('Track {}: {}'.format(i, track.name))
    for msg in track:
        print(msg)