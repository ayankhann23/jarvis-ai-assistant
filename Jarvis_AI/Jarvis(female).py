import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import webbrowser
import datetime
import pyttsx3
import speech_recognition as sr
import openai
import threading
from openai import OpenAI  # Import OpenAI
import re


# OpenAI API key
try:
    client = OpenAI(api_key="your-openai-api-key")  # Replace with your actual API key
except Exception as e:
    print(f"Error initializing OpenAI: {e}")
    client = None

# Initialize Dash App
app = dash.Dash(__name__)
server = app.server

# Global variable to hold mic result
mic_query = ""


# Voice output function with female voice


def say(text):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')

    # Try to find a female voice
    for voice in voices:
        if "female" in voice.name.lower() or "Zira" in voice.name:
            engine.setProperty('voice', voice.id)
            break

    engine.say(text)
    engine.runAndWait()







# Speech input function
def take_command():
    global mic_query
    r = sr.Recognizer()
    with sr.Microphone() as source:
        try:
            r.pause_threshold = 1
            audio = r.listen(source, timeout=5)
            query = r.recognize_google(audio, language="en-in")
            mic_query = query
        except Exception as e:
            print(f"Error in take_command: {e}")
            mic_query = ""



# GPT function
def chat_with_gpt(prompt):
    if client is None:
        return "Error: OpenAI client not initialized. Please check your API key and environment."
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except openai.APIError as e:
        if e.code == "insufficient_quota":
            return "Error: You have exceeded your OpenAI API quota. Please check your usage and billing."
        else:
            return f"Error: An error occurred with the OpenAI API-key"
    except Exception as e:
        return f"Error: An unexpected error occurred: {e}"


# Layout
app.layout = html.Div([
    html.H1("Jarvis Dashboard", style={'textAlign': 'center', 'color': '#2c3e50'}),
    dcc.Input(id='user-input', type='text', placeholder='Ask Jarvis...', style={'width': '60%', 'padding': '10px'}),
    html.Button('Enter', id='submit-btn', n_clicks=0, style={'margin': '10px'}),
    html.Button('🎙️ Mic', id='mic-btn', n_clicks=0, style={'margin': '10px'}),
    html.Div(id='output-response', style={'marginTop': '30px', 'fontSize': '18px'})
],style={
    'backgroundImage': 'url("https://picsum.photos/1600/900")',  #  Use your image URL here
    'backgroundSize': 'cover',
    'backgroundPosition': 'center',
    'minHeight': '100vh',
    'padding': '50px'})


# Callback
@app.callback(
    Output('output-response', 'children'),
    Input('submit-btn', 'n_clicks'),
    Input('mic-btn', 'n_clicks'),
    State('user-input', 'value')
)
def handle_input(submit_clicks, mic_clicks, typed_query):
    global mic_query
    try:
        ctx = dash.callback_context
        if not ctx.triggered:
            return ""
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

        query = ""
        if trigger_id == "mic-btn":
            thread = threading.Thread(target=take_command)
            thread.start()
            thread.join()
            query = mic_query
        elif trigger_id == "submit-btn":
            query = typed_query

        if not query:
            return "❗ Please say or type something."

        query = query.lower()
        print("Query received:", query)

        # Stop
        if "stop" in query:
            say("Okay sir, have a great day!")
            return "Jarvis: Okay sir, have a great day!"

        # How are you
        if "how are you" in query:
            say("I'm doing great—thanks for asking!,how can I help you?")
            return "Jarvis: I'm doing great—thanks for asking!,how can I help you?"
        if "who are you" in query:
            say("I'm assisting you, as always. Ready to help!")
            return "Jarvis: I'm assisting you, as always. Ready to help!"
        # Hey or Hello
        if "hello jarvis" in query or "hey jarvis" in query or " hi jarvis" in query:
            say("Hello sir! How can I assist you today?")
            return "Jarvis: Hello sir! How can I assist you today?"
        #hello to name
        if "say hello to" in query.lower():
            # Extract the name using a regular expression
            match = re.search(r"say hello to ([a-zA-Z]+)", query.lower())
            if match:
                name = match.group(1).capitalize()
                response = f"Hello {name}! It's always a pleasure to hear from you. I hope you're feeling fantastic today. Is there any kind of help you need from me?"
                say(response)
                return f"Jarvis: {response}"
            else:
                return "Jarvis: I didn't catch the name. Please say 'Say hello to [name]'."

        # Time
        if "time" in query:
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            say(f"The time is {current_time}")
            return f"Jarvis: The time is {current_time}"

        # Open websites
        sites = [
            ["youtube", "https://www.youtube.com"],
            ["google", "https://www.google.com"],
            ["wikipedia", "https://www.wikipedia.org"],
            ["gmail", "https://mail.google.com"],
            ["github", "https://github.com"],
            ["stackoverflow", "https://stackoverflow.com"],
            ["gpt", "https://chat.openai.com"],
            ["instagram", "https://www.instagram.com"],
            ["facebook", "https://www.facebook.com"],
            ["linkedin", "https://www.linkedin.com"],
            ["twitter", "https://twitter.com"],
            ["amazon", "https://www.amazon.in"],
            ["flipkart", "https://www.flipkart.com"],
            ["netflix", "https://www.netflix.com"],
            ["spotify", "https://open.spotify.com"],
            ["coursera", "https://www.coursera.org"],
            ["udemy", "https://www.udemy.com"],
            ["reddit", "https://www.reddit.com"],
            ["quora", "https://www.quora.com"]
        ]
        for site in sites:
            if f"open {site[0]}" in query:
                say(f"Sure sir ! ,Opening {site[0]}")
                webbrowser.open(site[1])
                return f"Jarvis: Opening {site[0]}"


        # GPT Response
        gpt_reply = chat_with_gpt(query)
        say(gpt_reply)
        return f"Jarvis: {gpt_reply}"

    except Exception as e:
        return f"⚠️ Error: {str(e)}"





# Run Server
if __name__ == '__main__':
    app.run(debug=True)
