# Importing required libraries:

# 🗣️ Speech Recognition and TTS
import speech_recognition as sr                     # Convert voice to text
import pyttsx3                                      # Offline text-to-speech

# 🌐 Web & API
import webbrowser                                   # Open URLs
import requests                                     # Make API calls (e.g., for news)
from pytube import Search                           # Search YouTube videos

# 🧠 Gemini AI
import google.generativeai as genai                 # Gemini AI integration

# 🔐 Environment and OS
import os                                           # File management (create, delete, play files)
from dotenv import load_dotenv                      # Load API keys from .env

load_dotenv()  # Load key-value pairs from .env into environment variables




# Initialize speech recognition and text-to-speech
recognizer = sr.Recognizer()
engine = pyttsx3.init()

# Configure recognizer settings
recognizer.energy_threshold = 100                   # Lower this if the recognizer isn’t picking up your voice; raise it if background noise is being detected as speech.
recognizer.dynamic_energy_threshold = True          # Keeps recognition reliable in noisy or quiet places without manually changing
recognizer.pause_threshold = 0.8                    # If the user pauses for 0.8 seconds, the recognizer will assume they're done speaking.
recognizer.operation_timeout = None                 # Maximum time to wait for an operation (like listening to a microphone). None means no time limit
recognizer.phrase_threshold = 0.3                   # Minimum length of continuous speech (in seconds) to be considered a phrase.
recognizer.non_speaking_duration = 0.8              # How much time (in seconds) of silence the recognizer will include before and after speech.


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")        # Loads Gemini API key from .env
NEWS_API_KEY = os.getenv("NEWS_API_KEY")            # Loads News API key from .env
genai.configure(api_key=GEMINI_API_KEY)             # Sets the Gemini API key for use
model = genai.GenerativeModel("gemini-1.5-pro")     # Prepares the Gemini model  # model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest")-other model



def speak(text):
    """Convert text to speech."""
    engine.say(text)
    engine.runAndWait()

# Get and speak top news headlines:
def get_news():
    """Fetches top news headlines."""
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}"
    
    try:
        response = requests.get(url)                                # API call
        news_data = response.json()                                 # (JSON)Convert response to Python dict
        
        # Debugging: Check API response
        print("News API Response:", news_data)                      # For debugging

        if news_data["status"] == "ok" and "articles" in news_data:
            articles = news_data["articles"][:5]                    # Get top 5 articles
            
            if not articles:  
                speak("Sorry, I couldn't find any news articles.")
                return
            
            # Extract just the headlines
            headlines = [article["title"] for article in articles]
            
            print("Top 5 News Headlines:")
            news_text = "Here are the top 5 news headlines. "
            
            for idx, headline in enumerate(headlines, start=1):
                print(f"{idx}. {headline}")                         # Print each headline for debugging
                news_text += f"Headline {idx}: {headline}. "

            speak(news_text)                                        # Speak all headlines together
        else:
            speak("Sorry, I couldn't fetch news.")
            print("News API error:", news_data)                     # Debugging: Print API error message
    except Exception as e:
        speak("An error occurred while fetching news.")
        print(f"Error: {e}")                                        # Print error for debugging


# Play a song from YouTube:
def play_song(song_name):
    """Searches for a song on YouTube and plays it."""
    try:
        search_results = Search(song_name).results                  # Search YouTube
        if search_results:
            video_url = f"https://www.youtube.com/watch?v={search_results[0].video_id}&autoplay=1"
            webbrowser.open(video_url)                              # Open first result
            speak(f"Playing {song_name}.")
            speak("Waiting for your next command.")
        else:
            speak("Sorry, I couldn't find that song.")
    except Exception as e:
        speak("An error occurred while playing the song.")
        print(f"Error: {e}")


# Use Gemini AI to answer general questions
def ask_gemini(question):
    """Uses Google Gemini AI to answer general knowledge questions."""
    try:
        response = model.generate_content(question)                   # Get AI answer
        answer = response.text.strip()                                # Clean it up
        print(f"Gemini AI: {answer}")
        speak(answer)
        speak("Waiting for your next command.")
    except Exception as e:
        print(f"Error with Gemini AI: {e}")
        speak("Sorry, I couldn't process your request.")


# Determine what the user wants based on their voice command
def processCommand(command):
    """Process the user's command."""
    print(f"Processing command: {command}")
    command_lower = command.lower()

    if "open " in command_lower:                                        # Example: "open youtube"
        website = command_lower.replace("open ", "").strip()
        webbrowser.open(f"https://www.{website}.com")
        speak(f"{website} is now open. Waiting for your next command.")
        return True                                                     # Indicate success
    elif command_lower.startswith("play"):                              # Example: "play another love"
        song_name = command_lower.split("play", 1)[1].strip()
        play_song(song_name)
        return True                                                     # Indicate success
    elif "what's today's news" in command_lower:
        get_news()
        return True                                                     # Indicate success
    else:
        # If none of the above conditions match, use Gemini AI for answering general questions
        speak("Let me check that for you.") 
        ask_gemini(command)
        return True                                                     # Indicate success



# Main logic that listens for wake word and takes commands:
if __name__ == "__main__":
    speak("Initializing Jarvis...")

    while True:
        print("Listening for wake word...")
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            try:
                audio = recognizer.listen(source, timeout=6, phrase_time_limit=5)
                word = recognizer.recognize_google(audio)
                print(f"You said: {word}")
                
                if word.lower().startswith(("hey jarvis", "jarvis")):
                    speak("Yes, how may I assist you?")
                    
                    while True:                                         # Keep listening for commands 
                        with sr.Microphone() as source:
                            print("Jarvis activated... Please say your command.")
                            recognizer.adjust_for_ambient_noise(source)
                            audio = recognizer.listen(source)
                            try:
                                command = recognizer.recognize_google(audio)
                                print(f"You said: {command}")
                                success = processCommand(command)
                                if success:
                                    break
                            except sr.UnknownValueError:
                                speak("I didn't catch that. Could you please repeat?")
                            except Exception as e:
                                print(f"Error: {e}")
            except sr.UnknownValueError:
                print("Jarvis could not understand the audio.")
            except sr.WaitTimeoutError:
                print("Listening timed out. Try speaking again.")
            except Exception as e:
                print(f"Error: {e}")



