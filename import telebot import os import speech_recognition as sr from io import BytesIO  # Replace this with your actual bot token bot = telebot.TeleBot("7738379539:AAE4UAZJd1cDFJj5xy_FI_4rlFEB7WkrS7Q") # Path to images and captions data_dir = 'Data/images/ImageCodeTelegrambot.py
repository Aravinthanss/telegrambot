import telebot
import os
import speech_recognition as sr
from io import BytesIO

# Replace this with your actual bot token
bot = telebot.TeleBot("7738379539:AAE4UAZJd1cDFJj5xy_FI_4rlFEB7WkrS7Q")
# Path to images and captions
data_dir = 'Data/images/'
captions_path = os.path.join(data_dir, 'captions.txt')

# Read the captions file
image_data = {}
with open(captions_path, 'r') as f:
    for line in f:
        filename, description = line.strip().split(',', 1)
        image_data[filename] = description

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Welcome to the chatbot! You can ask me to find images for you!")

@bot.message_handler(commands=['about'])
def send_about(message):
    bot.reply_to(message, "I can help you retrieve images based on descriptions!")

@bot.message_handler(commands=['info'])
def send_info(message):
    bot.reply_to(message, "Ask me about images or just chat!")

@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    # Download the voice message
    file_info = bot.get_file(message.voice.file_id)
    voice_file = bot.download_file(file_info.file_path)
    
    # Recognize speech from the audio file
    recognizer = sr.Recognizer()
    with sr.AudioFile(BytesIO(voice_file)) as source:
        audio_data = recognizer.record(source)
        try:
            # Convert audio to text
            query = recognizer.recognize_google(audio_data)
            bot.reply_to(message, f"You said: {query}")
            process_query(message, query)
        except sr.UnknownValueError:
            bot.reply_to(message, "Sorry, I could not understand the audio.")
        except sr.RequestError:
            bot.reply_to(message, "Could not request results from the speech recognition service.")

def process_query(message, query):
    if "find " in query:
        search_query = query.replace("find ", "").strip()
        results = {filename: desc for filename, desc in image_data.items() if search_query.lower() in desc.lower()}
        
        # Limit results to 5
        results = list(results.items())[:5]

        if results:
            for filename, description in results:
                image_path = os.path.join(data_dir, filename)
                
                if os.path.exists(image_path):
                    # Send the image with its description
                    with open(image_path, 'rb') as photo:
                        bot.send_photo(message.chat.id, photo, caption=description)
                else:
                    bot.reply_to(message, f"Image not found: {filename}")
        else:
            bot.reply_to(message, "No matching images found.")
    else:
        bot.reply_to(message, "I can help you find images. Just ask me!")

@bot.message_handler(func=lambda m: True)
def chatbot_reply(message):
    user_message = message.text.lower()
    process_query(message, user_message)

if __name__ == "__main__":
    bot.infinity_polling()
