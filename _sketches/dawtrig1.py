import dawdreamer as daw
import numpy as np
import time
from scipy.io import wavfile  # Import wavfile from scipy.io

SAMPLE_RATE = 44100

def make_sine(freq: float, duration: float, sr=SAMPLE_RATE):
  """Return sine wave based on freq in Hz and duration in seconds"""
  N = int(duration * sr) # Number of samples 
  return np.sin(np.pi*2.*freq*np.arange(N)/sr)

BUFFER_SIZE = 128 # Parameters will undergo automation at this buffer/block size.
PPQN = 960 # Pulses per quarter note.
SYNTH_PLUGIN = "C:/Users/dburbano/source/repos/dawdreamer/dawdreamer/assets/blocks.vst3/Contents/x86_64-win/blocks.vst3"  # extensions: .dll, .vst3, .vst, .component
# REVERB_PLUGIN = "C:/path/to/reverb.dll"  # extensions: .dll, .vst3, .vst, .component
MIDI_PATH = "C:/Users/dburbano/source/repos/dawdreamer/dawdreamer/assets/blocks-2.mid"

engine = daw.RenderEngine(SAMPLE_RATE, BUFFER_SIZE)

# Make a processor and give it the unique name "my_synth", which we use later.
synth = engine.make_plugin_processor("my_synth", SYNTH_PLUGIN)
assert synth.get_name() == "my_synth"

#load preser
synth.load_vst3_preset('C:/Users/dburbano/source/repos/dawdreamer/dawdreamer/assets/clappy.vstpreset')

# Load a MIDI file and keep the timing in units of beats. Changes to the Render Engine's BPM
# will affect the timing.
synth.load_midi(MIDI_PATH, beats=True)

# For any processor type, we can get the number of inputs and outputs
print("synth num inputs: ", synth.get_num_input_channels())
print("synth num outputs: ", synth.get_num_output_channels())

graph = [
  (synth, []),  # synth takes no inputs, so we give an empty list.
  # (reverb_processor, [synth.get_name()])  # hard-coding "my_synth" also works instead of get_name()
]

engine.load_graph(graph)
engine.render(5)  # Render 5 seconds of audio.
# engine.render(5, beats=True)  # Render 5 beats of audio.

audio = engine.get_audio()
filename = 'test'+str(time.time())+'.wav'
wavfile.write(filename, SAMPLE_RATE, audio.transpose())