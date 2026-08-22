import os
from dotenv import load_dotenv
from openai import OpenAI
from pathlib import Path
import base64

json_blueprint = """
{
  "boardSize": 6/7/8,
  "waypoints": [
    [x, y]
    [x, y], 
    ...
  ],
  "walls": [
    {
      "neighborA": [x, y],
      "neighborB": [x, y]
    }
  ],
  "solutionPath": []
}
"""


load_dotenv(Path(__file__).parent / ".env")

api_key = os.getenv("KIT_API_KEY")
base_url = "https://ki-toolbox.scc.kit.edu/api/v1"
client = OpenAI(api_key=api_key, base_url=base_url)

with open("test1.png", "rb") as image_file:
    b64_image = base64.b64encode(image_file.read()).decode("utf-8")

try:
    chat_completion = client.chat.completions.create(
        model="kit.mistral-small-4-119b-a8b",
        messages=[
            {"role": "system", "content": """
            Du erhältst ein Bild eines "Zip"-Puzzles (LinkedIn Zip). Analysiere das Bild und extrahiere die Puzzle-Struktur ausschließlich als JSON, das exakt dem folgenden Schema entspricht:

{
  "boardSize": <Integer, Kantenlänge des quadratischen Spielfelds>,
  "waypoints": [
    [x, y],
    ...
  ],
  "walls": [
    {
      "neighborA": [x, y],
      "neighborB": [x, y]
    },
    ...
  ],
  "solutionPath": []
}

Regeln zur Extraktion:
- boardSize: Anzahl der Zeilen/Spalten des Gitters (quadratisch).
- waypoints: Alle nummerierten Kreise auf dem Feld, in der Reihenfolge ihrer Nummerierung (1, 2, 3, ...), als [x, y] mit 0-basierter Indizierung.
- walls: Jede im Bild sichtbare Wand zwischen zwei benachbarten Zellen. Gib pro Wand die beiden angrenzenden Zellen als neighborA und neighborB an (0-basiert, x/y).
- solutionPath: Falls im Bild ein Lösungspfad eingezeichnet ist, gib ihn als geordnete Liste aller durchlaufenen Zellen an. Ist kein Lösungspfad sichtbar, setze solutionPath auf ein leeres Array [].

Wichtig:
- Gib ausschließlich valides JSON zurück, ohne Markdown-Codeblock, ohne Erklärtext, ohne zusätzliche Kommentare.
- Halte dich strikt an die oben genannten Feldnamen und die Koordinatenreihenfolge [x, y].
- Prüfe vor der Ausgabe, dass alle Koordinaten innerhalb von 0 bis boardSize-1 liegen.
- Lasse solution Path immer leer
            """},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{b64_image}"}
                    },
                ],
            },
        ],
    )
    # Antwort ausgeben
    print(chat_completion.choices[0].message.content)
except Exception as e:
    print(f"Fehler: {e}")