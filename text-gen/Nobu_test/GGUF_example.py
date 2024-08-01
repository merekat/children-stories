"""
Here, I show you how to run a quantized model (saved in the GGUF format) on CPUs using llama-cpp.
This example can be run on your local machine and uses about 5GB. On my Mac, the execution time is about 5 min, excluding the (one-time) time to download a model on your machine.

First, install llama-cpp-python and huggingface-hub.

- Installing llama-cpp-python:
If you want to use base ctransformers with no GPU acceleration, then run this command from the terminal:

    pip install llama-cpp-python

If you want some acceleration on Mac, then run this command from terminal:

    CMAKE_ARGS="-DGGML_BLAS=ON -DGGML_BLAS_VENDOR=OpenBLAS" pip install llama-cpp-python

If you want some acceleration on Windows, then run this command from terminal, I think. Please double check: https://github.com/abetlen/llama-cpp-python?tab=readme-ov-file

    $env:CMAKE_ARGS = "-DGGML_BLAS=ON -DGGML_BLAS_VENDOR=OpenBLAS"
    pip install llama-cpp-python


- Installing huggingface-hub:
    pip install huggingface-hub
    
    
References:
https://github.com/abetlen/llama-cpp-python?tab=readme-ov-file
https://github.com/ggerganov/llama.cpp#build
https://llama-cpp-python.readthedocs.io/en/latest/api-reference/
"""

from llama_cpp import Llama
import os

# Make a directory to save models
if not os.path.exists('./models'): 
    os.mkdir('./models')

# Download a quantized Llama 3.1
"""
Here, we will download a version with the Q4_K_M quantization. This model is 4.92GB.

You can find other quantization versions here:
https://huggingface.co/lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF

Info on GGUF and quantization versions:
https://huggingface.co/docs/hub/en/gguf

Info on Meta-Llama-3.1-8B-Instruct:
https://huggingface.co/meta-llama/Meta-Llama-3.1-8B-Instruct
"""
if not os.path.exists('./models/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf'):
    llm = Llama.from_pretrained(
        repo_id="lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF", \
        filename="Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf", \
        local_dir = "./models/")


# Simple inference example
llm = Llama(
      model_path="./models/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf",
      n_threads=8, # The number of CPU threads to use, tailor to your system and the resulting performance
      # n_gpu_layers=-1, # Uncomment to use GPU acceleration
      # seed=1337, # Uncomment to set a specific seed
      # n_ctx=2048, # Uncomment to increase the context window
      verbose=False
)

output = llm(
      "Listen children. Happy llamas don't spit! But, they",
      max_tokens=None, #set to None to generate up to the end of the context window
      stop=["The end", "The rest is for tomorrow."], # Stop generating just before the model would generate a new question
      echo=True # Echo the prompt back in the output
) # Generate a completion, can also call create_completion
print(output)

print(" ")
print(" ")
print(" ")

# Chat Completion example
llm = Llama(model_path="./models/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf",
            n_threads=8,
            verbose=False,
            #chat_format="llama-3.1",  # Set chat_format according to the model you are using
)
output = llm.create_chat_completion( messages = [
        {"role": "system", "content": "You are a story writing assistant."},
        {"role": "user", "content": "Write a story for children about happy llamas. The story should be about 500 word long and end with saying 'the end'."}
        ])
print(output)