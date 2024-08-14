# as a reference for time on cpu with 16GB ram: 
# 15 min for loading, quantizing the models + set up of pipeline
# 20-30 min for each iteration when image size 128x128
# at least 4 iterations needed --> ~2-2,5h

import torch

from optimum.quanto import freeze, qfloat8, quantize

from diffusers.models.transformers.transformer_flux import FluxTransformer2DModel
from diffusers.pipelines.flux.pipeline_flux import FluxPipeline

from transformers import T5EncoderModel

# define saving path for downloaded models
cache_dir = '../../models/text-to-image/flux.1-schnell'

model = "black-forest-labs/FLUX.1-schnell" # official model flux1.-schnell from Blackforest
model_tr = "https://huggingface.co/Kijai/flux-fp8/blob/main/flux1-schnell-fp8.safetensors" # quantized transformer from Hugginface

# load and quantize transformer
transformer = FluxTransformer2DModel.from_single_file(model_tr, 
                                                        torch_dtype=torch.bfloat16,
                                                        cache_dir = cache_dir
)
quantize(transformer, weights=qfloat8)
freeze(transformer)

# load and quantize text_encoder_2
text_encoder_2 = T5EncoderModel.from_pretrained(model,
                                                subfolder="text_encoder_2",
                                                torch_dtype=torch.bfloat16,
                                                cache_dir=cache_dir
)
quantize(text_encoder_2, weights=qfloat8)
freeze(text_encoder_2)

# set up pipe line with main model and the two quantized models (transformer & text_encoder_2)
pipe = FluxPipeline.from_pretrained(model,
                                    transformer=None,
                                    text_encoder_2=None,
                                    torch_dtype=torch.bfloat16
)
pipe.transformer = transformer
pipe.text_encoder_2 = text_encoder_2
pipe.to(torch.device('cpu'))

# define parameters for the image
prompt = "Ancient soldier with a sword and a shield. Behind there are horses. In the background there is a mountain with snow."
height, width = 128, 128
num_inference_steps = 2  # number of iterations, 4 gives decent results and should be considered as minimum; people on hugging face and git hub ~15-50 iterations
generator = torch.Generator("cpu").manual_seed(12345) # set seed for repeatable results

image = pipe(
    prompt=prompt,
    guidance_scale=0.0, # must be 0.0 for flux1.-schnell, may be 3.5 for flux1.-dev but up to 7.0 --> higher guidance scale forces the model to keep closer to the prompt at the expense of image quality
    height=height,
    width=width,
    #output_type="pil",
    num_inference_steps=num_inference_steps,
    max_sequence_length=128, #256 is max for flux1.-schnell; maximum sequence length to use with the prompt
    generator=generator
).images[0]

image.save(f"figs/Kijai_qt-qte2_{num_inference_steps}_{height}_{width}.png")
