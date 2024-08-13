import torch
from diffusers import StableDiffusionPipeline

model_name = "runwayml/stable-diffusion-v1-5"

#model_name = "CompVis/stable-diffusion-v1-4"

pipe = StableDiffusionPipeline.from_pretrained(model_name, 
                                               torch_dtype=torch.float16)
pipe = pipe.to("mps")

prompt = 'Watercolor of a village near a dark forrest with a little girl in the foreground.'

steps = 20

image = pipe(prompt, 
             #negative_prompt=negative_prompt, 
             num_inference_steps=steps).images[0]
image.save("figs/girl_village.jpg")