# WinSoundCapture

Questo progetto consente di registrare l'audio di sistema su Windows.
Il nuovo script `winsound_gui.py` combina le logiche presenti nei file
`main.py`, `ffmpeg_recorder.py` e `record_gui.py` e offre una semplice
interfaccia grafica per avviare e interrompere la registrazione.

## Requisiti
- Python 3.10+
- Le dipendenze elencate in `requirements.txt`
- (Opzionale) `ffmpeg` installato e disponibile nel `PATH` se si desidera
  utilizzare il metodo di registrazione tramite ffmpeg.

## Utilizzo
Eseguire il seguente comando dal terminale:

```bash
python winsound_gui.py
```

L'interfaccia permette di:
- scegliere il file di uscita (verrà forzata l'estensione `.wav`),
- selezionare il metodo di registrazione (`sounddevice` o `ffmpeg`),
- (per ffmpeg) specificare la durata in secondi,
- avviare e fermare la registrazione tramite i pulsanti dedicati.

Eventuali errori verranno mostrati a video tramite finestre di dialogo.
