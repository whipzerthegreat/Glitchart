#!/usr/bin/env python3
"""
Glitch-Art Batch Processor für MP4-Dateien
Bearbeitet alle .mp4 Dateien im Ordner 'input' und speichert Ergebnisse in 'output'
"""

import os
import subprocess
import sys
import json
from pathlib import Path


def get_video_codec(file_path: str) -> str | None:
    """Ermittelt den Video-Codec einer Datei mit ffprobe"""
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "quiet",
                "-print_format", "json",
                "-show_streams",
                str(file_path)
            ],
            capture_output=True,
            text=True,
            check=True
        )
        data = json.loads(result.stdout)
        
        for stream in data.get("streams", []):
            if stream.get("codec_type") == "video":
                return stream.get("codec_name")  # z.B. "h264", "hevc", "vp9"...
        
        return None
    except Exception as e:
        print(f"Fehler beim Auslesen von {file_path}: {e}")
        return None


def process_video(input_file: Path, output_dir: Path) -> None:
    """Verarbeitet eine einzelne Videodatei"""
    base_name = input_file.stem
    corrupted_temp = output_dir / f"{base_name}_corrupted.mp4"
    final_output = output_dir / f"{base_name}_glitch.mp4"

    # Schritt 1: Codec prüfen
    codec = get_video_codec(str(input_file))
    if codec is None:
        print(f"Fehler {input_file.name} Kein Video-Stream gefunden")
        return
    
    if codec.lower() != "h264":
        print(f"Fehler {input_file.name} Codec ist {codec!r} (nur h264 erlaubt)")
        return

    print(f"-> Bearbeite: {input_file.name} (h264)")

    # Schritt 2: Korruption mit Noise in Non-Keyframes
    corrupt_cmd = [
        "ffmpeg", "-y",
        "-i", str(input_file),
        "-c:v", "libx264",
        "-x264-params", "keyint=500:keyint_min=60:bf=8:partitions=none", # keyint ändert die Keyframes, bf 0-8 =nachzieheffekte
        "-bsf:v", "noise=amount=9000*not(key)", # noise = amount der Zerfickung
        "-pix_fmt", "yuv420p",
        str(corrupted_temp)
    ]

    try:
        subprocess.run(corrupt_cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Fehler: Korruptions-Schritt fehlgeschlagen bei {input_file.name}")
        print(f"   Fehler: {e}")
        if corrupted_temp.exists():
            corrupted_temp.unlink()
        return

    # Schritt 3: Re-Encoding -> abspielbar machen
    reencode_cmd = [
        "ffmpeg", "-y",
        "-i", str(corrupted_temp),
        "-c:v", "libx264",
        "-preset", "veryslow",       # machst du slow für schlechtere Qualität 
        "-crf", "28",              # Qualität ~ 18–28, machst du 23 für gute Kompromiss
        str(final_output)
    ]

    try:
        subprocess.run(reencode_cmd, check=True)
        print(f"Fertig: {final_output.name}")
        
        # Temporäre Datei aufräumen
        if corrupted_temp.exists():
            corrupted_temp.unlink()
            
    except subprocess.CalledProcessError as e:
        print(f"Fehler: Re-Encoding fehlgeschlagen bei {input_file.name}")
        print(f"   Fehler: {e}")
        if final_output.exists():
            final_output.unlink()


def main() -> None:
    input_dir = Path("input")
    output_dir = Path("output")

    if not input_dir.is_dir():
        print("Fehler: Ordner 'input' existiert nicht!")
        sys.exit(1)

    output_dir.mkdir(exist_ok=True)

    print("=== Glitch-Art Batch Processor ===\n")

    mp4_files = list(input_dir.glob("*.mp4"))
    if not mp4_files:
        print("Keine .mp4 Dateien im Ordner 'input' gefunden.")
        return

    print(f"Gefunden: {len(mp4_files)} MP4-Datei(en)\n")

    for idx, video_path in enumerate(mp4_files, 1):
        print(f"[{idx}/{len(mp4_files)}]")
        process_video(video_path, output_dir)
        print()

    print("=== Fertig ===")


if __name__ == "__main__":
    main()