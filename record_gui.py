import datetime
import queue
import threading

import PySimpleGUI as sg
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
                    extra_settings=sd.WasapiSettings(loopback=True),
                ):
                    while self.recording:
                        file.write(self.q.get())
            except Exception as e:
                sg.popup_error(f"Error during recording:\n{e}")

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
    sg.theme("DarkBlue")
    layout = [
        [
            sg.Text("Output file:"),
            sg.InputText("output.wav", key="FILE"),
            sg.FileSaveAs(file_types=(("WAV", "*.wav"),)),
        ],
        [
            sg.Button("Start Recording", key="-START-"),
            sg.Button("Stop Recording", key="-STOP-", disabled=True),
        ],
    ]
    window = sg.Window("WinSoundCapture", layout)

    recorder = Recorder()

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        elif event == "-START-":
            filename = values["FILE"]
            if not filename:
                filename = f"recording_{datetime.datetime.now():%Y%m%d_%H%M%S}.wav"
            recorder.start(filename)
            window["-START-"].update(disabled=True)
            window["-STOP-"].update(disabled=False)
        elif event == "-STOP-":
            recorder.stop()
            window["-START-"].update(disabled=False)
            window["-STOP-"].update(disabled=True)

    recorder.stop()
    window.close()


if __name__ == "__main__":
    main()
