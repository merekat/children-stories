def text_generation(topic = "happy animals", age_range = "3 and 6", word_count = 200): 

    """
    llama.cpp enables LLM inference with minimal setup and 
    state-of-the-art performance on a wide variety of hardware.

        pip install llama-cpp-python
        pip install huggingface-hub
        
    References:
    https://github.com/abetlen/llama-cpp-python?tab=readme-ov-file
    https://github.com/ggerganov/llama.cpp#build
    https://llama-cpp-python.readthedocs.io/en/latest/api-reference/
    https://github.com/ggerganov/llama.cpp/blob/master/docs/build.md
    """

    from llama_cpp import Llama
    import os

    # Make a directory to save models
    if not os.path.exists('./models'): 
        os.mkdir('./models')

    """
    Download quantized model and move it into folder "models". 

    You can find quantization versions here:
    https://huggingface.co/lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF
    https://huggingface.co/QuantFactory/Meta-Llama-3.1-8B-Instruct-GGUF

    Info on GGUF and quantization versions:
    https://huggingface.co/docs/hub/en/gguf

    Info on Meta-Llama-3.1-8B-Instruct:
    https://huggingface.co/meta-llama/Meta-Llama-3.1-8B-Instruct
    """

    # Model settings
    model_name = "Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf"
    repo_id = "QuantFactory/Meta-Llama-3.1-8B-Instruct-GGUF"

    # Pull model from hugging face 
    if not os.path.exists(f'./models/{model_name}'):
        llm = Llama.from_pretrained(
            repo_id=repo_id, \
            filename=model_name, \
            local_dir = "./models/")

    # Load model
    llm = Llama(model_path=f"./models/{model_name}",
                n_threads = 4, # Set the number of threads to use during generation.
                n_ctx = 4096, # Set the size of the prompt context (default: 512).
                temperature = 1.1, # Adjust the randomness of the generated text (default: 0.8).
                top_p = 0.95, # Limit the next token selection to a subset of tokens with a cumulative probability above a threshold P (default: 0.9).
                verbose = False,
                stop = ["The end."]
                #chat_format="llama-3",  # Set chat_format according to the model you are using
                #n_gpu_layers=-1, # Uncomment to use GPU acceleration
                #seed=1337, # Uncomment to set a specific seed
    )

    # Chat Completion example
    ending = "The end."
    constrains = "Only use appropriate sources for children."

    prompt = f"""Write a bedtime story for children about {topic}. {constrains}
                    The story should be understandable for kids with an age between {age_range} years. 
                    The story should be about {word_count} words long and end with saying '{ending}'."""

    prompt1 = """In a magical forest, there lived a group of happy animals who loved to throw parties in the moonlight. 
                One night, as they were celebrating, they heard a mysterious sound coming from the depths of the forest. 
                Curious, they decided to follow the sound and embark on an adventure that would lead them to a surprising discovery. 
                Write a bedtime story for children about the exciting journey of these cheerful animals and the secret they uncovered. 
                (200 words, end with 'the end')""" 

    output = llm.create_chat_completion( messages = [
            {"role": "system", "content": "You are a story writing assistant."},
            {"role": "user", "content": prompt}
            ])

    """
    # Simple inference example
    output = llm(
        "Listen children. Happy llamas don't spit! But, they",
        max_tokens=100, #set to None to generate up to the end of the context window
        stop=["The end", "The rest is for tomorrow."], # Stop generating just before the model would generate a new question
        echo=True # Echo the prompt back in the output
    ) # Generate a completion, can also call create_completion
    """
    
    text_gen = output["choices"][0]['message']['content']

    return text_gen