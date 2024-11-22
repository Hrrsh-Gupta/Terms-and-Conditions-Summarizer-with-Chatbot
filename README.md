# Terms and Conditions Summarizer with Chatbot
## Overview
This project is a PyQt5 GUI-based application designed to simplify the summarization of lengthy terms and conditions documents. Users can input text or upload documents to generate summaries in three formats: basic, topic-specific, and abstractive. The application integrates a Llama 3-based chatbot, enabling users to resolve queries related to the text. All generated summaries are stored in an SQLite database and can be accessed via the navigation sidebar under session date and time.

## Features
- **File Upload**: Upload Doc, Text, PDF, PNG files for text extraction.
- **Extractive Summary**: NLP based extractive summary.
- **Abstractive Summary**: llama3 based abstractive summary via Groq API.
- **Q&A Chatbot**: Ask questions related to the input text to find hidden phrases.
- **Database Integration**: All summaries are stored under a session name and can be exported as a PDF.
- **Minimalist UI**: Clean and interactive interface.

## Prerequisites
- The app was developed in Python 3.11. Ensure Python 3.11 or higher is installed.
- Ensure you have a GroqAPI key in environment variables to use abstractive summary and chatbot functionalities. To get a key check Groq API-Key Environment setup under Installation.

## Installation

1. Clone the repository:
```bash
git clone <repository_url>
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
```

3. Activate the virtual environment:
**For Windows:**
```bash
.\venv\Scripts\activate
```
**For Linux/Mac:**
```bash
source venv/bin/activate
```
4. Install the required packages:
```bash
pip install -r requirements.txt
```
5. Groq API-Key Environment setup:
   Obtain a free API key from GroqCloud by signing up at: [GroqCloud](https://console.groq.com/keys)
   **Windows Set-up**

   **Option 1**: Set your ‘GROQ_API_KEY’ Environment Variable via the cmd prompt
   Run the following in the cmd prompt, replacing <yourkey> with your API key:
   ```
   setx GROQ_API_KEY "<yourkey>"
   ```
   You can validate that this variable has been set by opening a new cmd prompt window and typing in 
   ```
   echo %GROQ_API_KEY%
   ```

   **Option 2**: Set your ‘GROQ_API_KEY’ through Environment Variables.
   1. Select "Edit the system environment variables" on start menu.
   2. Select Environment Variables...
   3. Select New… from the User variables section(top). Add your name/key value pair, replacing <yourkey> with your API key.
   ````
   Variable name: GROQ_API_KEY
   Variable value: <yourkey>
   ````
   
## Usage
1. Run the application app.py in your IDE or terminal.
2. Building the Executable.
   - Activate your virtual environment.
   - Install PyInstaller:
   ````
   pip install pyinstaller
   ````
   - Change directory to the project's main folder.
   - Run the command listed in `app_build_command.txt` to create the executable.


## Acknowledgements
GroqCloud: For providing API access to advanced models.
