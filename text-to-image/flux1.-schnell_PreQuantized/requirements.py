import subprocess
import sys

def p_install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
def p_upgrade(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--upgrade"])
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", package]) # -e editable
def git(*args):
    return subprocess.check_call(['git'] + list(args))

p_install('optimum-quanto')
p_install('accelerate')
git('clone', 'https://github.com/huggingface/diffusers.git')
install('diffusers/.[torch]')
install('diffusers/.[flax]')
git('-C', 'diffusers/', 'pull')
p_upgrade('transformers')

import torch # necessary to check the device
# identify which device is used (cuda = GPU, cpu = CPU only, mps = Mac)
device: str = 'cuda' if torch.cuda.is_available() else ('mps' if torch.backends.mps.is_available() else 'cpu')
if device == 'cpu':
    subprocess.check_call(["pip3", "install", "torch", "torchvision", "torchaudio", "--index-url", "https://download.pytorch.org/whl/cu118"])
elif device == 'cuda':
    subprocess.check_call(["pip3", "install", "torch", "torchvision", "torchaudio", "--index-url", "https://download.pytorch.org/whl/cu124"]) 
elif device == 'mps':
    subprocess.check_call(["pip3", "install", "torch", "torchvision", "torchaudio"])
else:
    print("device unknown")
# exception: cu124 necessary for google colab no matter if T4 GPU enabled or CPU only
