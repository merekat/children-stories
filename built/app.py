from flask import Flask, render_template, jsonify, Response
import torch
from TTS.api import TTS
import os
import re
from flask_cors import CORS
import json

app = Flask(__name__)
app = Flask(__name__, static_url_path='/static', static_folder='audio')
CORS(app)  # Enable CORS for all routes
app.config['DEBUG'] = True

# Initialize TTS with the XTTS v2 model
device = "cuda" if torch.cuda.is_available() else "cpu"
model = 'tts_models/multilingual/multi-dataset/xtts_v2'
tts = TTS(model).to(device)
tts.load_state_dict(torch.load('built/model/tts.pth'))

# Define user, language, and title
USER = 'michel'.lower().replace(' ', '_')
LANGUAGE = 'en'.lower().replace(' ', '_')
TITLE = 'Androcles and the Lion'.lower().replace(' ', '_')

# Create the output folder
OUTPUT_FOLDER = f"built/output/{USER}_{LANGUAGE}_{TITLE}"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Ensure the static/audio directory exists
os.makedirs('built/static/audio', exist_ok=True)

# The input file that I recorded
AUDIO_INPUT = 'built/audio/michel.wav'

# Check if the input audio file exists
if not os.path.exists(AUDIO_INPUT):
    raise FileNotFoundError(f"Input audio file '{AUDIO_INPUT}' not found.")
# Generated text
#TEXT = "Nearly a thousend years ago, an enslaved storyteller named Aesop became famous for marvelous fables and stories he created, and perhaps the most beloved of his tale is, 'Androcles and the Lion. ' In the story Androcles, also a slave, suffered terribly at the hands of one of the cruelest masters in all of Rome. No wonder that at the first chance he got, Androcles ran away. Bolting straight into the woods, he ran further and further until, exhausted, he could not move another step. Two days went by, and Androcles could find no food or water anywhere. 'I picked the wrong time of the year to run away!' Androcles despaired. 'The fruit and berries are all dried. The nuts are long gone. How did I manage to end up in the only part of the forest that has no streams or running water? Things can’t get any worse for me. 'If only that were true! Just then, Androcles heard a lion's roar - and not from a safe distance away but close, and coming closer! Panicked, he sprang to his feet and ran. As he fled through the bushes, he stumbled over the root of a tree. Imagine his horror when Androcles realized his foot was stuck! Each second the lion bounded closer and closer. Androcles froze in fear. 'I'm doomed!' he realized with dread.But when the great beast came up to him, instead of attacking him the lion lowered its head and moaned. The beast looked up with a strange expression. Then the lion held out its right paw. Covered in blood it was, and much swollen. 'That looks nasty,' Androcles said with sympathy, and the lion moaned like a sad little kitten. It thrust its paw closer to Androcles. 'Ah!' says Androcles with understanding, 'that's one nasty thorn in your paw. ' The lion moaned, nodding, and stared at him with those big sad eyes. 'Wait a minute!' says Androcles. 'You're not thinking you want ME to pull out that thorn?' Androcles thought, 'I would be out of my mind to take out that thorn! It would hurt the lion and I'd be so close it could just take one swipe of me and that would be it!' But the lion carried on in such a way and looked so pitiful and hopeless that Androcles was reminded of the wrenching pain he often felt after beatings by his slavemaster, and his heart relented. 'Well,' said Androcles, 'it's not as if my prospects were that great surviving in the woods, anyway. 'He gently wrapped both hands around the lion's paw. 'Now hold still,' he whispered. Taking the thorn with two fingers, in one quick stroke he twisted and drew it out. The lion roared with pain, but soon after found such relief with the thorn gone that he fawned upon Androcles and showed, in every way that he knew to whom he owed the relief. 'Give me a minute,' said Androcles, wondering why he was talking aloud to a lion. He wrapped some clean leaves around the wound and tied the bandage with long weeds. The lion limped off. Androcles freed himself of the tree root and just as he was wondering what his fate would be, there came the lion back again, this time with a young deer that it had slain. Androcles was able to cook it on a fire and have his first meal in days. Every day the lion would bring more food. Androcles would pet the beast on his head and talk to it in a tender way. He became quite fond of the huge creature.But one day a number of soldiers came marching through the forest and found Androcles. As he could not explain what he was doing, they took him prisoner and brought him back to the town from which he had fled. Here his master soon found him and brought him before the authorities. Soon Androcles was condemned to death for fleeing from his master. Now it used to be the custom in ancient Rome to throw murderers and other criminals to the lions in a huge circus. While the unlucky criminals were punished, the public would watch the spectacle of combat between them and the wild beasts. So Androcles was condemned to be thrown to the lions, and on the appointed day he was led forth into the Arena and left there alone with only a spear to protect him from the lion. The Emperor was in the royal box that day and gave the signal for the lion to come out and attack Androcles. But when it came out of its cage and got near Androcles, what do you think it did? Instead of jumping upon him, it fawned upon him and stroked him with its paw and made no attempt to do him any harm. It was of course the lion which Androcles had met in the forest. The Emperor, astonished at seeing such a strange behavior in so cruel a beast, summoned Androcles to him and demanded to know how it happened that this particular lion had lost all its cruelty of disposition. So Androcles told the Emperor all that had happened to him and how the lion was showing its gratitude for his having relieved it of the thorn.  The Emperor, convinced this must be the work of enchantment, pardoned Androcles and ordered his master to set him free.  Androcles then asked if the lion could be freed as well.  The  Emperor wasn't one to fool around with enchantments, and so he granted this wish, too.  From then on, whenever Androcles walked the streets of Rome, the lion marched by his side. No one bothered Androcles ever again, as I'm sure you can imagine. And we can end this story by saying that Androcles and his lion lived happily ever after."
TEXT = "Nearly a thousend years ago, an enslaved storyteller named Aesop became famous for marvelous fables and stories he created, and perhaps the most beloved of his tale is, 'Androcles and the Lion. ' In the story Androcles, also a slave, suffered terribly at the hands of one of the cruelest masters in all of Rome. No wonder that at the first chance he got, Androcles ran away. Bolting straight into the woods, he ran further and further until, exhausted, he could not move another step. Two days went by, and Androcles could find no food or water anywhere. 'I picked the wrong time of the year to run away!' Androcles despaired. "

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
    return render_template('index.html')

@app.route('/process', methods=['GET'])
def process_text():
    def generate():
        text_chunks = split_text(TEXT)
        for i, chunk in enumerate(text_chunks):
            audio_filename = f"{USER}_{LANGUAGE}_{TITLE}_{i+1}.wav"
            audio_path = os.path.join('built/static/audio', audio_filename)
            
            # Generate audio file
            tts.tts_to_file(text=chunk,
                            speaker_wav=AUDIO_INPUT,
                            language=LANGUAGE,
                            file_path=audio_path)
            
            result = {
                'text': chunk,
                'audio': f"/static/audio/{audio_filename}"
            }
            
            yield f"data: {json.dumps(result)}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True)