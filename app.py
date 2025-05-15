from flask import Flask, render_template, request, redirect, url_for, session
import os
from openai import OpenAI
from dotenv import load_dotenv
import openai

# Import philosopher prompts
from prompts import PHILOSOPHER_PROMPTS

# Load environment variables first
if os.environ.get('VERCEL_ENV') is None:  # We're not in Vercel
    load_dotenv()
    debug_mode = True
else:
    debug_mode = False

# Initialize Flask app with proper configuration
app = Flask(__name__)
app.config['ENV'] = 'production' if os.environ.get('VERCEL_ENV') else 'development'
app.config['DEBUG'] = debug_mode
# Add a secret key (required for session management)
app.secret_key = os.urandom(24)  # or use a fixed secret key from your environment variables

def get_philosophical_response(philosopher, question):
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        return "[Error: OpenAI API key not found. Please check your environment variables.]"
    
    try:
        client = OpenAI(api_key=api_key)
        
        # Build context from previous messages
        context = ""
        if 'messages' in session and len(session['messages']) > 0:
            # Get last 3 messages for context
            recent_messages = session['messages'][-3:]
            context = "\n".join([f"{msg['philosopher']}: {msg['text']}" for msg in recent_messages])
            
        # Add context to the prompt if it exists
        prompt = question
        if context:
            prompt = f"Previous conversation:\n{context}\n\nNow, please respond to: {question}"
        
        response = client.chat.completions.create(
            model="gpt-4.1-nano", # this is the model we're using. it works. do not change it!
            messages=[
                {"role": "system", "content": PHILOSOPHER_PROMPTS[philosopher]},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[Error: {str(e)}]"

@app.route("/")
def home():
    if 'messages' not in session:
        session['messages'] = []
    return render_template("index.html", messages=session['messages'])

@app.route("/send_message", methods=['POST'])
def send_message():
    if 'messages' not in session:
        session['messages'] = []
        
    philosopher = request.form.get('philosopher')
    question = request.form.get('message')

    if philosopher and question:
        # Check if this is a "tap in" request
        if question == "*taps in to respond to the conversation*":
            # For tap-in, don't add the user message, just get the philosopher's response
            response = get_philosophical_response(philosopher, "Please review the conversation and offer your philosophical perspective.")
            session['messages'].append({
                'philosopher': philosopher,
                'text': response
            })
        else:
            # Normal user question flow
            session['messages'].append({
                'philosopher': 'You',
                'text': question
            })
            
            response = get_philosophical_response(philosopher, question)
            session['messages'].append({
                'philosopher': philosopher,
                'text': response
            })
        session.modified = True
    
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=debug_mode)

# For Vercel deployment
app.debug = debug_mode
    