import speech_recognition as sr
import pyttsx3
from threading import Thread
import queue

class SpeechHandler:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.voice_queue = queue.Queue()
        self._setup_voice()
        self.is_recording = False
        self.audio_data = []
        
    def _setup_voice(self):
        """Configure the text-to-speech engine settings"""
        voices = self.engine.getProperty('voices')
        # Set the default voice (usually index 0 is male, 1 is female)
        self.engine.setProperty('voice', voices[0].id)
        # Set the speaking rate (default is 200)
        self.engine.setProperty('rate', 175)
        # Set volume (max is 1.0)
        self.engine.setProperty('volume', 0.9)
        
    def start_recording(self):
        """Start recording audio"""
        if self.is_recording:  # If already recording, stop first
            self.stop_recording()
        self.is_recording = True
        self.audio_data = []
        
    def stop_recording(self):
        """Stop recording and process the audio"""
        self.is_recording = False
        if not self.audio_data:
            return None
            
        try:
            print("Processing speech...")
            # Process each audio segment individually and combine the text
            text_segments = []
            for audio in self.audio_data:
                try:
                    text = self.recognizer.recognize_google(audio)
                    text_segments.append(text)
                except sr.UnknownValueError:
                    continue  # Skip segments that couldn't be recognized
                    
            if text_segments:
                final_text = " ".join(text_segments)
                print(f"Recognized: {final_text}")
                return final_text.lower()
            return None
        except sr.UnknownValueError:
            print("Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            return None
    
    def listen(self):
        """Listen for voice input and return transcribed text"""
        with sr.Microphone() as source:
            print("Listening...")
            self.speak("Listening...")
            try:
                while self.is_recording:
                    try:
                        audio = self.recognizer.listen(source, timeout=2)
                        self.audio_data.append(audio)
                    except sr.WaitTimeoutError:
                        continue  # Keep listening if timeout
                return self.stop_recording()
            except Exception as e:
                print(f"Error during recording: {e}")
                self.is_recording = False
                return None
    
    def speak(self, text):
        """Convert text to speech"""
        def _speak_worker():
            while True:
                text = self.voice_queue.get()
                if text is None:
                    break
                print(f"Speaking: {text}")
                self.engine.say(text)
                self.engine.runAndWait()
                self.voice_queue.task_done()
        
        # Start speaker thread if not already running
        if not hasattr(self, 'speaker_thread') or not self.speaker_thread.is_alive():
            self.speaker_thread = Thread(target=_speak_worker, daemon=True)
            self.speaker_thread.start()
        
        # Add text to queue
        self.voice_queue.put(text)
    
    def cleanup(self):
        """Clean up resources"""
        if hasattr(self, 'speaker_thread') and self.speaker_thread.is_alive():
            self.voice_queue.put(None)
            self.speaker_thread.join()
