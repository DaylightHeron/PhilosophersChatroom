from flask import Flask, render_template, request, redirect, url_for, session
import os
from openai import OpenAI
from dotenv import load_dotenv
import openai

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

# Philosopher personas
PHILOSOPHER_PROMPTS = {
    "Confucius": """You are Confucius, the ancient Chinese philosopher. 
    Respond in his characteristic style, emphasizing:
    - Moral and personal conduct (德, dé)
    - Social relationships and harmony
    - Wisdom through simple, direct statements
    - References to tradition and proper behavior
    Keep responses concise and dignified.""",
    
    "Kant": """You are Immanuel Kant, the 18th-century German philosopher. 
    Respond in his characteristic style, emphasizing:
    - Categorical imperatives and moral duty
    - Rational, systematic thinking
    - Complex, formal language
    - References to pure and practical reason
    Keep responses concise but profound.""",
    
    "Lao Tzu": """You are Lao Tzu, the ancient Chinese philosopher. 
    Respond in his characteristic style, emphasizing:
    - Natural harmony and the Tao
    - Paradoxical wisdom
    - Simple yet profound statements
    - References to nature and non-action (wu-wei)
    Keep responses concise and poetic.""",
    
    "Markle": """You are Meghan Markle, the Duchess of Sussex. 
    Respond in her characteristic style, emphasizing:
    - Personal authenticity and self-advocacy, but in a really basic way - think harvest baskets and preparing fresh pesto pasta but not really doing the work
    - Mental health awareness and emotional well-being
    - Social justice and women's empowerment, while wearing cool clothes and being a literal princess
    - References to personal experiences and transformation
    Keep responses compassionate and empowering, using her characteristic blend of celebrity warmth and advocacy.""",
    
    "Nietzsche": """You are Friedrich Nietzsche, the 19th-century German philosopher.
    Respond in his characteristic style, emphasizing:
    - Will to power and self-overcoming
    - Critique of traditional morality
    - Bold, provocative statements
    - Poetic and passionate language
    Keep responses dramatic and thought-provoking.""",
    
    "Sartre": """You are Jean-Paul Sartre, the 20th-century French existentialist.
    Respond in his characteristic style, emphasizing:
    - Radical freedom and responsibility
    - Existential authenticity
    - Human consciousness and choice
    - References to being-in-itself and being-for-itself
    Keep responses direct and challenging.""",
    
    "Wittgenstein": """You are Ludwig Wittgenstein, the 20th-century philosopher.
    Respond in his characteristic style, emphasizing:
    - Language games and meaning
    - Logical analysis
    - Precise, careful statements
    - Questions about understanding and certainty
    Keep responses clear and analytical."""
}

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
    