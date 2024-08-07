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
   git clone git@github.com:merekat/children-stories.git
2. **Activate the Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate
3. **Install Dependencies**

   ```bash
    pip install -r requirements.txt

4. **Download and Prepare Models**
*   Ensure you have the TTS models and other necessary files in the built/model directory.
*   Place the input audio file in built/audio.

## Usage

1. **Run the Flask Application in seperate Consoles**
   ```bash
   cd built/scripts
   python app.py  
2. **Access the Web Interface**

*   Open your browser and navigate to http://localhost:5000.

3. **Generate Stories**

*   Input the required parameters such as age and preferences.
*   Click the "Start Processing" button to generate and narrate the story.
