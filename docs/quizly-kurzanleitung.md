# Quizly Kurzanleitung

Quelle: `C:\Users\Anwender\Desktop\Kurzanleitung Quizly.pdf`

Diese Notizen fassen die wichtigsten Projektvoraussetzungen aus der Kurzanleitung zusammen.

## Systemvoraussetzung: FFmpeg

Quizly benötigt FFmpeg für die Verarbeitung von Audio-/Videodaten.

### Windows: Installation per Download

1. Ein aktuelles FFmpeg-Build herunterladen: <https://ffmpeg.org/download.html>
2. Windows-Build wählen, zum Beispiel von `gyan.dev` oder `BtbN`.
3. ZIP-Datei entpacken, zum Beispiel nach `C:\ffmpeg`.
4. Im Ordner `bin` liegt `ffmpeg.exe`.
5. Den Pfad `C:\ffmpeg\bin` zu den Windows-Umgebungsvariablen hinzufügen:
   - Rechtsklick auf "Dieser PC"
   - "Eigenschaften"
   - "Erweiterte Systemeinstellungen"
   - "Umgebungsvariablen..."
   - In `Path` den Eintrag `C:\ffmpeg\bin` ergänzen

### Windows: Installation per Terminal

```powershell
winget install --id Gyan.FFmpeg -e --source winget
```

### macOS

Homebrew installieren, falls noch nicht vorhanden:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

FFmpeg installieren:

```bash
brew install ffmpeg
```

## Python-/API-Abhängigkeiten für Quiz-Erstellung

Diese Komponenten werden für den Workflow benötigt, der aus einem YouTube-Video ein Quiz erzeugt.

### Whisper AI

Repository: <https://github.com/openai/whisper>

Whisper wird genutzt, um Audio in Text umzuwandeln. Das ist nötig, weil die kostenlose Gemini API Text als Eingabe verarbeitet.

### yt-dlp

Repository: <https://github.com/yt-dlp/yt-dlp>

yt-dlp wird für das Herunterladen von YouTube-Videos empfohlen. Vorteil: Das Video kann direkt als Audiodatei heruntergeladen werden.

### Gemini API

API-Key: <https://ai.google.dev/>

Dokumentation: <https://ai.google.dev/gemini-api/docs/libraries?hl=de>

Für die KI-basierte Erstellung des Quizzes wird ein Gemini API-Key benötigt.

## Umsetzungsliste

- [ ] FFmpeg als externe Systemvoraussetzung dokumentieren
- [ ] Runtime-/Worker-Strategie für Video-Download festlegen
- [ ] `yt-dlp` als Python-Abhängigkeit ergänzen, sobald der Download-Workflow implementiert wird
- [ ] Whisper-Integration planen und Paket/Runtime-Anforderungen klären
- [ ] Gemini API-Key als Environment Variable definieren
- [ ] Gemini-Client erst ergänzen, wenn der Quiz-Generierungsservice umgesetzt wird
- [ ] Tests für Video-URL-Verarbeitung, Audio-Extraktion und Quiz-Generierung planen
