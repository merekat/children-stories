import os

# Make a directory to save models
if not os.path.exists('built/model/'): 
      os.mkdir('built/model/')

# Download a quantized Llama 3.1
if not os.path.exists('built/model/textgen.gguf'):
      os.system('curl -L -o built/model/textgen.gguf https://huggingface.co/lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF/resolve/main/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf?download=true')

# download standard diffusion XL base model
if not os.path.isfile('built/model/imagegen-base.safetensors'):
      os.system('curl -L -o built/model/imagegen-base.safetensors  https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors')

# download fix for VAE of SD_XL
if not os.path.isfile('built/model/imagegen-fix.safetensors'):
      os.system('curl -L -o built/model/imagegen-fix.safetensors  https://huggingface.co/madebyollin/sdxl-vae-fp16-fix/resolve/main/sdxl.vae.safetensors?download=true')

