import os
import base64
from dotenv import load_dotenv
from openai import OpenAI
from pathlib import Path

# Load environment variables
load_dotenv(Path(__file__).parent / ".env")
api_key = os.getenv("KIT_API_KEY")
base_url = "https://ki-toolbox.scc.kit.edu/api/v1"

# Initialize client
client = OpenAI(api_key=api_key, base_url=base_url)


def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


# Prepare the image
image_path = "test1.png"
b64_image = encode_image_to_base64(image_path)

system_prompt = """
You are an expert puzzle analyzer. Extract the structure of a "Zip" puzzle from the provided image and output it strictly as a JSON object matching the schema below.

{
  "boardSize": <Integer, edge length of the square grid>,
  "waypoints": [
    [x, y]
  ],
  "walls": [
    {
      "neighborA": [x, y],
      "neighborB": [x, y]
    }
  ],
  "solutionPath": []
}

Extraction Rules:
- Coordinate System: 0-based indexing. [0, 0] is the top-left cell. 'x' is the column index (left to right), and 'y' is the row index (top to bottom).
- boardSize: The total number of rows/columns in the grid (the grid is always square).
- waypoints: All numbered circles on the board, ordered sequentially by their number (1, 2, 3, ...). Format as [x, y].
- walls: Every visible wall separating two adjacent cells. For each wall, provide the coordinates of the two cells it separates as `neighborA` and `neighborB`.
- solutionPath: Always leave this as an empty array [].

Important:
- Output ONLY valid JSON. Do not wrap the output in Markdown code blocks.
- Do not include any explanations, prefaces, or comments.
- Verify that all coordinates are within the range 0 to boardSize - 1.
"""

try:
    # IMPORTANT: Change this to a vision-capable model on your API
    # e.g., "kit.gpt-4o" or a DeepSeek-VL variant
    model_name = "kit.mistral-small-4"

    chat_completion = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Extract the puzzle structure from this image."
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{b64_image}"}
                    },
                ],
            },
        ],
        temperature=0.1  # Low temperature for more deterministic JSON output
    )

    # Output the result
    print(chat_completion.choices[0].message.content)

except Exception as e:
    print(f"Error: {e}")
