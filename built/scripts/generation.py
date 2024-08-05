from flask import Flask, Response, send_from_directory, request, jsonify
import torch
from TTS.api import TTS
import os
import re
from flask_cors import CORS
import json
import html
import sys
import chevron  
import subprocess

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Initialize Flask app
app = Flask(__name__, static_url_path='/built', static_folder=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CORS(app, resources={r"/*": {"origins": "*"}}) 

app.config['DEBUG'] = False

# Define speaker, language, and title
SPEAKER = ''.lower().replace(' ', '_')
LANGUAGE = 'en'.lower().replace(' ', '_')
TITLE = 'Androcles and the Lion'.lower().replace(' ', '_')

# Generated text
TEXT = "Once upon a time, in a small village nestled at the edge of a dense and mysterious forest, there lived a little girl named Lily. The villagers called her 'Forest Child' because she spent most of her days exploring the woods, collecting wildflowers, and watching the animals that roamed freely within its boundaries."

# Initialize TTS with the XTTS v2 model
device = "cuda" if torch.cuda.is_available() else "cpu"
model_name = 'tts_models/multilingual/multi-dataset/xtts_v2'

# Initialize the TTS model with the pre-trained XTTS v2
tts = TTS(model_name).to(device)

# Load speaker-specific model or fall back to standard model
speaker_model_path = os.path.join(app.root_path, '..', 'model', f'{SPEAKER}.pth')
standard_model_path = os.path.join(app.root_path, '..', 'model', 'standard.pth')

if os.path.exists(speaker_model_path):
    try:
        tts.load_model_weights(speaker_model_path)
        print(f"Loaded speaker-specific weights: {speaker_model_path}")
    except Exception as e:
        print(f"Failed to load speaker-specific weights: {e}")
elif os.path.exists(standard_model_path):
    try:
        tts.load_model_weights(standard_model_path)
        print(f"Loaded standard weights: {standard_model_path}")
    except Exception as e:
        print(f"Failed to load standard weights: {e}")
else:
    print(f"Using the default XTTS model weights.")

# Ensure the necessary directories exist
os.makedirs(os.path.join(app.root_path, '..', 'static', 'audio'), exist_ok=True)
os.makedirs(os.path.join(app.root_path, '..', 'config'), exist_ok=True)
os.makedirs(os.path.join(app.root_path, '..', 'static', 'story'), exist_ok=True)
os.makedirs(os.path.join(app.root_path, '..', 'model'), exist_ok=True)

@app.route('/speaker')
def speaker():
    config_path = os.path.join(app.root_path, '..', 'config', 'speaker.json')
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
        return jsonify(config)
    else:
        return jsonify({"speakers": []})

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

def generate_story_html(title, chunks, audio_files, language):
    template_path = os.path.join(app.root_path, '..', 'template', 'template.html')
    
    with open(template_path, 'r', encoding='utf-8') as template_file:
        template = template_file.read()
    
    data = {
        'title': html.escape(title),
        'chunks': [
            {'text': html.escape(chunk), 'audio': audio_file, 'index': i + 1}
            for i, (chunk, audio_file) in enumerate(zip(chunks, audio_files))
        ],
        'story_json_path': '../../config/story.json',
        'language': language
    }
    
    return chevron.render(template, data)

@app.route('/')
def index():
    return send_from_directory(os.path.dirname(os.path.dirname(app.root_path)), 'index.html')

@app.route('/process')
def process_text():
    speaker = request.args.get('speaker', default='', type=str)

    def generate():
        text_chunks = split_text(TEXT)
        audio_files = []
        for i, chunk in enumerate(text_chunks):
            audio_filename = f"{speaker}_{LANGUAGE}_{TITLE}_{i+1}.wav" if speaker else f"{LANGUAGE}_{TITLE}_{i+1}.wav"
            audio_path = os.path.join(app.root_path, '..', 'static', 'audio', audio_filename)

            # Generate audio file
            speaker_wav = os.path.join(app.root_path, '..', 'audio', f'{speaker}.wav') if speaker else None
            tts.tts_to_file(text=chunk,
                            speaker_wav=speaker_wav,
                            language=LANGUAGE,
                            file_path=audio_path)

            audio_url = f"/built/static/audio/{audio_filename}"
            audio_files.append(audio_url)

            result = {
                'text': chunk,
                'audio': audio_url
            }

            yield f"data: {json.dumps(result)}\n\n"

        # Update story JSON file
        story_json_path = os.path.join(app.root_path, '..', 'config', 'story.json')
        story = {
            "title": TITLE,
            "speaker": speaker if speaker else "default",
            "language": LANGUAGE
        }

        # Read existing data
        existing_data = []
        if os.path.exists(story_json_path):
            with open(story_json_path, 'r') as f:
                try:
                    existing_data = json.load(f)
                except json.JSONDecodeError:
                    print("Error reading existing JSON. Starting with empty list.")

        # Ensure existing_data is a list
        if not isinstance(existing_data, list):
            existing_data = []

        # Add new entry
        existing_data.append(story)

        # Write updated data back to file
        with open(story_json_path, 'w') as f:
            json.dump(existing_data, f, indent=2)

        # Generate story HTML file
        story_html = generate_story_html(TITLE.replace('_', ' ').title(), text_chunks, audio_files, LANGUAGE)
        story_html_path = os.path.join(app.root_path, '..', 'static', 'story', f"{TITLE}.html")
        with open(story_html_path, 'w', encoding='utf-8') as f:
            f.write(story_html)

        print(f"HTML file created at: {story_html_path}")

        # Signal completion
        yield "event: complete\ndata: {}\n\n"

    return Response(generate(), mimetype='text/event-stream')

@app.route('/generate_audio', methods=['POST'])
def generate_audio():
    try:
        data = request.json
        speaker = data['speaker']
        language = data['language']
        title = data['title']
        text = data['text']

        # Correct path construction
        script_path = os.path.join(os.path.dirname(__file__), 'regeneration.py')
        script_path = os.path.abspath(script_path)
        
        print(f"Attempting to run script at: {script_path}")  # Debug print

        result = subprocess.run([sys.executable, script_path, speaker, language, title, text], 
                                capture_output=True, text=True)

        if result.returncode == 0:
            return jsonify({"success": True, "message": "Audio generated successfully"}), 200
        else:
            return jsonify({"success": False, "message": f"Error in regeneration.py: {result.stderr}"}), 500
    except Exception as e:
        app.logger.error(f"Error in generate_audio: {str(e)}")
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500

@app.route('/built/static/audio/<path:filename>')
def serve_audio(filename):
    return send_from_directory(os.path.join(app.root_path, '..', 'static', 'audio'), filename)

@app.route('/built/static/story/<path:filename>')
def serve_story(filename):
    return send_from_directory(os.path.join(app.root_path, '..', 'static', 'story'), filename)

@app.route('/built/config/<path:filename>')
def serve_config(filename):
    return send_from_directory(os.path.join(app.root_path, '..', 'config'), filename)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)