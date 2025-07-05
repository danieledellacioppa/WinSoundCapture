import sounddevice as sd
import soundfile as sf

# Durata della registrazione in secondi
DURATION = 10
OUTPUT_FILENAME = "output.wav"

# Ottieni lista dei dispositivi audio
devices = sd.query_devices()
default_output = sd.default.device['output']
print(f"Using default output device for loopback: {devices[default_output]['name']}")

# Imposta parametri
samplerate = int(sd.query_devices(default_output)['default_samplerate'])
channels = 2  # stereo

# Registra in loopback
print("Recording...")
recording = sd.rec(int(DURATION * samplerate),
                   samplerate=samplerate,
                   channels=channels,
                   dtype='float32',
                   blocking=True,
                   device=(None, default_output),
                   mapping=None,
                   clip_off=True,
                   latency='low',
                   loopback=True)  # ATTENZIONE: solo su Windows!

# Salva come WAV
sf.write(OUTPUT_FILENAME, recording, samplerate)
print(f"Recording saved to {OUTPUT_FILENAME}")
