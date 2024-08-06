def text_generation(topic = "happy animals", age_range = "3 and 6", word_count = 200, **kwargs): 

    from llama_cpp import Llama
    import os

    # Make a directory to save models
    model_directory = '../built/model/'
    if not os.path.exists(model_directory): 
        os.mkdir(model_directory)

    # Model settings
    original_model_name = "Meta-Llama-3.1-8B-Instruct.Q4_K_M.gguf"
    model_name = "textgen.gguf"  
    repo_id = "QuantFactory/Meta-Llama-3.1-8B-Instruct-GGUF"

    # Pull model from hugging face 
    if not os.path.exists(model_directory + model_name):
        llm = Llama.from_pretrained(
            repo_id=repo_id,
            filename=original_model_name,
            local_dir=model_directory)
        
        # Rename the downloaded model to "textgen.gguf"
        os.rename(model_directory + original_model_name, model_directory + model_name)

    # Load model
    llm = Llama(model_path=model_directory + model_name,
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

    output = llm.create_chat_completion( messages = [
            {"role": "system", "content": "You are a story writing assistant."},
            {"role": "user", "content": prompt}
            ])
 
    text_gen = output["choices"][0]['message']['content']

    return text_gen

if __name__ == "__main__":
    # Example usage
    story = text_generation(topic="happy animals", age_range="3 and 6", word_count=200)
    print(story)