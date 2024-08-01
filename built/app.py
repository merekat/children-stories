from flask import Flask, Response, send_from_directory
import torch
from TTS.api import TTS
import os
import re
from flask_cors import CORS
import json

# Adjust the static_folder to point to the correct location
app = Flask(__name__, static_url_path='/built/static', static_folder='static')
CORS(app, resources={r"/*": {"origins": "http://localhost:5500"}})

app.config['DEBUG'] = False

# Define user, language, and title
USER = 'test'.lower().replace(' ', '_')
LANGUAGE = 'en'.lower().replace(' ', '_')
TITLE = 'Androcles and the Lion'.lower().replace(' ', '_')

# Initialize TTS with the XTTS v2 model
device = "cuda" if torch.cuda.is_available() else "cpu"
model = 'tts_models/multilingual/multi-dataset/xtts_v2'
tts = TTS(model).to(device)

# Load user-specific model or fall back to standard model
user_model_path = os.path.join('model', f'{USER}.pth')
standard_model_path = os.path.join('model', 'standard.pth')

if os.path.exists(user_model_path):
    tts.load_state_dict(torch.load(user_model_path))
    print(f"Loaded user-specific model: {user_model_path}")
elif os.path.exists(standard_model_path):
    tts.load_state_dict(torch.load(standard_model_path))
    print(f"Loaded standard model: {standard_model_path}")
else:
    raise FileNotFoundError(f"Neither user-specific model '{user_model_path}' nor standard model '{standard_model_path}' found.")

# Ensure the static/audio directory exists
os.makedirs(os.path.join('static', 'audio'), exist_ok=True)

# The input file that I recorded
AUDIO_INPUT = os.path.join('audio', f'{USER}.wav')

# Check if the input audio file exists
if not os.path.exists(AUDIO_INPUT):
    raise FileNotFoundError(f"Input audio file '{AUDIO_INPUT}' not found.")

# Generated text
TEXT = "Nearly a thousand years ago, an enslaved storyteller named Aesop became famous for marvelous fables and stories he created, and perhaps the most beloved of his tale is, 'Androcles and the Lion.' In the story Androcles, also a slave, suffered terribly at the hands of one of the cruelest masters in all of Rome. No wonder that at the first chance he got, Androcles ran away. Bolting straight into the woods, he ran further and further until, exhausted, he could not move another step. Two days went by, and Androcles could find no food or water anywhere. 'I picked the wrong time of the year to run away!' Androcles despaired."

def split_text(text, max_chars=250, max_sentences=5):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current_chunk = []
    current_char_count = 0
    for sentence in sentences:
        if len(current_chunk) < max_sentences and current_char_count + len(sentence) <= max_chars:
            current_chunk.append(sentence)
            current_char_count += len(sentence)
        else:
            if current_chunk:
                chunks.append(' '.join(current_chunk))
            current_chunk = [sentence]
            current_char_count = len(sentence)
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    return chunks

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/process', methods=['GET'])
def process_text():
    def generate():
        text_chunks = split_text(TEXT)
        for i, chunk in enumerate(text_chunks):
            audio_filename = f"{USER}_{LANGUAGE}_{TITLE}_{i+1}.wav"
            audio_path = os.path.join('static', 'audio', audio_filename)

            # Generate audio file
            tts.tts_to_file(text=chunk,
                            speaker_wav=AUDIO_INPUT,
                            language=LANGUAGE,
                            file_path=audio_path)

            result = {
                'text': chunk,
                'audio': f"/built/static/audio/{audio_filename}"
            }

            yield f"data: {json.dumps(result)}\n\n"

        # Signal completion
        yield "event: complete\ndata: {}\n\n"  # Custom event to indicate completion

    return Response(generate(), mimetype='text/event-stream')

@app.route('/built/static/audio/<path:filename>')
def serve_audio(filename):
    return send_from_directory('static/audio', filename)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)