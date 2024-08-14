import subprocess
import sys

def p_install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", package]) # -e editable
def git(*args):
    return subprocess.check_call(['git'] + list(args))

p_install('optimum-quanto')
git('clone', 'https://github.com/huggingface/diffusers.git')
install('diffusers/.[torch]')
install('diffusers/.[flax]')
git('-C', 'diffusers/', 'pull')