from flask import Flask, render_template, request, redirect, url_for
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Store messages in memory (they'll be lost when server restarts)
messages = []

# Initialize OpenAI client
api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key) if api_key else None

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
    if not client:
        return "[Error: OpenAI API key not found. Please check your .env file.]"
    
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[
                {"role": "system", "content": PHILOSOPHER_PROMPTS[philosopher]},
                {"role": "user", "content": question}
            ],
            max_tokens=200,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[Error: {str(e)}]"

@app.route("/")
def home():
    return render_template("index.html", messages=messages)

@app.route("/send_message", methods=['POST'])
def send_message():
    # Get the philosopher and question from the form
    philosopher = request.form.get('philosopher')
    question = request.form.get('message')
    
    # Check if the philosopher and question are provided
    if philosopher and question:
        # Add the user's question
        messages.append({
            'philosopher': 'You',
            'text': question
        })
        
        # Get and add the philosopher's response
        response = get_philosophical_response(philosopher, question)
        messages.append({
            'philosopher': philosopher,
            'text': response
        })
    
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)   # auto-reloads when you saveß
    