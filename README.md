# Glitch-Art Batch Processor (MP4 / H.264)

Ein kleines Python-Script zum **automatischen Glitchen von MP4-Videos**.  
Alle Videos im Ordner `input/` werden mit absichtlich kaputten Non-Keyframes versehen und als spielbare Glitch-Clips im Ordner `output/` gespeichert.

Das Ganze basiert auf **FFmpeg**, **ffprobe** und gezielter Codec-Korruption.

---

## Features

- Batch-Verarbeitung aller `.mp4` Dateien
- Prüft automatisch den Video-Codec
- **Nur H.264 erlaubt** (sonst Chaos oder gar nichts)
- Glitch-Effekt durch:
  - manipulierte Keyframe-Abstände
  - Noise-Injection in Non-Keyframes
  - B-Frames für Nachzieh-Artefakte
- Automatisches Re-Encoding und die Videos bleiben abspielbar
- Temporäre Dateien werden aufgeräumt

---

## Ordnerstruktur

```text
project/
├── glitch.py
├── input/
│   ├── video1.mp4
│   ├── video2.mp4
│   └── ...
└── output/
    ├── video1_glitch.mp4
    ├── video2_glitch.mp4
    └── ...
```

---

## Voraussetzungen

### Software
- **Python 3.10+**
- **FFmpeg** (inkl. `ffprobe`)

Prüfen ob FFmpeg installiert ist:
```bash
ffmpeg -version
ffprobe -version
```

Falls nicht:
- Linux: `sudo apt install ffmpeg`
- macOS nutzt eh keiner
- Windows: FFmpeg Build herunterladen und ins PATH legen

---

## Nutzung

1. Script ausführbar machen (optional):
```bash
chmod +x glitch.py
```

2. MP4-Dateien in den Ordner `input/` legen  
 **Wichtig:** Die Videos müssen **H.264** sein

3. Script starten:
```bash
python3 glitch.py
```

4. Fertige Glitch-Videos erscheinen in `output/`

---

## Codec-Regeln (wichtig!)

Das Script akzeptiert **ausschließlich H.264**:

erlaubt:
- h264

nicht erlaubt:
- hevc / h265 (bitte nicht!!!)
- vp9
- av1
- sonstiger Blödsinn

Nicht-H.264 Dateien werden übersprungen und gemeldet.

---

## Wie entsteht der Glitch?

Kurzfassung: **kontrollierte Zerstörung**.

### Schritt 1 – Analyse
- `ffprobe` liest den Video-Codec aus

### Schritt 2 – Korruption
- große Keyframe-Abstände
- Noise nur in **Non-Keyframes**
- viele B-Frames → Smearing / Ghosting
- Ziel: Datenmüll ohne Totalcrash

### Schritt 3 – Re-Encoding
- erneutes Encoden mit `libx264`
- macht das kaputte Video wieder abspielbar

---

## Parameter anpassen

Im Script kannst du brutal experimentieren:

```python

    noise_amount = 9000		# zB. 1000-9000 Intensität der Zerfickung
    x264params = [
        "keyint=500", 		# Resettet immer wieder das Ausgangsbild, damit es nicht zu sehr abkackt
        "keyint_min=60",
        "bf=8",				# z.B. 0-8 Nachzieheffekte, die Optik schmiert wie auf Pappe
        "partitions=none" 	# macht es etwas hübscher
    ]
    
    corrupt_cmd = [
        "ffmpeg", "-y",
        "-i", str(input_file),
        "-c:v", "libx264",
        "-x264-params",  ":".join(x264params), 
        "-bsf:v", f"noise=amount={noise_amount}*not(key)", 
        "-pix_fmt", "yuv420p",
        str(corrupted_temp)
    ]

```

Zu viel Zerfickung  = kaputte Datei  
Zu wenig Zerfickung = langweilige Datei

---

## Haftungsausschluss

- Dieses Script **zerstört absichtlich Videodaten**
- Nutze **Kopien**, niemals Originale aber ist auch nicht schlimm. Ist dann vielleicht weg.
- Ergebnisse sind nicht deterministisch
- Glitch-Art halt

---

## Warum?

Warum nicht?

![Meme mit Pizzajungen](https://c.tenor.com/14hr1KPxcCoAAAAd/tenor.gif)
