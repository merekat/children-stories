# ChildGPT

ChildGPT is an innovative application that creates custom children's stories based on input parameters such as age and other preferences. What sets this app apart is its ability to narrate these stories using an AI-generated voice that mimics a parent or loved one, trained on their voice samples. Additionally, the app generates captivating images to accompany each story, providing a unique and engaging experience for children.

## Features

- **Custom Story Generation**: Stories tailored to the child's age and preferences.
- **AI Voice Synthesis**: Narrates stories using a familiar voice (e.g., parent's voice).
- **Image Generation**: Automatically creates illustrations to accompany the stories.
- **Interactive Experience**: Engaging storytelling for children, even when parents can't be there in person.

## Installation

1. **Clone the Repository**

   ```bash
   git clone
   ```

2. **Activate the Environment**
   Requirements: Python 3.11.3
   
   For Mac:
   ```bash
   pyenv install 3.11.3
   pyenv local 3.11.3
   python -m venv .venv
   source .venv/bin/activate
   ```
   
   For Windows with `PowerShell` CLI :

    ```PowerShell
    pyenv local 3.11.3
    python -m venv .venv
    .venv\Scripts\Activate.ps1
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    ```

    For Windows with `Git-bash` CLI :
  
    ```BASH
    pyenv local 3.11.3
    python -m venv .venv
    source .venv/Scripts/activate
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    ```

4. **Install Dependencies**

   ```bash
   pip install pip==24.1.2
   pip install -r requirements.txt
    ```

5. **Download and Prepare Models**
*   Ensure you have the model files in the built/model directory.
*   Run text_generation.py to download and train prebuilt text generation model Lama. This might take some time.
   
   ```bash
   cd text-gen
   python text_generation.py  
   ```
*   Run audio_generation.py to download and train prebuilt text generation model xtts_v2. This might take some time. 

   ```bash
   cd audio-gen
   python audio_generation.py  
   ```

*   All models will automatically be saved in the built/model directory. 

## Usage

1. **Run the Flask Application**

   ```bash
   cd built/scripts
   python app.py  
   ```

2. **Access the Web Interface**

*   Open your browser and navigate to http://localhost:5000/built/index.html.

3. **Generate Stories**

*   Input the required parameters such as age and preferences.
*   Click the "Start Processing" button to generate and narrate the story.
