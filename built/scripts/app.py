from flask import Flask, send_from_directory, request, jsonify, render_template
import torch
import html
from TTS.api import TTS
import os
import re
from flask_cors import CORS
import json
import logging
from llama_cpp import Llama
import warnings
import chevron
import random
from datetime import datetime
import wave
from pydub import AudioSegment
import multiprocessing
from diffusers import StableDiffusionXLPipeline, AutoencoderKL

print("GPU available:", torch.cuda.is_available())

warnings.filterwarnings("ignore", message="The attention mask is not set and cannot be inferred from input because pad token is same as eos token.")

# Initialize Flask app
app = Flask(__name__, static_url_path='/built', static_folder=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CORS(app, resources={r"/*": {"origins": "*"}})
app.config['DEBUG'] = True


# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Use Flask's logger
app.logger.setLevel(logging.DEBUG)

# Ensure the necessary directories exist
os.makedirs(os.path.join(app.root_path, '..', 'audio'), exist_ok=True)
os.makedirs(os.path.join(app.root_path, '..', 'config'), exist_ok=True)
os.makedirs(os.path.join(app.root_path, '..', 'model'), exist_ok=True)
os.makedirs(os.path.join(app.root_path, '..', 'static', 'audio'), exist_ok=True)
os.makedirs(os.path.join(app.root_path, '..', 'static', 'story'), exist_ok=True)
os.makedirs(os.path.join(app.root_path, '..', 'static', 'image'), exist_ok=True)


# Global variables to store the generated story and title
TITLE = ""
TEXT = ""
LANGUAGE = 'en'
pipe = None

children_story_topics = [
    "Wizards and Elephants", "Adventures in Magical Forest", "Talking Tree", "Brave Little Dragon",
    "Secret Garden", "Lost Treasure of Pirate Island", "Enchanted Castle", "Friendly Ghost",
    "Time-Traveling Kids", "Underwater Kingdom", "Flying Unicorn", "Mysterious Cave",
    "Little Robot's Big Adventure", "Animal Orchestra", "Magic Paintbrush",
    "Adventures of Space Explorer", "Fairy and Giant", "Secret of Old Lighthouse",
    "Jungle Expedition", "Snowy Mountain Rescue", "Little Mermaid's Wish",
    "Haunted House Mystery", "Adventures of Tiny Dinosaur", "Magic School Bus",
    "Lost City of Atlantis", "Friendly Alien", "Magical Bookstore", "Adventures of Superhero Kid",
    "Secret World of Insects", "Little Witch's Potion"
]

topic = "wizards and elephants" # FIX

LANGUAGE_CODES = {
    'English': 'en', 'Spanish': 'es', 'French': 'fr', 'German': 'de', 'Italian': 'it',
    'Portuguese': 'pt', 'Polish': 'pl', 'Turkish': 'tr', 'Russian': 'ru', 'Dutch': 'nl',
    'Czech': 'cs', 'Arabic': 'ar', 'Chinese': 'zh-cn', 'Japanese': 'ja', 'Hungarian': 'hu',
    'Korean': 'ko'
}

word_count = ["150", "450", "750", "1500", "2250", "3000", "4500"] 

main_character = [
    "Liam", "Olivia", "Noah", "Emma", "Aiden", "Amelia", "Sophia", "Jackson", "Ava", 
    "Lucas", "Mohammed", "Fatima", "Ali", "Aisha", "Hassan", "Aya", "Yusuf", "Mei", "Hiroshi", 
    "Sakura", "Ethan", "Mia", "James", "Harper", "Benjamin", "Evelyn", "Elijah", "Abigail", 
    "Logan", "Emily", "Alexander", "Ella", "Sebastian", "Elizabeth", "William", "Sofia", 
    "Daniel", "Avery", "Matthew", "Scarlett", "Henry", "Grace", "Michael", "Chloe", "Jackson", 
    "Victoria", "Samuel", "Riley", "David", "Aria", "José", "María", "Juan", "Ana", "Mateo", 
    "Santiago", "Valentina", "Lucía"]

setting = ["in the forest", "on an island", "on the moon", "in a medieval village", 
           "under the sea", "in a magical kingdom",
           "in a jungle", "in a spaceship", "in a circus", "in a pirate ship", "in a futuristic city", "in a candy land", ]

age = 2 

age_groups_authors = {
    "0-2": ["Eric Carle", "Sandra Boynton", "Margaret Wise Brown", "Karen Katz", "Leslie Patricelli"],
    "2-5": ["Dr. Seuss", "Julia Donaldson", "Beatrix Potter", "Maurice Sendak", "Eric Carle"],
    "5-7": ["Roald Dahl", "Mo Willems", "Dav Pilkey", "E.B. White", "Beverly Cleary"],
    "7-12": ["J.K. Rowling", "Rick Riordan", "Jeff Kinney", "Roald Dahl", "C.S. Lewis"]
}

moral = ["friendship", "diversity", "empathy", "respect", "courage", "honesty", "teamwork", 
         "kindness", "integrity"]

# Load Llama model
device = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")
model_directory = '../model/'
model_name = "textgen.gguf"
llm = Llama(model_path=os.path.join(model_directory, model_name), 
            n_gpu_layers=-1,
            n_threads=multiprocessing.cpu_count(),
            n_ctx=2048,
            seed = -1,
            verbose=False,
            #stop=["The end."]
            )

# Loade XTTS v2 model
device = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")
model_name = 'tts_models/multilingual/multi-dataset/xtts_v2'
tts = TTS(model_name=model_name, progress_bar=False, gpu=torch.cuda.is_available())

# Loade Stable Diffusion model
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"Using device: {device}")
vae = AutoencoderKL.from_single_file("../model/imagegen-fix.safetensors", torch_dtype=torch.float16)
pipe = StableDiffusionXLPipeline.from_single_file(
    "../model/imagegen-base.safetensors",
    vae=vae,
    torch_dtype=torch.float16,
    variant="fp16",
    use_safetensors=True
)

pipe = pipe.to(device)

if device == 'cuda':
    pipe.enable_sequential_cpu_offload()
    pipe.enable_vae_slicing()
    pipe.enable_vae_tiling()
else:
    print("GPU not available. Some optimizations will not be applied.")

pipe.safety_checker = None
pipe.requires_safety_checker = False

def sanitize_filename(filename):
    sanitized = re.sub(r'[\\/*?:"<>|]', "", filename)
    sanitized = sanitized.replace(' ', '_')
    return sanitized

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

def generate_story_html(original_title, sanitized_title, chunks, audio_files, language):
    template_path = os.path.join(app.root_path, '..', 'template', 'template.html')
    
    with open(template_path, 'r', encoding='utf-8') as template_file:
        template = template_file.read()
    
    story_json_path = os.path.join(app.root_path, '..', 'config', 'story.json')
    speaker_json_path = os.path.join(app.root_path, '..', 'config', 'speaker.json')
    
    with open(story_json_path, 'r') as f:
        story_data = json.load(f)
    
    with open(speaker_json_path, 'r') as f:
        all_speakers = json.load(f).get('speakers', [])
     
    display_title = html.unescape(original_title)
    
    story_entry = next((item for item in story_data if item["title"] == sanitized_title), None)
    existing_speakers = story_entry["speaker"] if story_entry else []
    languages = story_entry["language"] if story_entry else []

    if isinstance(existing_speakers, str):
        existing_speakers = [existing_speakers]

    existing_speakers_json = json.dumps(existing_speakers)
    all_speakers_json = json.dumps(all_speakers)

    # Use the first existing speaker, or 'standard' if none exists
    initial_speaker = existing_speakers[0] if existing_speakers else 'standard'

    data = {
        'title': display_title, 
        'sanitized_title': sanitized_title,
        'language': language,
        'chunks': [
            {
                'text': html.escape(chunk),
                'audio': f"/built/static/audio/{initial_speaker}_{language}_{sanitized_title}_{i + 1}.wav",
                'index': i + 1
            }
            for i, chunk in enumerate(chunks)
        ],
        'existing_speakers_json': existing_speakers_json,
        'all_speakers_json': all_speakers_json,
        'existing_speakers': existing_speakers,
        'all_speakers': all_speakers
    }

    story_html = chevron.render(template, data)

    # Optional: Remove any remaining {{variables}} that weren't replaced
    story_html = re.sub(r'\{\{.*?\}\}', '', story_html)

    return story_html

def generate_and_save_story_image(sanitized_title, story_text):
    global pipe, device

    title = sanitized_title.replace('_', ' ')
    story_preview = story_text[:77]  # Take the first 77 characters of the story
    negative_prompt = "blurry, disfigured, ugly, bad, immature, b&w, pale"
    style = "epic and scenic background, watercolor painted, vibrant colors, highest resolution, cinematic, high detail"

    guidance_scale = 12 
    num_inference_steps = 25
    height = 1024
    width = 1024

    try:
        app.logger.info(f"Generating image for title: {title}")
        app.logger.debug(f"Story preview: {story_preview}")

        # Generate the image
        image = pipe(
            height=height,
            width=width,
            prompt=f"{style} {title} {story_preview}",
            negative_prompt=negative_prompt,
            guidance_scale=guidance_scale,
            num_inference_steps=num_inference_steps
        ).images[0]

        # Save the image in the correct static folder
        image_path = os.path.join(app.root_path, '..', 'static', 'image', f"{sanitized_title}.jpg")
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        image.save(image_path)

        app.logger.info(f"Image generated and saved at: {image_path}")
        return f"/built/static/image/{sanitized_title}.jpg"
    except Exception as e:
        app.logger.error(f"Error generating image: {str(e)}", exc_info=True)
        return None

@app.route('/')
def index():
    return send_from_directory(os.path.dirname(os.path.dirname(app.root_path)), 'index.html')

@app.route('/generate-story', methods=['POST'])
def generate_story():
    data = request.json
    topic = data.get('topic', "").strip() or random.choice(children_story_topics)
    child_age = data.get('child_age', 2)
    word_count = data.get('word_count')
    speaker = data.get('speaker', 'standard')
    language_code = data.get('language_code', 'en')
    language_name = data.get('language_name', 'English')
    user_main_character = data.get('main_character', "").strip()
    user_setting = data.get('setting', "").strip()
    prompt_user = data.get('user_prompt', "").strip()
    selected_moral_lessons = data.get('moral_lessons', [])

    if not speaker:
        return jsonify({"error": "Speaker is required"}), 400

    # Use user's input for main character if provided, otherwise randomly select from the list
    story_main_character = user_main_character if user_main_character else random.choice(main_character)

    # Use user's input for setting if provided, otherwise randomly select from the list
    story_setting = user_setting if user_setting else random.choice(setting)
    
    # Update the global LANGUAGE variable
    global LANGUAGE
    LANGUAGE = language_code.lower().replace(' ', '_')
    app.logger.info(f"Language set to: {LANGUAGE}")

    # Determine the age range and authors based on child_age
    age_ranges = ["0-2", "2-5", "5-7", "7-12"]
    age_range = age_ranges[child_age - 1]
    authors = age_groups_authors[age_range]
    selected_author = random.choice(authors)

    # Use the full language name for the story generation
    language = language_name

    # Generate a title
    title_prompt = f"Generate a title for a story about {topic} in {language} with a maximum of 6 words and no special characters or asterisks."
    title_output = llm.create_chat_completion(
        messages=[
            {"role": "system", "content": "You are a title generation assistant."},
            {"role": "user", "content": title_prompt}
        ]
    )
    
    title = title_output["choices"][0]['message']['content'].strip()
    
    # Validate title: remove special characters and limit to 6 words
    title = re.sub(r'[^\w\s]', '', title)  # Remove special characters
    title_words = title.split()
    
    if len(title_words) > 6:
        title = ' '.join(title_words[:6])  # Limit to first 6 words

    # Create the moral lessons part of the prompt only if lessons were selected
    moral_lessons_prompt = ""
    if selected_moral_lessons:
        moral_lessons_string = ", ".join(selected_moral_lessons)
        moral_lessons_prompt = f"The story should incorporate moral lesson(s) about the importance of {moral_lessons_string}."
                                                                   
    # Set initial prompt
    prompt_user = ""

    prompt_initial = f"""    
        Develop a prompt that enables large language models to create engaging and age-appropriate stories for children in {language_name}.
        Generate an enhanced prompt with the following key points and do not ignore these: 
        - Generate an entire story with approximately {word_count} words for children aged {age_range} about {topic} with a playful tone and narrative writing style like {selected_author}. 
        - {prompt_user}
        - Start with a meaningful title: {title}
        - The main character is {story_main_character}. 
        - The story takes place {story_setting}.  
        - The story should be set in a world that is both familiar and unknown to the child reader. 
        - The story should incorporate a moral lesson about the importance of {moral_lessons_prompt}.
        - End the story with the saying: "The end!"
        """

    # Prompt generation
    output = llm.create_chat_completion(
        messages=[
            {"role": "system", "content": """
             You are an assistant specialized in creating prompts for large language models. 
             Your focus is on generating prompts that helps large language models craft stories specifically for children.
             Your task is to generate prompts exclusively. Do not write stories and do not ask questions.
             """},
            {"role": "user", "content": prompt_initial}
        ],
        temperature=0.8, 
        top_p=0.90,
        top_k=40,
        min_p=0.05,
        typical_p=1.0,
        repeat_penalty=1.0
    )

    prompt = output["choices"][0]['message']['content']

    # Story generation
    output_1 = llm.create_chat_completion(
        messages=[
            {"role": "system", "content": f"""
             You are a creative story writing assistant dedicated to crafting appropriate stories for children in {language_name}. 
             Your goal is to write narratives with surprising twists and happy endings.
             Easy to follow and understand, with a clear beginning, middle, and end.  
             Use only child-appropriate sources, and ensure the content is gender-neutral, inclusive, and ethically sound. 
             Adhere to ethical guidelines and avoid perpetuating harmful biases.
             Ensure that all produced stories exclude content related to hate, self-harm, sexual themes, and violence.
             Only generate the story, nothing else and always begin with a title for the story. 
             Start directly with the title without using special characters and do not write something like this: "Here is a 200-word story for children aged 2-5 with a playful tone:"
             """},
            {"role": "user", "content": prompt}
        ],
        #top_p=0.95,
        #top_k=100,
        #min_p=0.05,
        #typical_p=1.0,
        #repeat_penalty=1.1
    )
    story = output_1["choices"][0]['message']['content']

    # Extract title and text
    lines = story.split('\n', 1)
    original_title = lines[0].strip()  
    text = lines[1].strip() if len(lines) > 1 else ""

    global TITLE, TEXT
    TITLE = original_title
    TEXT = text

    sanitized_title = sanitize_filename(original_title)
    update_story_json(sanitized_title, original_title, speaker, LANGUAGE, TEXT)
    app.logger.info(f"Generated story with original title: {original_title}")
    app.logger.info(f"Sanitized title: {sanitized_title}")

    return jsonify({
        "success": True,
        "title": original_title,
        "sanitized_title": sanitized_title,
        "language": LANGUAGE,
        "text": TEXT,  
        "audio_files": []
    }), 200

@app.route('/generate-image', methods=['POST'])
def generate_image():
    data = request.json
    sanitized_title = data.get('sanitized_title')
    
    if not sanitized_title:
        return jsonify({"error": "Sanitized title is required"}), 400

    # Get the story text from story.json
    story_text = get_story_by_title(sanitized_title)
    
    if not story_text:
        app.logger.error(f"Story text not found for title: {sanitized_title}")
        return jsonify({"error": "Story text not found"}), 404

    try:
        image_path = generate_and_save_story_image(sanitized_title, story_text)
        
        if image_path:
            return jsonify({"success": True, "image_path": image_path})
        else:
            return jsonify({"success": False, "error": "Failed to generate image"}), 500
    except Exception as e:
        app.logger.error(f"Error in generate_image: {str(e)}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/process', methods=['GET'])
def process_text():
    speaker = request.args.get('speaker', default='', type=str)
    title = request.args.get('title', default='', type=str)
    language = request.args.get('language', default='en', type=str)
    generate_audio = request.args.get('generate_audio', default='false', type=str).lower() == 'true'

    app.logger.info(f"Processing text for speaker: {speaker}, title: {title}, generate_audio: {generate_audio}")

    if not speaker or not title:
        return jsonify({"error": "Speaker and title are required"}), 400

    global TEXT, TITLE, LANGUAGE

    sanitized_title = sanitize_filename(title)
    story_text = TEXT if TITLE == title else get_story_by_title(sanitized_title)
    
    if not story_text:
        app.logger.error(f"Story not found for title: {sanitized_title}")
        return jsonify({"error": "Story not found"}), 404

    app.logger.info(f"Story text retrieved, length: {len(story_text)}")

    text_chunks = split_text(story_text)
    results = []
    audio_files = []

    for i, chunk in enumerate(text_chunks):
        if generate_audio:
            audio_filename = f"{speaker}_{LANGUAGE}_{sanitized_title}_{i+1}.wav"
            audio_path = os.path.join(app.root_path, '..', 'static', 'audio', audio_filename)
            app.logger.info(f"Generating audio for chunk {i+1} at: {audio_path}")
            
            try:
                speaker_wav = os.path.join(app.root_path, '..', 'audio', f'{speaker}.wav')
                if not os.path.exists(speaker_wav):
                    raise FileNotFoundError(f"Speaker audio file not found: {speaker_wav}")
                
                tts.tts_to_file(text=chunk, file_path=audio_path, speaker_wav=speaker_wav, language=LANGUAGE)
                
                if not os.path.exists(audio_path):
                    raise FileNotFoundError(f"Generated audio file not found: {audio_path}")
                
                app.logger.info(f"Audio generated successfully for chunk {i+1}")
                audio_url = f"/built/static/audio/{audio_filename}"
            except Exception as e:
                app.logger.error(f"Error generating audio for chunk {i+1}: {str(e)}", exc_info=True)
                audio_url = None
            
            audio_files.append({"text": chunk, "audio": audio_url})
        else:
            audio_url = None

        results.append({
            'text': chunk,
            'audio': audio_url
        })

    update_story_json(sanitized_title, title, speaker, LANGUAGE, TEXT)

    # Generate and save the HTML file
    save_story_html(sanitized_title, text_chunks, [af["audio"] for af in audio_files], LANGUAGE)

    return jsonify(results)

@app.route('/generate_audio', methods=['POST'])
def generate_audio():
    data = request.json
    speaker = data.get('speaker')
    language = data.get('language', 'en')
    title = data.get('title')
    text = data.get('text')

    app.logger.debug(f"Received audio generation request: speaker={speaker}, language={language}, title={title}, text={text[:50] if text else None}...")

    if not speaker or not title or not text:
        return jsonify({"error": "Speaker, title, and text are required"}), 400

    sanitized_title = sanitize_filename(title)
    text_chunks = split_text(text)
    audio_files = []

    for i, chunk in enumerate(text_chunks):
        audio_filename = f"{speaker}_{language}_{sanitized_title}_{i+1}.wav"
        audio_path = os.path.join(app.root_path, '..', 'static', 'audio', audio_filename)
        tts.tts_to_file(text=chunk, file_path=audio_path, speaker_wav=os.path.join(app.root_path, '..', 'audio', f'{speaker}.wav'), language=language)
        audio_url = f"/built/static/audio/{audio_filename}"
        audio_files.append({"text": chunk, "audio": audio_url})

    # Update story.json
    update_story_json(sanitized_title, title, speaker, language, text)

    return jsonify({"success": True, "audio_files": audio_files})


def generate_audio_for_speaker(speaker, language, title, text):
    try:
        app.logger.info(f"Starting audio generation for speaker: {speaker}, title: {title}")

        speaker_wav = os.path.join(app.root_path, '..', 'audio', f'{speaker}.wav')
        app.logger.info(f"Looking for speaker audio file at: {speaker_wav}")
        
        if not os.path.exists(speaker_wav):
            app.logger.error(f"Speaker audio file does not exist: {speaker_wav}")
            return False, []

        # Verify the speaker audio file
        try:
            with wave.open(speaker_wav, 'rb') as wav_file:
                params = wav_file.getparams()
                app.logger.info(f"Speaker audio file params: {params}")
        except wave.Error as e:
            app.logger.error(f"Error verifying speaker audio file: {e}")
            return False, []

        chunks = split_text(text)
        audio_files = []
        sanitized_title = sanitize_filename(title)
        app.logger.info(f"Sanitized title: {sanitized_title}")

        for i, chunk in enumerate(chunks):
            audio_filename = f"{speaker}_{language}_{sanitized_title}_{i+1}.wav"
            audio_path = os.path.join(app.root_path, '..', 'static', 'audio', audio_filename)
            app.logger.info(f"Attempting to generate audio file: {audio_path}")

            try:
                tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=False, gpu=torch.cuda.is_available())
                tts.tts_to_file(text=chunk, file_path=audio_path, speaker_wav=speaker_wav, language=language)
                
                # Verify the generated audio file
                with wave.open(audio_path, 'rb') as wav_file:
                    params = wav_file.getparams()
                    app.logger.info(f"Generated audio file params: {params}")
                
                app.logger.info(f"Generated audio file: {audio_filename}")
                
                if not os.path.exists(audio_path):
                    app.logger.error(f"Generated audio file not found: {audio_path}")
                else:
                    app.logger.info(f"Verified audio file exists: {audio_path}")
                    audio_files.append({"text": chunk, "audio": f"/built/static/audio/{audio_filename}"})
            except Exception as e:
                app.logger.error(f"Error generating audio for chunk {i+1}: {str(e)}", exc_info=True)
                # If there's an error, we'll skip this chunk and continue with the next one
                continue

        if not audio_files:
            app.logger.error("No audio files were successfully generated.")
            return False, []

        app.logger.info("Audio generation completed successfully.")
        return True, audio_files
    except Exception as e:
        app.logger.error(f"Error in generate_audio_for_speaker: {str(e)}", exc_info=True)
        return False, []

def get_story_by_title(title):
    story_json_path = os.path.join(app.root_path, '..', 'config', 'story.json')
    app.logger.info(f"Searching for story in: {story_json_path}")
    if os.path.exists(story_json_path):
        with open(story_json_path, 'r') as f:
            story_data = json.load(f)
        app.logger.info(f"Number of stories in story.json: {len(story_data)}")
        for item in story_data:
            app.logger.debug(f"Comparing '{item['title'].lower()}' with '{title.lower()}'")
            if item["title"].lower() == title.lower():
                app.logger.info(f"Found matching story for title: {title}")
                return item.get("text")
        app.logger.error(f"No matching story found for title: {title}")
    else:
        app.logger.error(f"Story JSON file not found: {story_json_path}")
    return None

@app.route('/built/static/audio/<path:filename>')
def serve_audio(filename):
    return send_from_directory(os.path.join(app.root_path, '..', 'static', 'audio'), filename)

@app.route('/built/static/story/<path:filename>')
def serve_story(filename):
    return send_from_directory(os.path.join(app.root_path, '..', 'static', 'story'), filename)

@app.route('/built/config/<path:filename>')
def serve_config(filename):
    return send_from_directory(os.path.join(app.root_path, '..', 'config'), filename)

@app.route('/story')
def story_page():
    return send_from_directory(os.path.join(app.root_path, '..', 'built', 'content'), 'story.html')

def update_speaker_config(speaker):

    app.logger.debug(f"Updating speaker config for: {speaker}")
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

    app.logger.debug(f"Updated speaker.json with user: {speaker}")
    app.logger.debug(f"Current speaker.json content: {json.dumps(config, indent=2)}")

def convert_to_wav(input_path, output_path):
    try:
        audio = AudioSegment.from_file(input_path)
        audio.export(output_path, format="wav")
        app.logger.info(f"Audio file converted and saved as: {output_path}")
        return True
    except Exception as e:
        app.logger.error(f"Error converting audio file: {e}")
        return False

@app.route('/save-audio', methods=['POST'])
def save_audio():
    try:
        if 'audioFile' not in request.files or 'speakerName' not in request.form:
            return jsonify({'success': False, 'error': 'Audio file and speaker name are required'}), 400

        audio_file = request.files['audioFile']
        speaker = request.form['speakerName']

        audio_dir = os.path.join(app.root_path, '..', 'audio')
        os.makedirs(audio_dir, exist_ok=True)
        temp_path = os.path.join(audio_dir, f'temp_{speaker}.wav')
        audio_path = os.path.join(audio_dir, f'{speaker}.wav')

        app.logger.info(f"Saving temporary audio file to: {temp_path}")
        audio_file.save(temp_path)

        # Try to convert the audio file
        if not convert_to_wav(temp_path, audio_path):
            os.remove(temp_path)
            return jsonify({'success': False, 'error': 'Failed to convert audio file'}), 400

        os.remove(temp_path)  # Remove the temporary file

        # Verify the saved audio file
        try:
            with wave.open(audio_path, 'rb') as wav_file:
                params = wav_file.getparams()
                app.logger.info(f"Audio file params: {params}")
        except wave.Error as e:
            app.logger.error(f"Error verifying audio file: {e}")
            os.remove(audio_path)  # Remove the invalid file
            return jsonify({'success': False, 'error': 'Invalid WAV file format'}), 400

        update_speaker_config(speaker)

        app.logger.info(f"Audio file saved and verified at: {audio_path}")

        return jsonify({'success': True, 'message': f'Audio saved as {audio_path}'})
    except Exception as e:
        app.logger.error(f"Error saving audio: {e}", exc_info=True)
        # Clean up any temporary files if they exist
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)
        if 'audio_path' in locals() and os.path.exists(audio_path):
            os.remove(audio_path)
        return jsonify({'success': False, 'error': str(e)}), 500


def update_story_json(sanitized_title, original_title, new_speaker, language=None, text=None):
    try:
        story_json_path = os.path.join(app.root_path, '..', 'config', 'story.json')
        app.logger.debug(f"Updating story.json at: {story_json_path}")
        app.logger.debug(f"Received data: sanitized_title={sanitized_title}, original_title={original_title}, new_speaker={new_speaker}, language={language}, text={text[:50] if text else None}...")

        if os.path.exists(story_json_path):
            with open(story_json_path, 'r') as f:
                story_data = json.load(f)
        else:
            app.logger.warning(f"story.json not found. Creating new file.")
            story_data = []

        existing_entry = next((item for item in story_data if item["title"] == sanitized_title), None)
        if existing_entry:
            app.logger.info(f"Updating existing entry for title: {sanitized_title}")
            existing_entry["original_title"] = original_title
            if new_speaker:
                if "speaker" not in existing_entry:
                    existing_entry["speaker"] = []
                if new_speaker not in existing_entry["speaker"]:
                    existing_entry["speaker"].append(new_speaker)
            if language:
                if "language" not in existing_entry:
                    existing_entry["language"] = []
                if language not in existing_entry["language"]:
                    existing_entry["language"].append(language)
            if text:
                existing_entry["text"] = text
        else:
            app.logger.info(f"Creating new entry for title: {sanitized_title}")
            new_entry = {
                "title": sanitized_title,
                "original_title": original_title,
                "text": text or "",
                "speaker": [new_speaker] if new_speaker else [],
                "language": [language] if language else []
            }
            story_data.append(new_entry)

        app.logger.debug(f"Updated story data: {json.dumps(story_data, indent=2)}")

        with open(story_json_path, 'w') as f:
            json.dump(story_data, f, indent=2)
        app.logger.info(f"Successfully updated story.json with entry for title: {sanitized_title}")
    except Exception as e:
        app.logger.error(f"Error updating story.json: {e}", exc_info=True)

def save_story_html(sanitized_title, chunks, audio_files, language):
    app.logger.debug(f"Saving HTML for title: {sanitized_title}")
    
    # Retrieve the original title from the story.json file
    original_title = get_original_title(sanitized_title)
    
    # If original_title is not found, use the sanitized_title but replace underscores with spaces
    if not original_title:
        original_title = sanitized_title.replace('_', ' ')

    story_html = generate_story_html(original_title, sanitized_title, chunks, audio_files, language)
    story_html_path = os.path.join(app.root_path, '..', 'static', 'story', f"{sanitized_title}.html")
    with open(story_html_path, 'w', encoding='utf-8') as f:
        f.write(story_html)
    app.logger.info(f"HTML file generated at: {story_html_path}")

def get_original_title(sanitized_title):
    story_json_path = os.path.join(app.root_path, '..', 'config', 'story.json')
    if os.path.exists(story_json_path):
        with open(story_json_path, 'r') as f:
            story_data = json.load(f)
        for story in story_data:
            if story.get('title') == sanitized_title:
                return story.get('original_title', sanitized_title.replace('_', ' '))
    return None

@app.route('/test', methods=['GET'])
def test():
    return jsonify({'message': 'Test successful'})

@app.errorhandler(Exception)
def handle_exception(e):
    logging.error(f"Unhandled exception: {str(e)}", exc_info=True)
    return jsonify({'success': False, 'error': 'An unexpected error occurred'}), 500

# Define the path to the child.json file
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
CHILD_JSON_PATH = os.path.join(parent_dir, 'config', 'child.json')

print(f"Child JSON Path: {CHILD_JSON_PATH}")

@app.route('/save-child-info', methods=['POST'])
def save_child_info():
    data = request.json
    child_name = data.get('childName')
    child_age = data.get('childAge')  # This will be 1, 2, 3, or 4
    language = data.get('language')

    try:
        if os.path.exists(CHILD_JSON_PATH):
            with open(CHILD_JSON_PATH, 'r') as f:
                child_data = json.load(f)
        else:
            child_data = {}

        # Store only the necessary information
        child_data[child_name] = {
            'age_group_value': child_age,  # Store the slider value directly
            'language': language,
            'last_updated': datetime.now().timestamp()
        }

        os.makedirs(os.path.dirname(CHILD_JSON_PATH), exist_ok=True)

        with open(CHILD_JSON_PATH, 'w') as f:
            json.dump(child_data, f, indent=2)

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    
@app.route('/get-child-data', methods=['GET'])
def get_child_data():
    try:
        print(f"Attempting to read file from: {CHILD_JSON_PATH}")
        if not os.path.exists(CHILD_JSON_PATH):
            print(f"File does not exist: {CHILD_JSON_PATH}")
            return jsonify({'success': False, 'error': 'Child data file not found'}), 404

        with open(CHILD_JSON_PATH, 'r') as f:
            child_data = json.load(f)
        
        print(f"Raw child data: {child_data}")
        
        # Remove any empty string keys
        child_data = {k: v for k, v in child_data.items() if k}
        
        # Sort children by most recently added/updated
        sorted_children = sorted(child_data.items(), key=lambda x: x[1].get('last_updated', 0), reverse=True)
        
        # Get the last 5 entries
        recent_children = dict(sorted_children[:5])
        
        print(f"Processed child data: {recent_children}")
        
        return jsonify({'success': True, 'data': recent_children})
    except Exception as e:  
        print(f"Error in get_child_data: {str(e)}") 
        return jsonify({'success': False, 'error': str(e)}), 500  
    
@app.route('/check-child-json', methods=['GET'])
def check_child_json():
    try:
        with open(CHILD_JSON_PATH, 'r') as f:
            child_data = json.load(f)
        return jsonify({'success': True, 'data': child_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    
@app.route('/built/static/image/<path:filename>')
def serve_image(filename):
    return send_from_directory(os.path.join(app.root_path, '..', 'static', 'image'), filename)
    
@app.route('/get-story-speakers', methods=['GET'])
def get_story_speakers():
    title = request.args.get('title')
    if not title:
        return jsonify({"error": "Title parameter is required"}), 400

    story_json_path = os.path.join(app.root_path, '..', 'config', 'story.json')
    speaker_json_path = os.path.join(app.root_path, '..', 'config', 'speaker.json')

    try:
        # Get existing speakers for the story
        with open(story_json_path, 'r') as f:
            story_data = json.load(f)
        
        story_entry = next((item for item in story_data if item["title"] == title), None)
        existing_speakers = story_entry.get("speaker", []) if story_entry else []

        # Get all available speakers
        with open(speaker_json_path, 'r') as f:
            all_speakers_data = json.load(f)
        all_speakers = all_speakers_data.get("speakers", [])

        return jsonify({
            "success": True,
            "existing_speakers": existing_speakers,
            "all_speakers": all_speakers
        })
    except Exception as e:
        app.logger.error(f"Error in get_story_speakers: {str(e)}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500
    
if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=False, threaded=False)