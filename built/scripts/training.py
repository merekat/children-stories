from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import io
import torch
from TTS.api import TTS
from TTS.utils.manage import ModelManager
import logging
from threading import Thread
import json
from pydub import AudioSegment
import subprocess

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

logging.basicConfig(level=logging.DEBUG)

def update_speaker_config(speaker):
    config_path = os.path.join(app.root_path, '..', 'config', 'speaker.json')
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
    else:
        config = {"speakers": []}

    if speaker not in config["speakers"]:
        config["speakers"].append(speaker)

    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

    logging.debug(f"Updated speaker.json with user: {speaker}")
    logging.debug(f"Current speaker.json content: {json.dumps(config, indent=2)}")

@app.route('/save-audio', methods=['POST'])
def save_audio():
    try:
        if 'audio' not in request.files:
            return jsonify({'success': False, 'error': 'No audio file'}), 400
        
        audio_file = request.files['audio']
        speaker = request.form.get('speaker', 'unknown_user')
        
        if not speaker:
            return jsonify({'success': False, 'error': 'Invalid speaker'}), 400

        audio_dir = os.path.join(app.root_path, '..', 'audio')
        os.makedirs(audio_dir, exist_ok=True)
        audio_path = os.path.join(audio_dir, f'{speaker}.wav')
        
        logging.debug(f"Attempting to save audio to: {audio_path}")
        
        # Save the raw audio data
        audio_file.save(audio_path)
        
        # Use FFmpeg to convert the audio to a valid WAV format
        try:
            ffmpeg_command = [
                'ffmpeg',
                '-i', audio_path,
                '-acodec', 'pcm_s16le',
                '-ar', '44100',
                '-ac', '2',
                '-y',  # Overwrite output file if it exists
                f'{audio_path}.converted.wav'
            ]
            result = subprocess.run(ffmpeg_command, capture_output=True, text=True)
            if result.returncode != 0:
                logging.error(f"FFmpeg error: {result.stderr}")
                return jsonify({'success': False, 'error': f'Error converting audio: {result.stderr}'}), 500
            
            # Replace the original file with the converted one
            os.replace(f'{audio_path}.converted.wav', audio_path)
        except Exception as e:
            logging.error(f"Error running FFmpeg: {e}", exc_info=True)
            return jsonify({'success': False, 'error': f'Error converting audio: {e}'}), 500

        file_size = os.path.getsize(audio_path)
        logging.debug(f"Audio saved and converted successfully! File size: {file_size} bytes")
        
        # Check if the file is not empty
        if file_size == 0:
            os.remove(audio_path)
            return jsonify({'success': False, 'error': 'Saved audio file is empty'}), 400
        
        # Update speaker.json
        update_speaker_config(speaker)
        
        return jsonify({'success': True, 'message': f'Audio saved as {audio_path}'})
    
    except Exception as e:
        logging.error(f"Error saving audio: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

def train_model_task(speaker):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    os.environ["COQUI_TOS_AGREED"] = "1"

    manager = ModelManager()
    model = 'tts_models/multilingual/multi-dataset/xtts_v2'
    manager.download_model(model)

    tts = TTS(model).to(device)

    audio_path = os.path.join(app.root_path, '..', 'audio', f'{speaker}.wav')
    logging.debug(f"Training model with audio: {audio_path}")

    try:
        # Add your training code here
        # Example: tts.train(audio_path)

        model_dir = os.path.join(app.root_path, '..', 'model')
        os.makedirs(model_dir, exist_ok=True)
        model_path = os.path.join(model_dir, f'{speaker}.pth')
        logging.debug(f"Saving model to: {model_path}")
        torch.save(tts.state_dict(), model_path)
        logging.debug("Model saved successfully!")

        # Update speaker.json
        update_speaker_config(speaker)

    except Exception as e:
        logging.error(f"Error during training or saving model: {e}", exc_info=True)

@app.route('/train-model', methods=['POST'])
def train_model():
    try:
        data = request.json
        if not data:
            return jsonify({'success': False, 'error': 'No JSON data provided'}), 400
        
        speaker = data.get('speaker')
        if not speaker:
            return jsonify({'success': False, 'error': 'No speaker provided'}), 400

        Thread(target=train_model_task, args=(speaker,)).start()
        return jsonify({'success': True, 'message': 'Model training started'})
    except Exception as e:
        logging.error(f"Error in train_model: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/test', methods=['GET'])
def test():
    return jsonify({'message': 'Test successful'})

@app.errorhandler(Exception)
def handle_exception(e):
    logging.error(f"Unhandled exception: {str(e)}", exc_info=True)
    return jsonify({'success': False, 'error': 'An unexpected error occurred'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001, use_reloader=False, threaded=False)