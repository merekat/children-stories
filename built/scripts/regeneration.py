import sys
import os
import torch
from TTS.api import TTS
import json

def generate_audio_for_speaker(speaker, language, title, text):
    # Initialize TTS with the XTTS v2 model
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model_name = 'tts_models/multilingual/multi-dataset/xtts_v2'

    # Initialize the TTS model with the pre-trained XTTS v2
    tts = TTS(model_name).to(device)

    # Load speaker-specific model
    speaker_model_path = os.path.join(os.path.dirname(__file__), '..', 'model', f'{speaker}.pth')
    if os.path.exists(speaker_model_path):
        try:
            tts.load_model_weights(speaker_model_path)
            print(f"Loaded speaker-specific weights: {speaker_model_path}")
        except Exception as e:
            print(f"Failed to load speaker-specific weights: {e}")
            return False

    # Generate audio files
    chunks = text.split('. ')
    audio_files = []
    for i, chunk in enumerate(chunks):
        audio_filename = f"{speaker}_{language}_{title}_{i+1}.wav"
        audio_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'audio', audio_filename)

        tts.tts_to_file(text=chunk,
                        speaker_wav=os.path.join(os.path.dirname(__file__), '..', 'audio', f'{speaker}.wav'),
                        language=language,
                        file_path=audio_path)

        audio_files.append(f"/built/static/audio/{audio_filename}")

    # Update story.json
    story_json_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'story.json')
    if os.path.exists(story_json_path):
        with open(story_json_path, 'r') as f:
            story_data = json.load(f)
    else:
        story_data = []

    new_entry = {
        "title": title,
        "speaker": speaker,
        "language": language
    }
    story_data.append(new_entry)

    with open(story_json_path, 'w') as f:
        json.dump(story_data, f, indent=2)

    return True

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python regeneration.py <speaker> <language> <title> <text>", file=sys.stderr)
        sys.exit(1)

    speaker, language, title, text = sys.argv[1:]
    try:
        success = generate_audio_for_speaker(speaker, language, title, text)
        if success:
            print("Audio generation completed successfully")
            sys.exit(0)
        else:
            print("Audio generation failed", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"Error during audio generation: {str(e)}", file=sys.stderr)
        sys.exit(1)