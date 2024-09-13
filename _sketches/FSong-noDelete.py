import dawdreamer as daw
import numpy as np
import time
import os
import subprocess
from scipy.io import wavfile
from mido import MidiFile, MidiTrack
import sys

# Constants
SAMPLE_RATE = 44100
BUFFER_SIZE = 128
PPQN = 960

# Get the directory of the current script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Paths to assets
SYNTH_PLUGIN1 = os.path.join(SCRIPT_DIR, "assets", "blocks.vst3", "Contents", "x86_64-win", "blocks.vst3")
SYNTH_PLUGIN2 = os.path.join(SCRIPT_DIR, "assets", "blocks.vst3", "Contents", "x86_64-win", "blocks.vst3")
SYNTH_PLUGIN3 = os.path.join(SCRIPT_DIR, "assets", "blocks.vst3", "Contents", "x86_64-win", "blocks.vst3")
SYNTH_PLUGIN4 = os.path.join(SCRIPT_DIR, "assets", "AudiblePlanets.vst3", "Contents", "x86_64-win", "AudiblePlanets.vst3")
SYNTH_PLUGIN5 = os.path.join(SCRIPT_DIR, "assets", "Dexed.vst3")
SYNTH_PLUGIN6 = os.path.join(SCRIPT_DIR, "assets", "AudiblePlanets.vst3", "Contents", "x86_64-win", "AudiblePlanets.vst3")
SYNTH_PLUGIN7 = os.path.join(SCRIPT_DIR, "assets", "discoDSP", "OB-Xd 3.dll")
MIDI_PATH = os.path.join(SCRIPT_DIR, "assets", "dBTestSong.mid")
PRESETS = [
    os.path.join(SCRIPT_DIR, 'assets', 'clappy.vstpreset'),
    os.path.join(SCRIPT_DIR, 'assets', 'snare0.vstpreset'),
    os.path.join(SCRIPT_DIR, 'assets', 'kicky.vstpreset'),
    os.path.join(SCRIPT_DIR, 'assets', 'venus-dawn.vstpreset'),
    os.path.join(SCRIPT_DIR, 'assets', 'dxBass-t5.vstpreset'),
    os.path.join(SCRIPT_DIR, 'assets', 'spacelead1.vstpreset'),
    os.path.join(SCRIPT_DIR, 'assets', 'Ob_x-bass.fxp')
]

def make_sine(freq: float, duration: float, sr=SAMPLE_RATE):
    """Return sine wave based on freq in Hz and duration in seconds"""
    N = int(duration * sr)
    return np.sin(np.pi * 2. * freq * np.arange(N) / sr)

def initialize_engine(sample_rate, buffer_size):
    return daw.RenderEngine(sample_rate, buffer_size)

def create_synth(engine, plugin_path, preset_path, name):
    synth = engine.make_plugin_processor(name, plugin_path)
    assert synth.get_name() == name
    
    # Check the file extension and load the preset accordingly
    _, ext = os.path.splitext(preset_path)
    if ext == '.vstpreset':
        synth.load_vst3_preset(preset_path)
    elif ext == '.fxp':
        synth.load_preset(preset_path)
        
    else:
        raise ValueError(f"Unsupported preset file extension: {ext}")
    
    return synth

def load_midi_tracks(midi_path):
    midi = MidiFile(midi_path)
    tracks = [track for track in midi.tracks]
    return tracks

def extract_tempo_from_track_0(track):
    for msg in track:
        if msg.type == 'set_tempo':
            return msg.tempo
    return None

def filter_midi_events(track):
    filtered_track = MidiTrack()
    for msg in track:
        if not msg.is_meta:
            filtered_track.append(msg)
    return filtered_track

def assign_midi_to_synth(synth, midi_events):
    temp_midi = MidiFile()
    temp_midi.tracks.append(midi_events)
    temp_midi_path = 'temp_midi.mid'
    temp_midi.save(temp_midi_path)
    synth.load_midi(temp_midi_path, beats=True)
    return temp_midi_path

def render_audio(engine, duration):
    engine.render(duration)
    return engine.get_audio()

def save_audio(filename, sample_rate, audio):
    wavfile.write(filename, sample_rate, audio.transpose())

def mix_audio_files_with_ffmpeg(filenames, output_filename):
    input_args = []
    for filename in filenames:
        input_args.extend(['-i', filename])
    
    amix_filter = f"amix=inputs={len(filenames)}:duration=longest"
    
    # Adjust audio volume to -3dB
    volume_filter = f"volume=-3dB"
    
    subprocess.run(['ffmpeg', *input_args, '-filter_complex', f"{amix_filter},{volume_filter}", '-y', output_filename])

def main():
    engine = initialize_engine(SAMPLE_RATE, BUFFER_SIZE)
    
    synths = [
        create_synth(engine, SYNTH_PLUGIN1, PRESETS[0], "my_synth_1"),
        create_synth(engine, SYNTH_PLUGIN2, PRESETS[1], "my_synth_2"),
        create_synth(engine, SYNTH_PLUGIN3, PRESETS[2], "my_synth_3"),
        create_synth(engine, SYNTH_PLUGIN4, PRESETS[3], "my_synth_4"),
        create_synth(engine, SYNTH_PLUGIN5, PRESETS[4], "my_synth_5"),
        create_synth(engine, SYNTH_PLUGIN6, PRESETS[5], "my_synth_6"),
        create_synth(engine, SYNTH_PLUGIN7, PRESETS[6], "my_synth_7")
    ]
    
    midi_tracks = load_midi_tracks(MIDI_PATH)
    temp_midi_files = []
    individual_audio_files = []
    norm_audio_files = []

    # Extract tempo from Track 0 of the MIDI file
    midi = MidiFile(MIDI_PATH)
    tempo = extract_tempo_from_track_0(midi.tracks[0])
    if tempo:
        # Convert tempo to BPM
        bpm = 120000000 / tempo
        # Set the BPM in the engine
        engine.set_bpm(bpm)

    for i, synth in enumerate(synths):
        track_index = i + 1  # Start from Track 1
        if track_index < len(midi_tracks):
            filtered_events = filter_midi_events(midi_tracks[track_index])
            temp_midi_path = assign_midi_to_synth(synth, filtered_events)
            temp_midi_files.append(temp_midi_path)
            
            # Render individual audio track
            graph = [(synth, [])]
            engine.load_graph(graph)
            audio = render_audio(engine, 34)
            individual_filename = f'track_{track_index}_{time.time()}.wav'
            save_audio(individual_filename, SAMPLE_RATE, audio)
            individual_audio_files.append(individual_filename)

           # Normalize audio to -3dB
            normalized_audio = audio / np.max(np.abs(audio)) * 10 ** (-3 / 20)

            # Save normalized audio
            normalized_filename = f'normalized_track_{track_index}_{time.time()}.wav'
            save_audio(normalized_filename, SAMPLE_RATE, normalized_audio)
            norm_audio_files.append(normalized_filename)
            
            print(f"synth_{i+1} num inputs: ", synth.get_num_input_channels())
            print(f"synth_{i+1} num outputs: ", synth.get_num_output_channels())
    
    # Mix individual audio files into one using FFMPEG
    mixed_filename = 'mixed_' + str(time.time()) + '.wav'
    mix_audio_files_with_ffmpeg(norm_audio_files, mixed_filename)
    print(f"Mixed audio saved to {mixed_filename}")
    
    # Delete temporary MIDI files
    for temp_midi_path in temp_midi_files:
        if os.path.exists(temp_midi_path):
            os.remove(temp_midi_path)
            print(f"Deleted temporary file: {temp_midi_path}")
    
    # Optionally delete individual audio files
    # for individual_filename in individual_audio_files:
      #  if os.path.exists(individual_filename):
       #     os.remove(individual_filename)
        #    print(f"Deleted individual audio file: {individual_filename}")

if __name__ == "__main__":
    main()
    sys.exit()