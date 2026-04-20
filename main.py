#Codegnan workshop on voive Assessment

import streamlit as st      #used to build the front end

# configure the frontend page
st.set_page_config(
    page_title="Voive Assesstent",
    layout="wide"
)


#import all required libraries

import os
import time
import pyttsx3
import speech_recognition as sr
from groq import Groq
from dotenv import load_dotenv



#code to load the API key from local environment

load_dotenv()
GROQ_API_KEY=os.getenv("GROQ_API_KEY")

#checking if API key is uploaded successfully or not
if not GROQ_API_KEY:
    st.error("Missing API key")
    st.stop()


#Intialization of LLm model
client=Groq(api_key=GROQ_API_KEY)
MODEL="llama-3.3-70b-versatile"

#Initialization of speech to text recognizer
@st.cache_resource

def get_recognizer():
    return sr.Recognizer()



recognizer = get_recognizer()


#initialize the text to speech

def get_tts_engine():

    try:
        engine = pyttsx3.init()
        return engine

    except Exception as e:
        st.error(f"Failed to intialize the TTs engine: {e}")
        return None
    

def speak(text,voice_gender="girl"):
    try:
        engine=get_tts_engine()
        if engine is None:
            return

        voices=engine.getProperty('voices')

        if voices:
            if voice_gender=='boy':
                for voice in voices:
                    if "male" in voice.name.lower():
                        engine.setProperty("voice",voice.id)
                        break

            else:

                for voice in voices:
                    if "female" in voice.name.lower() or "zira" in voice.name.lower():
                        engine.setProperty('voice',voice.id)
                        break

        engine.setProperty('rate',150)
        engine.setProperty('volume',0.8)
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    except Exception as e:
        st.error("TTS error: {e}")


    
def listen_to_speech():
    try:
        with sr.Microphone() as source:                        #allowing the microphone to listen from user
            recognizer.adjust_for_ambient_noise(source, duration=1)               #removing noise
            audio=recognizer.listen(source,phrase_time_limit=10)               #listening to user for 10 seconds
            text=recognizer.recognize_google(audio)                 #converting the audio in to text
            return text.lower()                             #return the text
    except sr.UnknownValueError:
        return "Sorry, I do not catch you"
    except sr.RequestError:
        return "Speech service is not available"
    except Exception as e:
        return f"Error: {e}"

 

 #this fun taking user data which we are speaking 
def get_ai_response(messeges):
    try:
        response = client.chat.completions.create(
            model = MODEL,
            messages=messeges,
            temperature=0.7
    )
        result=response.choices[0].message.content
        return result.strip() if result else "Sorry I could not generate the respose"
    except Exception as e:
        return f"Error getting the AI response: {e}"








def main():
    st.title(" GenAI Voice Assessment")
    
    st.markdown("---------------")


    #initailizing the chat
    if "chat_history" not in st.session_state:
        st.session_state.chat_history=[
            {"role":"system","content":"You are the helpfull voice assesstent. plz just reply in one line"}
        ]


    #initailise megs to print on screen
    if "messages" not in st.session_state:
        st.session_state.messages = []


    with st.sidebar:
        st.header("CONTROLS")

        tts_enabled=st.checkbox("Enter text to Speech",value=True)


        #selecting gender of voice ssessment
        voice_gender=st.selectbox(
            "voice Gender",
            options=["girl","boy"],
            index=0 , #to select a baby girl voice
            help="Choose the Gender of Voice Assistant"

        )

        if st.button("Start Voice Input",use_container_width=True,type='primary'):
            with st.spinner("Listening......"):
                user_input=listen_to_speech()

                if user_input and user_input not in ["Sorry, I do not catch you","Speech Service is not available"]:
                    # st.session_state.messages.append({"role":"user", "content":user_input})
                    st.session_state.messages.insert(0, {"role":"user", "content":user_input})
                    st.session_state.chat_history.append({"role":"user", "content":user_input})


                    with st.spinner("Thinking...."):
                        ai_response=get_ai_response(st.session_state.chat_history)
                        # st.session_state.messages.append({"role":"assistant", "content":ai_response})
                        st.session_state.messages.insert(1, {"role":"assistant", "content":ai_response})
                        st.session_state.chat_history.append({"role":"assistant", "content":ai_response})

                    if tts_enabled:
                        speak(ai_response,voice_gender)

                    st.rerun()

                st.markdown("-----")

        if st.button("Clear Chat",use_container_width=True):
            st.session_state.messages = []
            st.session_state.chat_history = [
            {"role":"system","content":"You are the helpfull voice assesstent. plz just reply in one line"}
                    ]

            st.rerun()


    st.subheader("CONVERSTION")

    for message in st.session_state.messages:
        if message['role'] == "user":
            with st.chat_message("user"):
                st.write(message["content"])
        else:
            with st.chat_message("assistant"):
                st.write(message["content"])


    st.markdown("-----")
    st.markdown(
        """
            <div style = 'text-align: center; color: #666;'>
            <p> Copyright @ Codegnan </p>
            </div>
        """, unsafe_allow_html= True
    )



if __name__ == "__main__":
    main()