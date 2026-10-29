import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import webbrowser
import datetime
import pyttsx3
import speech_recognition as sr
import threading
import requests
import re

# DeepSeek API Key
DEEPSEEK_API_KEY = "Replace with your actual DeepSeek API key"  # Replace with your actual DeepSeek API key

# Initialize Dash App
app = dash.Dash(__name__)
server = app.server

# Global variable to hold mic result
mic_query = ""

# Voice output function
def say(text):
    engine = pyttsx3.init()
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

# GPT function using DeepSeek
def chat_with_gpt(prompt):
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
        }
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        }
        response = requests.post("https://api.deepseek.com/v1/chat/completions", headers=headers, json=data)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        elif response.status_code == 401:
            return "\u274c Invalid DeepSeek API Key."
        else:
            return f"\u274c DeepSeek API Error {response.status_code}: {response.text}"
    except Exception as e:
        return f"\u26a0\ufe0f Error in DeepSeek API call: {e}"

# Layout
app.layout = html.Div([
    html.H1("Jarvis Dashboard", style={'textAlign': 'center', 'color': '#2c3e50'}),
    dcc.Input(id='user-input', type='text', placeholder='Ask Jarvis...', style={'width': '60%', 'padding': '10px'}),
    html.Button('Enter', id='submit-btn', n_clicks=0, style={'margin': '10px'}),
    html.Button('\ud83c\udfa7 Mic', id='mic-btn', n_clicks=0, style={'margin': '10px'}),
    html.Div(id='output-response', style={'marginTop': '30px', 'fontSize': '18px'}),

    html.Div([
        html.H2("\ud83d\udcf0 Today's Highlights", style={'marginTop': '40px', 'textAlign': 'center', 'color': '#34495e'}),
        html.Div([
            html.Div([
                html.Img(src="/assets/ai_transforming.jpg", style={'width': '100%', 'borderRadius': '15px'}),
                html.H4("AI is transforming the world!", style={'textAlign': 'center'}),
                html.P("From smart assistants to self-driving cars, artificial intelligence is changing how we live and work."),
            ], style={'width': '30%', 'margin': '10px'}),

            html.Div([
                html.Img(src="/assets/future_robo.jpg", style={'width': '100%', 'borderRadius': '15px'}),
                html.H4("Robots of the Future", style={'textAlign': 'center'}),
                html.P("Robots are no longer science fiction—they’re now part of healthcare, logistics, and even customer service."),
            ], style={'width': '30%', 'margin': '10px'}),

            html.Div([
                html.Img(src="/assets/power_of_code.jpg", style={'width': '100%', 'borderRadius': '15px'}),
                html.H4("The Power of Code", style={'textAlign': 'center'}),
                html.P("Learning to code opens doors to creativity, innovation, and career opportunities."),
            ], style={'width': '30%', 'margin': '10px'}),
        ], style={'display': 'flex', 'justifyContent': 'center', 'flexWrap': 'wrap'})
    ])

], style={
    'backgroundImage': 'url("https://picsum.photos/1600/1000")',
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
            return "\u2757 Please say or type something."

        query = query.lower()
        print("Query received:", query)

        if "stop" in query:
            say("Okay sir, have a great day!")
            return "Jarvis: Okay sir, have a great day!"
        if "how are you" in query:
            say("I'm doing great—thanks for asking!,how can I help you?")
            return "Jarvis: I'm doing great—thanks for asking!,how can I help you?"
        if "who are you" in query:
            say("I am Jarvis, your personal AI assistant—always here to help, answer the questions, and make your day a little easier!")
            return "Jarvis: I am your AI assistant Jarvis—ready to assist you!"
        if "hello jarvis" in query or "hey jarvis" in query or "hi jarvis" in query:
            say("Hello sir! How can I assist you today?")
            return "Jarvis: Hello sir! How can I assist you today?"

        if "fuck you jarvis" in query:
            say("Fuck you too sir ")
            return "Jarvis: Fuck you too sir"

        if "say hello to" in query:
            match = re.search(r"say hello to ([a-zA-Z]+)", query)
            if match:
                name = match.group(1).capitalize()
                response = f"Hello {name}! It's always a pleasure to hear from you. I hope you're feeling fantastic today. Is there any kind of help you need from me?"
                say(response)
                return f"Jarvis: {response}"
            else:
                return "Jarvis: I didn't catch the name. Please say 'Say hello to [name]'."
        if "time" in query:
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            say(f"The time is {current_time}")
            return f"Jarvis: The time is {current_time}"

        # Websites
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

        gpt_reply = chat_with_gpt(query)
        say(gpt_reply)
        return f"Jarvis: {gpt_reply}"

    except Exception as e:
        return f"\u26a0\ufe0f Error: {str(e)}"

# Run Server
if __name__ == '__main__':
    app.run(debug=True)