import os
os.system('pip install stable-diffusion-cpp-python')

if not os.path.exists('../sd_models'): os.system('mkdir ../sd_models')
if not os.path.exists('../sd_models/loras'): os.system('mkdir ../sd_models/loras')
if not os.path.exists('figs'): os.system('mkdir figs')

# download standard diffusion XL base model
if not os.path.isfile('../sd_models/sd_xl_base_1.0.safetensors'):
      os.system('curl -L -o ../sd_models/sd_xl_base_1.0.safetensors  https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors')

# download fix for VAE of SD_XL
if not os.path.isfile('../sd_models/sdxl_vae-fp16-fix.safetensors'):
      os.system('curl -L -o ../sd_models/sdxl_vae-fp16-fix.safetensors  https://huggingface.co/madebyollin/sdxl-vae-fp16-fix/resolve/main/sdxl.vae.safetensors?download=true')

# download LCM LoRA for image generation in 4 to 8 steps
if not os.path.isfile('../sd_models/loras/sdxl_lcm-lora.safetensors'):
      os.system('curl -L -o ../sd_models/loras/sdxl_lcm-lora.safetensors  https://huggingface.co/latent-consistency/lcm-lora-sdxl/resolve/main/pytorch_lora_weights.safetensors')


LCM = True

if LCM:
      sample_method=7 # LCM
      cfg_scale=1.0
      sample_steps=6
else:
      sample_method=0 # Euler A
      cfg_scale=7.0
      sample_steps=20


#prompt = "Doll PippiXL in the foreground, fantasy, volumetric lighting, medieval village and forrest in the back, depth of field, 4k resolution"

#prompt = "medieval village world inside a glass sphere, high detail, fantasy, realistic, light effect, volumetric lighting, cinematic, macro, depth of field, blur, red light and clouds from the back, highly detailed epic cinematic concept art, excellent composition, 4k resolution"

#prompt = "Doll PippiXL crying in the rain, city street in the background, high detail, fantasy, light effect, volumetric lighting, cinematic, macro, depth of field, blur, highly detailed epic cinematic concept art, excellent composition, 4k resolution"

prompt = "anime, photorealistic, girl, collarbone, wavy hair, looking at viewer, upper body, necklace, floral print, ponytail, freckles, red hair, sunlight"


negative_prompt = "disfigured, ugly, bad, immature, b&w"

model_path="../sd_models/sd_xl_base_1.0.safetensors" 
vae_path = "../sd_models/sdxl_vae-fp16-fix.safetensors"
wtype="f16" # Weight type (options: default, f32, f16, q4_0, q4_1, q5_0, q5_1, q8_0)
width=1024
height=1024
prompt = prompt + "<lora:sdxl_lcm-lora:1.0>" #+ "<lora:sdxl_PippiXL:1.0>"

out_file = 'sdxl_anime_f16'



from stable_diffusion_cpp import StableDiffusion

pipe = StableDiffusion(
      n_threads=6,
      model_path=model_path,
      vae_path = vae_path,
      wtype=wtype,
      #
      lora_model_dir="../sd_models/loras/",
      #seed=1337, # Uncomment to set a specific seed
      rng_type=1 #CUDA
)

pipe.safety_checker = None
pipe.requires_safety_checker = False


image = pipe.txt_to_img(
      prompt=prompt,
      negative_prompt=negative_prompt,
      width=width,height=height,
      sample_method=sample_method, 
      cfg_scale=cfg_scale,
      sample_steps=sample_steps)

rgb_im = image[0].convert('RGB')
rgb_im.save("./figs/" + out_file + ".jpg")




