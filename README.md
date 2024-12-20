# Voice Task Manager

A GUI application for managing tasks with voice note capabilities. You can create tasks, mark them as complete, and add voice notes to tasks using speech-to-text functionality.

## Features

- Create and manage tasks with titles and descriptions
- Mark tasks as complete and earn points
- Add voice notes to tasks using speech-to-text
- View task history and completion status
- Points system to track progress

## Installation

1. Create a virtual environment and activate it:
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:
```bash
python main.py
```

2. Using the application:
   - Click "Add Task" to create a new task
   - Select a task and click "Complete Task" to mark it as done
   - Select a task and click "Start Recording" to begin recording a voice note
   - Click "Stop Recording" when you're done speaking to save the note
   - Voice notes will appear in the right panel when a task is selected
   - The status bar will show feedback during recording

## Dependencies

- SQLAlchemy: Database ORM
- SpeechRecognition: Speech-to-text functionality
- pyttsx3: Text-to-speech engine
- PyAudio: Audio interface for speech recognition
- tkinter: GUI framework (included with Python)
