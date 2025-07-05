import datetime
import queue
import threading

import tkinter as tk
from tkinter import filedialog, messagebox
import sounddevice as sd
import soundfile as sf


class Recorder:
    def __init__(self):
        self.q = queue.Queue()
        self.fs = 44100
        self.channels = 2
        self.recording = False
        self.thread = None

    def _callback(self, indata, frames, time, status):
        if status:
            print(status)
        self.q.put(indata.copy())

    def _record(self, filename):
        with sf.SoundFile(filename, mode="w", samplerate=self.fs, channels=self.channels) as file:
            try:
                with sd.InputStream(
                        samplerate=self.fs,
                        channels=self.channels,
                        dtype="float32",
                        callback=self._callback,
                        blocksize=1024,
                        device=self._get_loopback_device()
                ):
                    while self.recording:
                        file.write(self.q.get())
            except Exception as e:
                messagebox.showerror("Recording Error", str(e))

    def _get_loopback_device(self):
        for i, dev in enumerate(sd.query_devices()):
            if 'loopback' in dev['name'].lower():
                return i
        raise RuntimeError("Nessun dispositivo di loopback trovato.")

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


def main():
    root = tk.Tk()
    root.title("WinSoundCapture")

    file_var = tk.StringVar(value="output.wav")

    tk.Label(root, text="Output file:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    file_entry = tk.Entry(root, textvariable=file_var, width=40)
    file_entry.grid(row=0, column=1, padx=5, pady=5)

    def browse():
        filename = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV files", "*.wav")])
        if filename:
            file_var.set(filename)

    tk.Button(root, text="Browse", command=browse).grid(row=0, column=2, padx=5, pady=5)

    recorder = Recorder()

    def start_recording():
        filename = file_var.get().strip()
        if not filename:
            filename = f"recording_{datetime.datetime.now():%Y%m%d_%H%M%S}.wav"
            file_var.set(filename)
        recorder.start(filename)
        start_btn.config(state=tk.DISABLED)
        stop_btn.config(state=tk.NORMAL)

    def stop_recording():
        recorder.stop()
        start_btn.config(state=tk.NORMAL)
        stop_btn.config(state=tk.DISABLED)

    start_btn = tk.Button(root, text="Start Recording", command=start_recording)
    start_btn.grid(row=1, column=0, padx=5, pady=5)
    stop_btn = tk.Button(root, text="Stop Recording", state=tk.DISABLED, command=stop_recording)
    stop_btn.grid(row=1, column=1, padx=5, pady=5)

    def on_close():
        recorder.stop()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()


if __name__ == "__main__":
    main()