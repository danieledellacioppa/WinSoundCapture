import argparse
import datetime
import queue
import shutil
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

import sounddevice as sd
import soundfile as sf


class SoundDeviceRecorder:
    """Recorder implementation using sounddevice."""

    def __init__(self, samplerate=44100, channels=2):
        self.q = queue.Queue()
        self.fs = samplerate
        self.channels = channels
        self.recording = False
        self.thread = None

    def _callback(self, indata, frames, time, status):
        if status:
            print(status)
        self.q.put(indata.copy())

    def _get_loopback_device(self):
        for i, dev in enumerate(sd.query_devices()):
            if 'loopback' in dev['name'].lower():
                return i
        raise RuntimeError("Nessun dispositivo di loopback trovato.")

    def _record(self, filename):
        try:
            with sf.SoundFile(filename, mode="w", samplerate=self.fs, channels=self.channels) as file:
                with sd.InputStream(
                        samplerate=self.fs,
                        channels=self.channels,
                        dtype="float32",
                        callback=self._callback,
                        blocksize=1024,
                        device=self._get_loopback_device()):
                    while self.recording:
                        file.write(self.q.get())
        except Exception as e:
            messagebox.showerror("Recording Error", str(e))
            self.recording = False

    def start(self, filename):
        if self.recording:
            return
        self.recording = True
        self.thread = threading.Thread(target=self._record, args=(filename,), daemon=True)
        self.thread.start()

    def stop(self):
        self.recording = False
        if self.thread:
            self.thread.join()
            self.thread = None


class FFmpegRecorder:
    """Recorder implementation using ffmpeg WASAPI."""

    def __init__(self):
        self.process = None

    def _find_ffmpeg(self):
        path = shutil.which("ffmpeg")
        if not path:
            raise RuntimeError("ffmpeg not found. Please install it and ensure it's in PATH.")
        return path

    def start(self, filename, duration=None):
        if self.process:
            return
        ffmpeg = self._find_ffmpeg()
        cmd = [ffmpeg, "-y", "-f", "wasapi", "-i", "default",
               "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "2"]
        if duration:
            cmd += ["-t", str(duration)]
        cmd.append(filename)
        try:
            print("Running:", " ".join(cmd))
            self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except Exception as e:
            messagebox.showerror("Recording Error", str(e))
            self.process = None

    def stop(self):
        if not self.process:
            return
        self.process.terminate()
        self.process.wait()
        self.process = None


def ensure_wav_extension(path):
    if not path.lower().endswith('.wav'):
        path += '.wav'
    return path


def main():
    root = tk.Tk()
    root.title("WinSoundCapture")

    file_var = tk.StringVar(value="output.wav")
    duration_var = tk.StringVar()
    method_var = tk.StringVar(value="sounddevice")

    tk.Label(root, text="Output file:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    file_entry = tk.Entry(root, textvariable=file_var, width=40)
    file_entry.grid(row=0, column=1, padx=5, pady=5)

    def browse():
        filename = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV files", "*.wav")])
        if filename:
            file_var.set(filename)

    tk.Button(root, text="Browse", command=browse).grid(row=0, column=2, padx=5, pady=5)

    tk.Label(root, text="Duration (sec, ffmpeg only):").grid(row=1, column=0, padx=5, pady=5, sticky="e")
    duration_entry = tk.Entry(root, textvariable=duration_var, width=10)
    duration_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

    tk.Label(root, text="Method:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
    tk.Radiobutton(root, text="sounddevice", variable=method_var, value="sounddevice").grid(row=2, column=1, sticky="w")
    tk.Radiobutton(root, text="ffmpeg", variable=method_var, value="ffmpeg").grid(row=2, column=1, padx=120, sticky="w")

    sd_recorder = SoundDeviceRecorder()
    ff_recorder = FFmpegRecorder()

    def start_recording():
        filename = ensure_wav_extension(file_var.get().strip())
        file_var.set(filename)
        method = method_var.get()
        if method == "sounddevice":
            sd_recorder.start(filename)
        else:
            dur = duration_var.get().strip()
            try:
                duration = int(dur) if dur else None
            except ValueError:
                messagebox.showerror("Invalid duration", "Duration must be an integer")
                return
            ff_recorder.start(filename, duration)
        start_btn.config(state=tk.DISABLED)
        stop_btn.config(state=tk.NORMAL)

    def stop_recording():
        if method_var.get() == "sounddevice":
            sd_recorder.stop()
        else:
            ff_recorder.stop()
        start_btn.config(state=tk.NORMAL)
        stop_btn.config(state=tk.DISABLED)

    start_btn = tk.Button(root, text="Start Recording", command=start_recording)
    start_btn.grid(row=3, column=0, padx=5, pady=5)
    stop_btn = tk.Button(root, text="Stop Recording", state=tk.DISABLED, command=stop_recording)
    stop_btn.grid(row=3, column=1, padx=5, pady=5)

    def on_close():
        stop_recording()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()


if __name__ == "__main__":
    main()
