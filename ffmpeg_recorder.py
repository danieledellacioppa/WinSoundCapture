import argparse
import shutil
import subprocess
import sys


def find_ffmpeg() -> str:
    """Return the path to ffmpeg or raise an error."""
    path = shutil.which("ffmpeg")
    if not path:
        raise RuntimeError("ffmpeg not found. Please install it and ensure it's in PATH.")
    return path


def record(duration: int, output: str) -> None:
    """Record system audio using ffmpeg WASAPI."""
    ffmpeg = find_ffmpeg()
    cmd = [
        ffmpeg,
        "-y",  # overwrite existing file
        "-f", "wasapi",
        "-i", "default",
        "-acodec", "pcm_s16le",
        "-ar", "44100",
        "-ac", "2",
        "-t", str(duration),
        output,
    ]
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Record system audio using ffmpeg WASAPI")
    parser.add_argument("duration", type=int, help="Duration of the recording in seconds")
    parser.add_argument("output", nargs="?", default="output.wav", help="Output WAV file")
    args = parser.parse_args()
    try:
        record(args.duration, args.output)
    except Exception as exc:
        print("Error:", exc)
        sys.exit(1)

