from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import torch
from TTS.api import TTS
from TTS.utils.manage import ModelManager
import logging
from threading import Thread

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

logging.basicConfig(level=logging.DEBUG)

@app.route('/save-audio', methods=['POST'])
def save_audio():
    if 'audio' not in request.files:
        return jsonify({'success': False, 'error': 'No audio file'}), 400
    
    audio_file = request.files['audio']
    username = os.path.splitext(audio_file.filename)[0]
    
    if not username:
        return jsonify({'success': False, 'error': 'Invalid filename'}), 400

    audio_dir = os.path.join('built', 'audio')
    os.makedirs(audio_dir, exist_ok=True)
    audio_path = os.path.join(audio_dir, f'{username}.wav')
    logging.debug(f"Saving audio to: {audio_path}")
    try:
        audio_file.save(audio_path)
        file_size = os.path.getsize(audio_path)
        logging.debug(f"Audio saved successfully! File size: {file_size} bytes")
        
        # Check if the file is not empty
        if file_size == 0:
            os.remove(audio_path)
            return jsonify({'success': False, 'error': 'Saved audio file is empty'}), 400
        
    except Exception as e:
        logging.error(f"Error saving audio: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

    return jsonify({'success': True})

def train_model_task(username):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    os.environ["COQUI_TOS_AGREED"] = "1"

    manager = ModelManager()
    model = 'tts_models/multilingual/multi-dataset/xtts_v2'
    manager.download_model(model)

    tts = TTS(model).to(device)

    audio_path = os.path.join('built', 'audio', f'{username}.wav')
    logging.debug(f"Training model with audio: {audio_path}")

    try:
        # Add your training code here
        # Example: tts.train(audio_path)

        model_dir = os.path.join('built', 'model')
        os.makedirs(model_dir, exist_ok=True)
        model_path = os.path.join(model_dir, f'{username}.pth')
        logging.debug(f"Saving model to: {model_path}")
        torch.save(tts.state_dict(), model_path)
        logging.debug("Model saved successfully!")
    except Exception as e:
        logging.error(f"Error during training or saving model: {e}", exc_info=True)

@app.route('/train-model', methods=['POST'])
def train_model():
    data = request.json
    username = data.get('username')

    if not username:
        return jsonify({'success': False, 'error': 'No username provided'}), 400

    Thread(target=train_model_task, args=(username,)).start()

    return jsonify({'success': True, 'message': 'Model training started'})

@app.route('/test', methods=['GET'])
def test():
    return jsonify({'message': 'Test successful'})

@app.errorhandler(Exception)
def handle_exception(e):
    logging.error(f"Unhandled exception: {str(e)}", exc_info=True)
    return jsonify({'success': False, 'error': 'An unexpected error occurred'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001, use_reloader=False, threaded=False)