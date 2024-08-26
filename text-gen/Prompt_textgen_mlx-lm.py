#######
# Implementation of 
# 1) Prompt generation
# 2) Story generation
# 3) Stroty translation to German
# using the mlx-lm library for Apple Silicon chips

import os
os.system('pip install mlx-lm')

from mlx_lm import load, generate
import random

import time
start = time.time()

# Specify the checkpoint
checkpoint = "mlx-community/Meta-Llama-3.1-8B-Instruct-4bit"

# Load the corresponding model and tokenizer
model, tokenizer = load(path_or_hf_repo=checkpoint)

# Set story parameters
topic = "happy horses"
prompt_user = "The horses should fly."

language_name = "English"
word_count = ["150", "450", "750", "1500", "2250", "3000", "4500"] # [1, 3, 5, 10, 15, 20, 30] min
main_character = ["Liam", "Olivia", "Noah", "Emma", "Aiden", "Amelia", "Sophia", "Jackson", "Ava", 
                  "Lucas", "Mohammed", "Fatima", "Ali", "Aisha", "Hassan", "Aya", "Yusuf", "Mei", "Hiroshi", 
                  "Sakura", "Ethan", "Mia", "James", "Harper", "Benjamin", "Evelyn", "Elijah", "Abigail", 
                  "Logan", "Emily", "Alexander", "Ella", "Sebastian", "Elizabeth", "William", "Sofia", 
                  "Daniel", "Avery", "Matthew", "Scarlett", "Henry", "Grace", "Michael", "Chloe", "Jackson", 
                  "Victoria", "Samuel", "Riley", "David", "Aria", "José", "María", "Juan", "Ana", "Mateo", 
                  "Santiago", "Valentina", "Lucía"]
setting = ["in the forest", "on an island", "on the moon", "in a medieval village", "under the sea", "in a magical kingdom",
           "in a jungle", "in a spaceship", "in a circus", "in a pirate ship", "in a futuristic city", "in a candy land", ]
age_range = 2 # 0: "0-2", 1: "2-5", 2: "5-7", 3: "7-12"
age_groups_authors = {
    "0-2": ["Eric Carle", "Sandra Boynton", "Margaret Wise Brown", "Karen Katz", "Leslie Patricelli"],
    "2-5": ["Dr. Seuss", "Julia Donaldson", "Beatrix Potter", "Maurice Sendak", "Eric Carle"],
    "5-7": ["Roald Dahl", "Mo Willems", "Dav Pilkey", "E.B. White", "Beverly Cleary"],
    "7-12": ["J.K. Rowling", "Rick Riordan", "Jeff Kinney", "Roald Dahl", "C.S. Lewis"]
}
moral = ["friendship", "diversity", "empathy", "respect", "courage", "honesty", "teamwork", "kindness", "integrity"]

################
# Generate initial prompt
prompt_initial = f"""    
    Develop a prompt that enables large language models to create engaging and age-appropriate stories for children in {language_name}.
    Generate an enhanced prompt with the following key points and do not ignore these: 
    - Generate an entire story with approximately {word_count[1]} words for children aged {list(age_groups_authors.keys())[age_range]} about {topic} with a playful tone and narrative writing style like {random.choice(age_groups_authors[list(age_groups_authors.keys())[age_range]])}. 
    - {prompt_user}
    - Start with a meaningful title.
    - The main character is {random.choice(main_character)}. 
    - The story takes place {random.choice(setting)}.  
    - The story should be set in a world that is both familiar and unknown to the child reader. 
    - The story should incorporate a moral lesson about the importance of {random.choice(moral)}.
"""

#print("\nINITIAL PROMPT:")
#print(prompt_initial)
#print("\nEND OF INITIAL PROMPT.")

# Prompt generation
chatbot_role = """
        You are an assistant specialized in creating prompts for large language models. 
        Your focus is on generating prompts that helps large language models craft stories specifically for children.
        Your task is to generate prompts exclusively. Do not write stories and do not ask questions.
        Just create the prompt within quotation marks and do not write something like: "Here is a prompt that meets the requirements" or "This prompt should enable the large language model to generate a story that meets all the requirements, including the tone, style, and key elements specified.".
    """

messages = [
    {"role": "system", "content": chatbot_role},
    {"role": "user", "content": prompt_initial}
]
        
# Apply the chat template to format the input for the model
input_ids = tokenizer.apply_chat_template(messages, add_generation_prompt=True)
# Decode the tokenized input back to text format to be used as a prompt for the model
prompt = tokenizer.decode(input_ids)


# Specify the maximum number of tokens
max_tokens = 1024
# Specify if tokens and timing information will be printed
verbose = True
response = generate(
    model=model,
    tokenizer=tokenizer,
    prompt=prompt,
    max_tokens=max_tokens,
    verbose=verbose,
    #**generation_args,
)
prompt_final = response + '- End the story with the saying: "The end!"'

############################
# Now generate story with generated prompt
chatbot_role = """
    You are a creative story writing assistant dedicated to crafting appropriate stories for children. 
    Your goal is to write narratives with surprising twists and happy endings.
    Easy to follow and understand, with a clear beginning, middle, and end.  
    Use only child-appropriate sources, and ensure the content is gender-neutral, inclusive, and ethically sound. 
    Adhere to ethical guidelines and avoid perpetuating harmful biases.
    Ensure that all produced stories exclude content related to hate, self-harm, sexual themes, and violence.
    Only generate the story, nothing else and always begin with a title for the story. 
    Start directly with the title and do not write something like this: "Here is a 200-word story for children aged 2-5 with a playful tone:"
    """

messages = [
    {"role": "system", "content": chatbot_role},
    {"role": "user", "content": prompt_final}
]
        
# Apply the chat template to format the input for the model
input_ids = tokenizer.apply_chat_template(messages, add_generation_prompt=True)
# Decode the tokenized input back to text format to be used as a prompt for the model
prompt = tokenizer.decode(input_ids)



# Some optional arguments for causal language model generation
generation_args = {
    "temp": 0.7,
    "repetition_penalty": 1.2,
    "repetition_context_size": 20,
    "top_p": 0.95,
}
# Specify the maximum number of tokens
max_tokens = 4096
# Specify if tokens and timing information will be printed
verbose = True
response = generate(
    model=model,
    tokenizer=tokenizer,
    prompt=prompt,
    max_tokens=max_tokens,
    verbose=verbose,
    **generation_args,
)
story = response

############################
# Translation to German

chatbot_role = """
        You are a translation assistant. You translate the English input into German.
         """
messages = [
        {"role": "system", "content": chatbot_role},
        {"role": "user", "content": story}]
# Apply the chat template to format the input for the model
input_ids = tokenizer.apply_chat_template(messages, add_generation_prompt=True)
# Decode the tokenized input back to text format to be used as a prompt for the model
prompt = tokenizer.decode(input_ids)

response = generate(
    model=model,
    tokenizer=tokenizer,
    prompt=prompt,
    max_tokens=max_tokens,
    verbose=verbose,
    **generation_args,
)
translation = response

end = time.time()
print(f"\nEverything took {end-start:.1f} seconds")

