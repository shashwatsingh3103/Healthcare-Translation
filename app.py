import streamlit as st
import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
import os
import tempfile
import io

# Initialize recognizer and translator
recognizer = sr.Recognizer()
translator = Translator()

# Define language codes (same as before)
languages = {
    'Afrikaans': 'af', 'Albanian': 'sq', 'Amharic': 'am', 'Arabic': 'ar', 'Armenian': 'hy',
    'Azerbaijani': 'az', 'Basque': 'eu', 'Belarusian': 'be', 'Bengali': 'bn', 'Bosnian': 'bs',
    'Bulgarian': 'bg', 'Catalan': 'ca', 'Cebuano': 'ceb', 'Chinese (Simplified)': 'zh-CN',
    'Chinese (Traditional)': 'zh-TW', 'Corsican': 'co', 'Croatian': 'hr', 'Czech': 'cs',
    'Danish': 'da', 'Dutch': 'nl', 'English': 'en', 'Esperanto': 'eo', 'Estonian': 'et',
    'Finnish': 'fi', 'French': 'fr', 'Frisian': 'fy', 'Galician': 'gl', 'Georgian': 'ka',
    'German': 'de', 'Greek': 'el', 'Gujarati': 'gu', 'Haitian Creole': 'ht', 'Hausa': 'ha',
    'Hawaiian': 'haw', 'Hebrew': 'he', 'Hindi': 'hi', 'Hmong': 'hmn', 'Hungarian': 'hu',
    'Icelandic': 'is', 'Igbo': 'ig', 'Indonesian': 'id', 'Irish': 'ga', 'Italian': 'it',
    'Japanese': 'ja', 'Javanese': 'jw', 'Kannada': 'kn', 'Kazakh': 'kk', 'Khmer': 'km',
    'Kinyarwanda': 'rw', 'Korean': 'ko', 'Kurdish': 'ku', 'Kyrgyz': 'ky', 'Lao': 'lo',
    'Latin': 'la', 'Latvian': 'lv', 'Lithuanian': 'lt', 'Luxembourgish': 'lb', 'Macedonian': 'mk',
    'Malagasy': 'mg', 'Malay': 'ms', 'Malayalam': 'ml', 'Maltese': 'mt', 'Maori': 'mi',
    'Marathi': 'mr', 'Mongolian': 'mn', 'Myanmar (Burmese)': 'my', 'Nepali': 'ne',
    'Norwegian': 'no', 'Nyanja (Chichewa)': 'ny', 'Odia (Oriya)': 'or', 'Pashto': 'ps',
    'Persian': 'fa', 'Polish': 'pl', 'Portuguese': 'pt', 'Punjabi': 'pa', 'Romanian': 'ro',
    'Russian': 'ru', 'Samoan': 'sm', 'Scots Gaelic': 'gd', 'Serbian': 'sr', 'Sesotho': 'st',
    'Shona': 'sn', 'Sindhi': 'sd', 'Sinhala (Sinhalese)': 'si', 'Slovak': 'sk', 'Slovenian': 'sl',
    'Somali': 'so', 'Spanish': 'es', 'Sundanese': 'su', 'Swahili': 'sw', 'Swedish': 'sv',
    'Tagalog (Filipino)': 'tl', 'Tajik': 'tg', 'Tamil': 'ta', 'Tatar': 'tt', 'Telugu': 'te',
    'Thai': 'th', 'Turkish': 'tr', 'Turkmen': 'tk', 'Ukrainian': 'uk', 'Urdu': 'ur',
    'Uyghur': 'ug', 'Uzbek': 'uz', 'Vietnamese': 'vi', 'Welsh': 'cy', 'Xhosa': 'xh',
    'Yiddish': 'yi', 'Yoruba': 'yo', 'Zulu': 'zu'
}

# Set session state for conversation log
if 'languages_selected' not in st.session_state:
    st.session_state.languages_selected = {}

if 'conversation_log' not in st.session_state:
    st.session_state.conversation_log = []

if 'listening' not in st.session_state:
    st.session_state.listening = False

# Language selection step (no changes here)
def language_selection():
    st.title("Healthcare Translation App")
    st.subheader("Select Languages")

    patient_lang = st.selectbox("Select speaking language for Patient", options=list(languages.keys()))
    patient_desired_lang = st.selectbox("Select output desired language for Patient", options=list(languages.keys()))

    healthcare_lang = st.selectbox("Select speaking language for Healthcare Provider", options=list(languages.keys()))
    healthcare_desired_lang = st.selectbox("Select output desired language for Healthcare Provider", options=list(languages.keys()))

    proceed = st.button("Proceed")

    if proceed:
        st.session_state.languages_selected = {
            'patient_lang_code': languages[patient_lang],
            'patient_desired_lang_code': languages[patient_desired_lang],
            'healthcare_lang_code': languages[healthcare_lang],
            'healthcare_desired_lang_code': languages[healthcare_desired_lang]
        }

        st.write("Language selection complete. Proceed to start the conversation.")

# Function to capture and translate speech
def capture_and_translate(input_lang_code, output_lang_code):
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        recognized_text = recognizer.recognize_google(audio, language=input_lang_code)
        translated_text = translator.translate(recognized_text, src=input_lang_code, dest=output_lang_code).text
        return recognized_text, translated_text
    except Exception as e:
        st.error(f"Error recognizing or translating: {str(e)}")
        return None, None

# Function to generate and play audio for the translated text
def play_audio(text, lang_code):
    tts = gTTS(text=text, lang=lang_code)
    tmp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(tmp_audio_file.name)
    return tmp_audio_file

# Conversation interface
def show_conversation_interface():
    patient_lang_code = st.session_state.languages_selected['patient_lang_code']
    healthcare_lang_code = st.session_state.languages_selected['healthcare_lang_code']
    patient_desired_lang_code = st.session_state.languages_selected['patient_desired_lang_code']
    healthcare_desired_lang_code = st.session_state.languages_selected['healthcare_desired_lang_code']

    col1, col2 = st.columns(2)

    with col1:
        st.header("Patient")
        if st.session_state.listening:
            if st.button("Stop Listening for Patient"):
                st.session_state.listening = False
                st.write("Stopped listening to Patient.")
        else:
            if st.button("Speak - Patient"):
                st.session_state.listening = True
                st.write("Listening to Patient...")
                patient_text, patient_translated = capture_and_translate(patient_lang_code, healthcare_desired_lang_code)
                if patient_text:
                    st.write("Patient's Original Text:", patient_text)
                    st.write("Patient's Translated Text:", patient_translated)
                    st.session_state.conversation_log.append({"speaker": "Patient", "original_text": patient_text, "translated_text": patient_translated})
                    patient_audio = play_audio(patient_translated, healthcare_desired_lang_code)
                    st.audio(patient_audio.name)

    with col2:
        st.header("Healthcare Provider")
        if st.session_state.listening:
            if st.button("Stop Listening for Healthcare Provider"):
                st.session_state.listening = False
                st.write("Stopped listening to Healthcare Provider.")
        else:
            if st.button("Speak - Healthcare Provider"):
                st.session_state.listening = True
                st.write("Listening to Healthcare Provider...")
                healthcare_text, healthcare_translated = capture_and_translate(healthcare_lang_code, patient_desired_lang_code)
                if healthcare_text:
                    st.write("Provider's Original Text:", healthcare_text)
                    st.write("Provider's Translated Text:", healthcare_translated)
                    st.session_state.conversation_log.append({"speaker": "Healthcare Provider", "original_text": healthcare_text, "translated_text": healthcare_translated})
                    healthcare_audio = play_audio(healthcare_translated, patient_desired_lang_code)
                    st.audio(healthcare_audio.name)

# Conversation controls and log download
def conversation_controls():
    if st.button("Start Conversation"):
        st.session_state.conversation_started = True
        st.write("Conversation started. Speak to communicate.")

    if st.button("End Conversation"):
        st.session_state.conversation_started = False
        st.write("Conversation ended. Download the conversation log below.")
        
        if st.session_state.conversation_log:
            log_filename = "conversation_log.txt"
            log_content = "\n".join([f"{entry['speaker']}:\nOriginal: {entry['original_text']}\nTranslated: {entry['translated_text']}\n" for entry in st.session_state.conversation_log])
            st.download_button("Download Conversation Log", log_content, file_name=log_filename)

# Main function to drive the app
def main():
    language_selection()

    if 'languages_selected' in st.session_state and st.session_state.languages_selected:
        show_conversation_interface()
        conversation_controls()

if __name__ == "__main__":
    main()
