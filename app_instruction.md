# OhanashiGPT


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

3. **Install Dependencies**

   ```bash
   pip install pip==24.1.2
   pip install -r requirements.txt
    ```

4. **Download and Prepare Models**
Ensure you have the model files in the built/model directory. Run text_generation.py to download and train prebuilt models. This might take some time.

   ```bash
   python downloads.py  
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
*   Click the "Generate Story" button to generate and narrate the story.
