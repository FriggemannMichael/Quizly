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

## Frontend Repository

Das gestellte Frontend liegt hier:

```text
git@github.com:Developer-Akademie-Backendkurs/project.Quizly.git
```

Das Backend muss die dokumentierten API-Endpunkte und Response-Formate passend zu diesem Frontend bereitstellen.

## Wichtige Implementierungsdetails

### yt-dlp Optionen

Für den YouTube-Audio-Download sollen diese Optionen verwendet werden:

```python
ydl_opts = {
    "format": "bestaudio/best",
    "outtmpl": tmp_filename,
    "quiet": True,
    "noplaylist": True,
}
```

Wichtig:

- Nur YouTube-Videos verarbeiten.
- Keine Playlists verarbeiten (`noplaylist=True`).
- Temporäre Dateinamen kontrolliert erzeugen und nach Verarbeitung aufräumen.

### Kanonische YouTube-URL speichern

Die gespeicherte Video-URL muss exakt in dieser Form aufgebaut werden:

```text
https://www.youtube.com/watch?v=ID-DES-VIDEOS
```

Dafür muss aus jeder akzeptierten YouTube-URL zuerst die Video-ID extrahiert werden. Danach wird die URL aus dieser ID neu zusammengesetzt. Nicht blind die eingereichte URL speichern, weil das Frontend eine einheitliche URL-Struktur erwartet.

### Gemini-Ausgabe bereinigen

Gemini kann die JSON-Antwort in Markdown-Codeblöcke einpacken, zum Beispiel:

````text
```json
{ ... }
```
````

oder:

````text
```
{ ... }
```
````

Vor dem Speichern und vor `json.loads` müssen solche Markdown-Fences entfernt werden. Die gespeicherten Quizdaten sollen aus validem JSON stammen, nicht aus rohem Markdown-Text.

### Gemini Prompt-Vorlage

Das Transkript muss am Ende des Prompts angefügt werden.

```text
Based on the following transcript, generate a quiz in valid JSON format.

The quiz must follow this exact structure:

{
  "title": "Create a concise quiz title based on the topic of the transcript.",
  "description": "Summarize the transcript in no more than 150 characters. Do not include any quiz questions or answers.",
  "questions": [
    {
      "question_title": "The question goes here.",
      "question_options": ["Option A", "Option B", "Option C", "Option D"],
      "answer": "The correct answer from the above options"
    },
    ...
    (exactly 10 questions)
  ]
}

Requirements:

- Each question must have exactly 4 distinct answer options.
- Only one correct answer is allowed per question, and it must be present in 'question_options'.
- The output must be valid JSON and parsable as-is (e.g., using Python's json.loads).
- Do not include explanations, comments, or any text outside the JSON.

Transcript:
{transcript}
```

## Ergänzte Umsetzungsliste

- [ ] Frontend-Repository lokal referenzieren und API-Kompatibilität prüfen
- [ ] YouTube-Video-ID robust aus verschiedenen URL-Formaten extrahieren
- [ ] Video-URL kanonisch als `https://www.youtube.com/watch?v=<video_id>` speichern
- [ ] yt-dlp mit den vorgegebenen Optionen kapseln
- [ ] Gemini-Prompt als zentrale Vorlage ablegen
- [ ] Markdown-Fences aus Gemini-Antworten entfernen
- [ ] Gemini-Antwort per `json.loads` validieren
- [ ] Prüfen, dass genau 10 Fragen entstehen
- [ ] Prüfen, dass jede Frage genau 4 unterschiedliche Optionen enthält
- [ ] Prüfen, dass `answer` in `question_options` enthalten ist
