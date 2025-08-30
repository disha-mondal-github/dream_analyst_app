import streamlit as st
import os
import re
import json
from datetime import datetime, timedelta
import hashlib
import pymongo
from mistralai import Mistral
from dotenv import load_dotenv
import time
from collections import Counter
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import base64
from io import BytesIO

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Dream Analyst",
    page_icon="🌙",
    layout="wide",
    initial_sidebar_state="collapsed"
)
st.markdown("""
<style>
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
</style>
""", unsafe_allow_html=True)


# Custom CSS for dreamy interface
def load_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    /* Main background with gradient */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        font-family: 'Poppins', sans-serif;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom title styling */
    .dream-title {
        font-size: 4rem;
        font-weight: 700;
        text-align: center;
        background: linear-gradient(45deg, #FFD700, #FF69B4, #87CEEB);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        animation: glow 2s ease-in-out infinite alternate;
    }
    
    @keyframes glow {
        from { filter: drop-shadow(0 0 5px rgba(255, 215, 0, 0.5)); }
        to { filter: drop-shadow(0 0 20px rgba(255, 105, 180, 0.8)); }
    }
    
    /* Quote styling - only shown on homepage */
    .dream-quote {
        font-size: 1.3rem;
        font-style: italic;
        text-align: center;
        color: #E6E6FA;
        margin: 2rem 0;
        padding: 1rem;
        border-radius: 15px;
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.8rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px 0 rgba(31, 38, 135, 0.2);
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px 0 rgba(31, 38, 135, 0.3);
        background: linear-gradient(45deg, #FF5252, #26C6DA);
    }
    
    /* Card styling */
    .dream-card {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        border: 1px solid rgba(255, 255, 255, 0.18);
    }
    
    /* Hide empty dream cards */
    .dream-card:empty {
        display: none;
    }
    
    /* Stats card styling */
    .stats-card {
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(15px);
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        border: 1px solid rgba(255, 255, 255, 0.18);
        transition: transform 0.3s ease;
    }
    
    .stats-card:hover {
        transform: translateY(-5px);
    }
    
    .stat-number {
        font-size: 2.5rem;
        font-weight: 700;
        color: #FFD700;
        margin-bottom: 0.5rem;
    }
    
    .stat-label {
        font-size: 1rem;
        color: #E6E6FA;
        font-weight: 400;
    }
    
    /* Input field styling */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 15px;
        color: white;
        padding: 0.8rem;
    }
    
    .stTextArea > div > div > textarea {
        background: rgba(255, 255, 255, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 15px;
        color: white;
        padding: 0.8rem;
    }
    
    /* Chat message styling */
    .chat-message {
        padding: 1rem;
        border-radius: 15px;
        margin: 1rem 0;
        animation: fadeIn 0.5s ease-in;
    }
    
    .user-message {
        background: rgba(255, 107, 107, 0.3);
        margin-left: 2rem;
        border-left: 4px solid #FF6B6B;
    }
    
    .analyst-message {
        background: rgba(78, 205, 196, 0.3);
        margin-right: 2rem;
        border-left: 4px solid #4ECDC4;
    }
    
    .therapist-message {
        background: rgba(255, 182, 193, 0.3);
        margin-right: 2rem;
        border-left: 4px solid #FFB6C1;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Dream figure animation */
    .dream-figure {
        font-size: 8rem;
        text-align: center;
        animation: float 3s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-20px); }
    }
    
    /* Success/error messages */
    .success-message {
        background: rgba(76, 175, 80, 0.3);
        color: #E8F5E8;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .error-message {
        background: rgba(244, 67, 54, 0.3);
        color: #FFEBEE;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    /* Share buttons */
    .share-buttons {
        display: flex;
        gap: 10px;
        justify-content: center;
        margin: 1rem 0;
    }
    
    .share-btn {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
        border: none;
        border-radius: 25px;
        padding: 0.8rem 1.5rem;
        color: white !important;
        text-decoration: none;
        transition: all 0.3s ease;
        font-weight: 600;
        cursor: pointer;
        display: inline-block;
        text-align: center;
        box-shadow: 0 4px 15px 0 rgba(31, 38, 135, 0.2);
        margin: 0.5rem;
    }
    
    .share-btn:hover {
        background: linear-gradient(45deg, #FF5252, #26C6DA);
        transform: translateY(-3px);
        box-shadow: 0 8px 25px 0 rgba(31, 38, 135, 0.3);
        color: white !important;
        text-decoration: none;
    }
    
    /* Mood indicator */
    .mood-indicator {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 500;
        margin: 0.2rem;
    }
    
    .mood-positive { background: rgba(76, 175, 80, 0.4); color: #E8F5E8; }
    .mood-neutral { background: rgba(255, 193, 7, 0.4); color: #FFF3C4; }
    .mood-negative { background: rgba(244, 67, 54, 0.4); color: #FFEBEE; }
    .mood-mysterious { background: rgba(156, 39, 176, 0.4); color: #F3E5F5; }
    
    /* White text for better visibility */
    .white-text {
        color: white !important;
        font-weight: bold;
    }
    
    /* Email display styling - FIXED */
    .user-email {
        color: white !important;
        font-weight: bold;
        font-size: 1.1rem;
    }
    
    /* Remove empty box */
    .empty-box {
        display: none;
    }
    
    /* Ensure all text in buttons is white */
    a.share-btn, a.share-btn:visited, a.share-btn:hover {
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# MongoDB connection function
@st.cache_resource
def connect_to_mongodb():
    """Connect to MongoDB with caching"""
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    
    if not mongo_uri or mongo_uri == "mongodb://localhost:27017":
        return None

    connection_options = [
        {},
        {"tls": True, "tlsAllowInvalidCertificates": True}
    ]

    for i, options in enumerate(connection_options):
        try:
            client = pymongo.MongoClient(mongo_uri, **options, serverSelectionTimeoutMS=5000)
            client.admin.command('ping')
            return client
        except Exception:
            continue
    return None

# Initialize connections
@st.cache_resource
def initialize_clients():
    """Initialize MongoDB and Mistral clients"""
    mongo_client = connect_to_mongodb()
    db = None
    users_collection = None
    dreams_collection = None
    
    if mongo_client:
        db = mongo_client["dream_analyst"]
        users_collection = db["users"]
        dreams_collection = db["dreams"]
    
    mistral_api_key = os.getenv("MISTRAL_API_KEY")
    mistral_client = None
    if mistral_api_key:
        mistral_client = Mistral(api_key=mistral_api_key)
    
    return mongo_client, users_collection, dreams_collection, mistral_client

# Authentication functions
def is_valid_password(password):
    """Check if password meets requirements"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one number"
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character"
    return True, "Password is valid"

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def is_valid_email(email):
    """Simple email validation"""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None

def register_user(users_collection, email, password):
    """Register a new user"""
    if users_collection.find_one({"email": email}):
        return False, "Email already registered"
    
    hashed_password = hash_password(password)
    user_data = {
        "email": email,
        "password": hashed_password,
        "created_at": datetime.now(),
        "last_login": datetime.now()
    }
    
    users_collection.insert_one(user_data)
    return True, "Registration successful"

def login_user(users_collection, email, password):
    """Login user"""
    hashed_password = hash_password(password)
    user = users_collection.find_one({"email": email})
    
    if not user or user["password"] != hashed_password:
        return False, "Invalid email or password"
    
    users_collection.update_one(
        {"email": email},
        {"$set": {"last_login": datetime.now()}}
    )
    
    return True, "Login successful"

# Dream analysis functions
def extract_keywords(conversation, mistral_client):
    """Extract keywords from conversation"""
    try:
        system_prompt = """
        Extract 5-10 key thematic words or phrases from this dream analysis conversation.
        Focus on important symbols, emotions, and interpretations.
        Return ONLY a JSON object with a "keywords" field containing an array of strings.
        Example: {"keywords": ["flying", "falling", "childhood home", "water", "transformation"]}
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": conversation}
        ]
        
        response = mistral_client.chat.complete(
            model="mistral-large-latest",
            messages=messages,
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        response_text = response.choices[0].message.content
        keywords = json.loads(response_text).get("keywords", [])
        return keywords if keywords else ["dream", "analysis"]
    except Exception:
        return ["dream", "analysis"]

def analyze_dream_mood(dream_text, mistral_client):
    """Analyze the mood/emotional tone of a dream"""
    try:
        system_prompt = """
        Analyze the emotional tone and mood of this dream. 
        Return ONLY a JSON object with "mood" (positive/neutral/negative/mysterious) and "emotions" (array of 2-3 key emotions).
        Example: {"mood": "mysterious", "emotions": ["curiosity", "anxiety", "wonder"]}
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": dream_text}
        ]
        
        response = mistral_client.chat.complete(
            model="mistral-large-latest",
            messages=messages,
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        response_text = response.choices[0].message.content
        mood_data = json.loads(response_text)
        return mood_data.get("mood", "neutral"), mood_data.get("emotions", ["calm"])
    except Exception:
        return "neutral", ["calm"]

def analyze_dream(dream_text, mistral_client, user_email=None, previous_dreams=None):
    """Analyze dream using Mistral AI with crisis detection"""
    # Crisis detection - check if dream contains concerning content
    crisis_keywords = [
        "suicid", "kill myself", "end my life", "don't want to live", 
        "self-harm", "cut myself", "hurt myself", "die", "death",
        "hopeless", "no reason to live", "no point", "can't go on",
        "give up", "too much pain", "better off without me"
    ]
    
    mental_health_resources = {
        "india": "Tele-MANAS: 14416 (24/7), Parivarthan: +91-7676602602",
        "united states": "988 Suicide & Crisis Lifeline, Crisis Text Line: Text HOME to 741741",
        "uk": "Samaritans: 116 123, Shout: Text 85258",
        "united kingdom": "Samaritans: 116 123, Shout: Text 85258",
        "australia": "Lifeline: 13 11 14, Beyond Blue: 1300 22 4636",
        "canada": "Crisis Services Canada: 1-833-456-4566"
    }
    
    global_resource = "International Association for Suicide Prevention (IASP): https://findahelpline.com"
    
    # Check for crisis keywords in the dream text
    crisis_detected = any(keyword in dream_text.lower() for keyword in crisis_keywords)
    
    # If crisis is detected, prioritize crisis response over dream analysis
    if crisis_detected:
        crisis_response = """
        I'm genuinely concerned about what you've shared. Dreams about suicide or self-harm can be very distressing, and I want to make sure you have immediate support.

        Your safety and wellbeing are the most important things right now. Please know that help is available, and you don't have to go through these feelings alone.

        Could you tell me which country you're in so I can provide the most relevant crisis resources? In the meantime, here are some international resources:

        International Association for Suicide Prevention: https://findahelpline.com

        Please reach out to these resources. They have trained professionals available 24/7 who can provide immediate support.
        """
        return crisis_response
    
    # If no crisis detected, proceed with normal dream analysis
    system_prompt = """
    You are a professional dream analyst with expertise in psychology, symbolism, and interpretation.
    
    Your responses should be warm, natural, and conversational. DO NOT use numbered lists or section headings.
    Flow naturally from one idea to another as if having a thoughtful conversation.
    
    When analyzing dreams:
    - Begin with a warm acknowledgment and brief overall impression of the dream
    - Weave interpretations of symbols, psychological perspectives, and real-life connections together naturally
    - Avoid clinical language - speak as a wise, empathetic friend would
    - Ask only ONE thoughtful question per response
    - If you reference previous dreams, do so naturally within your analysis
    """
    
    if previous_dreams:
        previous_dreams_context = "\n".join([
            f"Previous dream ({dream['date'].strftime('%Y-%m-%d')}): {dream['dream_text'][:150]}..."
            for dream in previous_dreams[:3]
        ])
        system_prompt += f"\n\nPrevious dreams context:\n{previous_dreams_context}"
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Here is my dream: {dream_text}"}
    ]
    
    try:
        response = mistral_client.chat.complete(
            model="mistral-large-latest",
            messages=messages,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"I apologize, but I'm having trouble analyzing your dream right now. Error: {str(e)}"

def save_dream(dreams_collection, user_email, dream_text, analysis, conversation, keywords, mood=None, emotions=None):
    """Save dream to database"""
    dream_data = {
        "user_email": user_email,
        "dream_text": dream_text,
        "analysis": analysis,
        "conversation": conversation,
        "keywords": keywords,
        "mood": mood or "neutral",
        "emotions": emotions or [],
        "date": datetime.now()
    }
    
    result = dreams_collection.insert_one(dream_data)
    return result.inserted_id

def get_user_previous_dreams(dreams_collection, user_email, limit=5):
    """Get user's previous dreams"""
    cursor = dreams_collection.find(
        {"user_email": user_email}
    ).sort("date", pymongo.DESCENDING).limit(limit)
    
    return list(cursor)

def search_user_dreams(dreams_collection, user_email, search_term=None, date_filter=None, mood_filter=None):
    """Search user's dreams with filters"""
    query = {"user_email": user_email}
    
    if search_term:
        query["$or"] = [
            {"dream_text": {"$regex": search_term, "$options": "i"}},
            {"keywords": {"$regex": search_term, "$options": "i"}}
        ]
    
    if date_filter:
        start_date = datetime.combine(date_filter, datetime.min.time())
        end_date = datetime.combine(date_filter, datetime.max.time())
        query["date"] = {"$gte": start_date, "$lte": end_date}
    
    if mood_filter and mood_filter != "All":
        query["mood"] = mood_filter.lower()
    
    cursor = dreams_collection.find(query).sort("date", pymongo.DESCENDING)
    return list(cursor)

def get_dream_statistics(dreams_collection, user_email):
    """Get user's dream statistics"""
    try:
        dreams = list(dreams_collection.find({"user_email": user_email}))
        
        if not dreams:
            return None
        
        total_dreams = len(dreams)
        
        # Most recent dream
        most_recent = max(dreams, key=lambda x: x['date'])
        days_since_last = (datetime.now() - most_recent['date']).days
        
        # Keyword frequency
        all_keywords = []
        all_moods = []
        all_emotions = []
        
        for dream in dreams:
            all_keywords.extend(dream.get('keywords', []))
            if dream.get('mood'):
                all_moods.append(dream['mood'])
            all_emotions.extend(dream.get('emotions', []))
        
        keyword_counts = Counter(all_keywords)
        mood_counts = Counter(all_moods)
        emotion_counts = Counter(all_emotions)
        
        # Dreams per month (last 6 months)
        six_months_ago = datetime.now() - timedelta(days=180)
        recent_dreams = [d for d in dreams if d['date'] > six_months_ago]
        
        monthly_counts = {}
        for dream in recent_dreams:
            month_key = dream['date'].strftime('%Y-%m')
            monthly_counts[month_key] = monthly_counts.get(month_key, 0) + 1
        
        return {
            'total_dreams': total_dreams,
            'days_since_last': days_since_last,
            'most_common_keywords': keyword_counts.most_common(5),
            'mood_distribution': dict(mood_counts),
            'most_common_emotions': emotion_counts.most_common(3),
            'monthly_counts': monthly_counts
        }
    except Exception:
        return None

def create_download_link(content, filename, file_format="txt"):
    """Create a download link for dream content with consistent styling"""
    if file_format == "txt":
        b64 = base64.b64encode(content.encode()).decode()
        href = f'<a href="data:text/plain;base64,{b64}" download="{filename}" class="share-btn">&#128221; Download as Text</a>'
    elif file_format == "json":
        b64 = base64.b64encode(json.dumps(content, default=str, indent=2).encode()).decode()
        href = f'<a href="data:application/json;base64,{b64}" download="{filename}" class="share-btn">&#128203; Download as JSON</a>'
    
    return href

def therapist_chat(user_input, conversation_history, mistral_client, user_email):
    """Handle therapist conversation with crisis detection"""
    crisis_keywords = [
        "suicid", "kill myself", "end my life", "don't want to live", 
        "self-harm", "cut myself", "hurt myself", "die", "death",
        "hopeless", "no reason to live", "no point", "can't go on",
        "give up", "too much pain", "better off without me"
    ]
    
    mental_health_resources = {
        "india": "Tele-MANAS: 14416 (24/7), Parivarthan: +91-7676602602",
        "united states": "988 Suicide & Crisis Lifeline, Crisis Text Line: Text HOME to 741741",
        "uk": "Samaritans: 116 123, Shout: Text 85258",
        "united kingdom": "Samaritans: 116 123, Shout: Text 85258",
        "australia": "Lifeline: 13 11 14, Beyond Blue: 1300 22 4636",
        "canada": "Crisis Services Canada: 1-833-456-4566"
    }
    
    global_resource = "International Association for Suicide Prevention (IASP): https://findahelpline.com"
    
    # Check for crisis keywords
    crisis_mode = any(keyword in user_input.lower() for keyword in crisis_keywords)
    
    # Check if we already asked for country
    asked_for_country = any("which country are you in" in msg["content"].lower() or 
                           "what country are you in" in msg["content"].lower() 
                           for msg in conversation_history if msg["role"] == "therapist")
    
    # Check if user already provided country
    user_country = None
    for msg in conversation_history:
        if msg["role"] == "user":
            for country in mental_health_resources.keys():
                if country in msg["content"].lower():
                    user_country = country
                    break
            if user_country:
                break
    
    system_prompt = f"""
    You are a compassionate, professional therapist. Your responses should be warm, supportive, and conversational.
    
    Guidelines for your responses:
    - Be empathetic and non-judgmental
    - Use a warm, conversational tone
    - Ask thoughtful, open-ended questions (only one per response)
    - Avoid clinical language or jargon
    - Provide gentle guidance and validation
    - Practice active listening in your responses
    """
    
    # Add crisis instructions if in crisis mode
    if crisis_mode:
        system_prompt += f"""
        
        CRITICAL: MENTAL HEALTH CRISIS PROTOCOL
        
        The user has mentioned concerning content that suggests they may be in crisis.
        
        Follow these steps exactly:
        1. Express empathy and validation for their feelings
        2. If we don't know their country yet, ask: "I'm concerned about you. Could you tell me which country you're in so I can provide the most relevant resources?"
        3. If we know their country, provide the appropriate crisis resources
        4. Encourage them to reach out to these resources immediately
        5. Remind them that they're not alone and help is available
        
        Available resources:
        {json.dumps(mental_health_resources, indent=2)}
        Global resource: {global_resource}
        
        This is your HIGHEST PRIORITY. Provide specific helpline numbers when possible.
        """
    
    # Build conversation context
    conversation_context = ""
    for msg in conversation_history:
        role = "User" if msg["role"] == "user" else "Therapist"
        conversation_context += f"{role}: {msg['content']}\n\n"
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Previous conversation: {conversation_context}\nUser's latest message: {user_input}"}
    ]
    
    try:
        response = mistral_client.chat.complete(
            model="mistral-large-latest",
            messages=messages,
            temperature=0.7
        )
        
        therapist_response = response.choices[0].message.content
        
        # If in crisis mode and we know the country but therapist didn't include resources,
        # manually append the appropriate resources
        if crisis_mode and user_country and user_country in mental_health_resources:
            if mental_health_resources[user_country].lower() not in therapist_response.lower():
                therapist_response += f"\n\nPlease reach out to these resources immediately: {mental_health_resources[user_country]}"
        
        # If in crisis mode but no country known and therapist didn't ask for it,
        # manually prompt for country
        elif crisis_mode and not user_country and not asked_for_country:
            if "country" not in therapist_response.lower() and "where are you" not in therapist_response.lower():
                therapist_response += "\n\nI'm concerned about you. Could you tell me which country you're in so I can provide the most relevant resources?"
        
        return therapist_response
        
    except Exception as e:
        # Fallback response that includes crisis resources
        if crisis_mode:
            crisis_response = "I'm really concerned about what you're sharing. It sounds like you're going through an incredibly difficult time."
            
            if user_country and user_country in mental_health_resources:
                crisis_response += f" Please reach out to these resources immediately: {mental_health_resources[user_country]}"
            elif not asked_for_country:
                crisis_response += " Could you tell me which country you're in so I can provide the most relevant resources?"
            else:
                crisis_response += f" Here are some global resources: {global_resource}"
                
            return crisis_response
        return "I appreciate you sharing that with me. Could you tell me more about how you're feeling about this situation?"
# Page functions
def show_homepage():
    """Display homepage with quote and buttons"""
    load_css()
    
    st.markdown('<h1 class="dream-title">&#127769;&#10024; Dream Analyst &#10024;&#127769;</h1>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="dream-figure">&#127756;</div>', unsafe_allow_html=True)
    
    quotes = [
        "Dreams are the touchstones of our characters. - Henry David Thoreau",
        "All that we see or seem is but a dream within a dream. - Edgar Allan Poe",
        "Dreams are illustrations from the book your soul is writing about you. - Marsha Norman",
        "The future belongs to those who believe in the beauty of their dreams. - Eleanor Roosevelt",
        "Dreams are the seeds of change. Nothing ever grows without a seed. - Debby Boone"
    ]
    
    import random
    selected_quote = random.choice(quotes)
    st.markdown(f'<div class="dream-quote">"{selected_quote}"</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("&#127379; Use for Free", key="free_btn", use_container_width=True):
                st.session_state.page = "free_analysis"
                st.rerun()
        
        with col_b:
            if st.button("&#128274; Sign In", key="signin_btn", use_container_width=True):
                st.session_state.page = "auth"
                st.rerun()

def show_auth_page():
    """Display authentication page"""
    load_css()
    
    _, users_collection, dreams_collection, mistral_client = initialize_clients()
    
    st.markdown('<h1 class="dream-title">&#128274; Account Access</h1>', unsafe_allow_html=True)
    
    if st.button("&#11013; Back to Home"):
        st.session_state.page = "home"
        st.rerun()
    
    tab1, tab2 = st.tabs(["Sign In", "Register"])
    
    with tab1:
        st.markdown('<div class="dream-card">', unsafe_allow_html=True)
        st.subheader("Welcome Back! &#128075;")
        
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="Enter your email")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submit = st.form_submit_button("Sign In", use_container_width=True)
            
            if submit:
                if users_collection is None:
                    st.error("Database connection failed. Please try again later.")
                    return
                
                if email and password:
                    success, message = login_user(users_collection, email, password)
                    if success:
                        st.session_state.user_email = email
                        st.session_state.page = "dashboard"
                        st.success("Login successful! Redirecting...")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("Please fill in all fields")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="dream-card">', unsafe_allow_html=True)
        st.subheader("Create Your Account &#10024;")
        
        with st.form("register_form"):
            email = st.text_input("Email", placeholder="Enter your email")
            password = st.text_input("Password", type="password", placeholder="Create a password")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
            submit = st.form_submit_button("Register", use_container_width=True)
            
            if submit:
                if users_collection is None:
                    st.error("Database connection failed. Please try again later.")
                    return
                
                if email and password and confirm_password:
                    if not is_valid_email(email):
                        st.error("Please enter a valid email address")
                    elif password != confirm_password:
                        st.error("Passwords do not match")
                    else:
                        valid, message = is_valid_password(password)
                        if not valid:
                            st.error(message)
                        else:
                            success, message = register_user(users_collection, email, password)
                            if success:
                                st.session_state.user_email = email
                                st.session_state.page = "dashboard"
                                st.success("Registration successful! Redirecting...")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(message)
                else:
                    st.error("Please fill in all fields")
        
        with st.expander("Password Requirements"):
            st.write("""
            - At least 8 characters long
            - At least one uppercase letter
            - At least one lowercase letter
            - At least one number
            - At least one special character (!@#$%^&*(),.?\":{}|<>)"
            """)
        
        st.markdown('</div>', unsafe_allow_html=True)
def show_free_analysis():
    """Display free dream analysis page"""
    load_css()
    
    _, users_collection, dreams_collection, mistral_client = initialize_clients()
    
    st.markdown('<h1 class="dream-title">Free Dream Analysis</h1>', unsafe_allow_html=True)
    
    if st.button("&#11013; Back to Home"):
        st.session_state.page = "home"
        st.rerun()
    
    st.markdown('<div class="dream-card">', unsafe_allow_html=True)
    st.write("Describe your dream in detail and I'll help you understand its meaning...")
    
    dream_text = st.text_area(
        "Your Dream",
        placeholder="I had a dream where I was flying over a beautiful landscape...",
        height=150,
        help="The more details you provide, the better the analysis will be!"
    )
    
    if st.button("&#128302; Analyze My Dream", use_container_width=True):
        if dream_text.strip():
            if mistral_client is None:
                st.error("AI service is currently unavailable. Please try again later.")
                return
            
            with st.spinner("&#10024; Analyzing your dream..."):
                analysis = analyze_dream(dream_text, mistral_client)
                mood, emotions = analyze_dream_mood(dream_text, mistral_client)
            
            st.markdown("### &#128302; Dream Analysis")
            st.markdown(f'<div class="mood-indicator mood-{mood}">Mood: {mood.title()}</div>', unsafe_allow_html=True)
            for emotion in emotions[:3]:
                st.markdown(f'<div class="mood-indicator mood-neutral">{emotion}</div>', unsafe_allow_html=True)
            
            st.markdown(f'<div class="chat-message analyst-message"><strong>&#128302; Dream Analyst:</strong> {analysis}</div>', unsafe_allow_html=True)
            
            # Check for crisis keywords to show additional resources
            crisis_keywords = [
                "suicid", "kill myself", "end my life", "don't want to live", 
                "self-harm", "cut myself", "hurt myself", "die", "death",
                "hopeless", "no reason to live", "no point", "can't go on",
                "give up", "too much pain", "better off without me"
            ]
            
            crisis_detected = any(keyword in dream_text.lower() for keyword in crisis_keywords)
            
            if crisis_detected:
                st.markdown("### &#128680; Mental Health Support")
                st.warning("""
                **If you're experiencing thoughts of self-harm or suicide, please reach out for help immediately:**
                
                - **International:** International Association for Suicide Prevention: https://findahelpline.com
                - **US:** 988 Suicide & Crisis Lifeline
                - **UK:** Samaritans: 116 123
                - **India:** Tele-MANAS: 14416
                - **Australia:** Lifeline: 13 11 14
                - **Canada:** Crisis Services Canada: 1-833-456-4566
                
                You are not alone, and there are people who want to help.
                """)
            
            # Share buttons
            st.markdown("### &#127775; Share Your Analysis")
            share_text = f"Dream Analysis: {analysis[:100]}..."
            col1, col2, col3 = st.columns(3)
            
            with col1:
                twitter_url = f"https://twitter.com/intent/tweet?text={share_text.replace(' ', '%20')}"
                st.markdown(f'<a href="{twitter_url}" target="_blank" class="share-btn">&#128038; Twitter</a>', unsafe_allow_html=True)
            
            with col2:
                facebook_url = f"https://www.facebook.com/sharer/sharer.php?u=dreamanalyst.com"
                st.markdown(f'<a href="{facebook_url}" target="_blank" class="share-btn">&#128084; Facebook</a>', unsafe_allow_html=True)
            
            with col3:
                download_content = f"Dream: {dream_text}\n\nAnalysis: {analysis}\n\nMood: {mood}\nEmotions: {', '.join(emotions)}"
                download_link = create_download_link(download_content, "dream_analysis.txt")
                st.markdown(download_link, unsafe_allow_html=True)
            
            # Store in session for conversation
            st.session_state.current_dream = dream_text
            st.session_state.current_analysis = analysis
            st.session_state.conversation_history = [
                {"role": "analyst", "content": analysis}
            ]
            
            st.info("&#128161; Want to continue this conversation or save your dreams? Consider signing up for a free account!")
            
        else:
            st.error("Please describe your dream before analyzing.")
    
    # Continue conversation if analysis exists
    if hasattr(st.session_state, 'current_analysis'):
        st.markdown("### &#128172; Continue the Conversation")
        user_response = st.text_input("Ask a follow-up question or share more details...")
        
        if st.button("Send", key="continue_free"):
            if user_response.strip():
                st.session_state.conversation_history.append({
                    "role": "user", 
                    "content": user_response
                })
                
                # Check for crisis keywords in user response
                crisis_keywords = [
                    "suicid", "kill myself", "end my life", "don't want to live", 
                    "self-harm", "cut myself", "hurt myself", "die", "death",
                    "hopeless", "no reason to live", "no point", "can't go on",
                    "give up", "too much pain", "better off without me"
                ]
                
                crisis_detected = any(keyword in user_response.lower() for keyword in crisis_keywords)
                
                # If crisis is detected in the follow-up, prioritize crisis response
                if crisis_detected:
                    crisis_response = """
                    I'm really concerned about what you're sharing. It sounds like you're going through an incredibly difficult time right now.
                    
                    Your safety is the most important thing. Please reach out to these resources immediately:
                    
                    International Association for Suicide Prevention: https://findahelpline.com
                    
                    Could you tell me which country you're in so I can provide more specific resources? There are people available 24/7 who want to help and are trained to support you through this.
                    """
                    
                    st.session_state.conversation_history.append({
                        "role": "analyst",
                        "content": crisis_response
                    })
                    
                    st.rerun()
                else:
                    # Normal conversation continuation
                    conversation_context = f"Dream: {st.session_state.current_dream}\n\n"
                    for msg in st.session_state.conversation_history:
                        role = "Dream Analyst" if msg["role"] == "analyst" else "User"
                        conversation_context += f"{role}: {msg['content']}\n\n"
                    
                    system_prompt = """Continue the dream analysis conversation naturally. 
                    Be supportive and insightful. Ask only one question per response."""
                    
                    messages = [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"{conversation_context}User's latest message: {user_response}"}
                    ]
                    
                    try:
                        response = mistral_client.chat.complete(
                            model="mistral-large-latest",
                            messages=messages,
                            temperature=0.7
                        )
                        
                        ai_response = response.choices[0].message.content
                        st.session_state.conversation_history.append({
                            "role": "analyst",
                            "content": ai_response
                        })
                        
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Error continuing conversation: {str(e)}")
        
        # Display conversation history
        for i, msg in enumerate(st.session_state.conversation_history):
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-message user-message"><strong>You:</strong> {msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message analyst-message"><strong>&#128302; Dream Analyst:</strong> {msg["content"]}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_dashboard():
    """Display user dashboard"""
    load_css()
    
    _, users_collection, dreams_collection, mistral_client = initialize_clients()
    
    st.markdown('<h1 class="dream-title">&#127775;&#10024; Your Dream Journey &#10024;&#127775;</h1>', unsafe_allow_html=True)
    
    # User info and logout - FIXED: Email now uses user-email class
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f'<div class="user-email">Welcome back, {st.session_state.user_email}!</div>', unsafe_allow_html=True)
    with col2:
        if st.button("Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.session_state.page = "home"
            st.rerun()
    
    # Get user statistics
    stats = get_dream_statistics(dreams_collection, st.session_state.user_email)
    
    # Display statistics cards
    if stats:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f'''
            <div class="stats-card">
                <div class="stat-number">{stats['total_dreams']}</div>
                <div class="stat-label">Total Dreams</div>
            </div>
            ''', unsafe_allow_html=True)
        
        with col2:
            st.markdown(f'''
            <div class="stats-card">
                <div class="stat-number">{stats['days_since_last']}</div>
                <div class="stat-label">Days Since Last</div>
            </div>
            ''', unsafe_allow_html=True)
        
        with col3:
            most_common_keyword = stats['most_common_keywords'][0][0] if stats['most_common_keywords'] else "None"
            st.markdown(f'''
            <div class="stats-card">
                <div class="stat-number">"{most_common_keyword}"</div>
                <div class="stat-label">Top Symbol</div>
            </div>
            ''', unsafe_allow_html=True)
        
        with col4:
            most_common_mood = max(stats['mood_distribution'].items(), key=lambda x: x[1])[0] if stats['mood_distribution'] else "neutral"
            st.markdown(f'''
            <div class="stats-card">
                <div class="stat-number">{most_common_mood.title()}</div>
                <div class="stat-label">Common Mood</div>
            </div>
            ''', unsafe_allow_html=True)
    
    # Main dashboard tabs
    tab1, tab2, tab3, tab4 = st.tabs(["&#128302; Analyze Dream", "&#129489;&#8205;&#9877;&#65039; Talk to Therapist", "&#128216; Dream History", "&#128202; Analytics"])
    
    with tab1:
        st.markdown('<div class="dream-card">', unsafe_allow_html=True)
        st.subheader("Analyze Your Dream")
        
        dream_text = st.text_area(
            "Describe your dream in detail:",
            placeholder="I had a dream where...",
            height=150
        )
        
        if st.button("&#128302; Analyze Dream", use_container_width=True):
            if dream_text.strip():
                if mistral_client is None:
                    st.error("AI service is currently unavailable.")
                    return
                
                previous_dreams = get_user_previous_dreams(dreams_collection, st.session_state.user_email)
                
                with st.spinner("&#10024; Analyzing your dream..."):
                    analysis = analyze_dream(dream_text, mistral_client, st.session_state.user_email, previous_dreams)
                    mood, emotions = analyze_dream_mood(dream_text, mistral_client)
                
                st.markdown("### &#128302; Dream Analysis")
                st.markdown(f'<div class="mood-indicator mood-{mood}">Mood: {mood.title()}</div>', unsafe_allow_html=True)
                for emotion in emotions[:3]:
                    st.markdown(f'<div class="mood-indicator mood-neutral">{emotion}</div>', unsafe_allow_html=True)
                
                st.markdown(f'<div class="chat-message analyst-message"><strong>&#128302; Dream Analyst:</strong> {analysis}</div>', unsafe_allow_html=True)
                
                # Save dream
                conversation = f"Dream: {dream_text}\n\nAnalysis: {analysis}"
                keywords = extract_keywords(conversation, mistral_client)
                
                dream_id = save_dream(
                    dreams_collection,
                    st.session_state.user_email,
                    dream_text,
                    analysis,
                    conversation,
                    keywords,
                    mood,
                    emotions
                )
                
                st.success(f"&#9989; Dream saved successfully! (ID: {dream_id})")
                
                # Share options
                st.markdown("### &#127775; Share & Export")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    share_text = f"Just analyzed my dream with Dream Analyst! {analysis[:100]}..."
                    twitter_url = f"https://twitter.com/intent/tweet?text={share_text.replace(' ', '%20')}"
                    st.markdown(f'<a href="{twitter_url}" target="_blank" class="share-btn">&#128038; Share on Twitter</a>', unsafe_allow_html=True)
                
                with col2:
                    export_data = {
                        "dream": dream_text,
                        "analysis": analysis,
                        "mood": mood,
                        "emotions": emotions,
                        "keywords": keywords,
                        "date": datetime.now().isoformat()
                    }
                    json_link = create_download_link(export_data, f"dream_analysis_{dream_id}.json", "json")
                    st.markdown(json_link, unsafe_allow_html=True)
                
                with col3:
                    text_content = f"DREAM ANALYSIS REPORT\n\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\nDream:\n{dream_text}\n\nAnalysis:\n{analysis}\n\nMood: {mood}\nEmotions: {', '.join(emotions)}\nKeywords: {', '.join(keywords)}"
                    text_link = create_download_link(text_content, f"dream_report_{dream_id}.txt", "txt")
                    st.markdown(text_link, unsafe_allow_html=True)
                
                # Store for continued conversation
                st.session_state.current_dream_session = {
                    "dream_text": dream_text,
                    "analysis": analysis,
                    "conversation": conversation,
                    "dream_id": dream_id
                }
                
            else:
                st.error("Please describe your dream.")
        
        # Continue conversation
        if hasattr(st.session_state, 'current_dream_session'):
            st.markdown("### &#128172; Continue Conversation")
            
            if 'dream_conversation' not in st.session_state:
                st.session_state.dream_conversation = [
                    {"role": "analyst", "content": st.session_state.current_dream_session['analysis']}
                ]
            
            user_response = st.text_input("Ask questions or share more details...", key="dream_followup")
            
            if st.button("Send Message", key="send_dream_msg"):
                if user_response.strip():
                    st.session_state.dream_conversation.append({
                        "role": "user",
                        "content": user_response
                    })
                    
                    conversation_context = f"Dream: {st.session_state.current_dream_session['dream_text']}\n\n"
                    for msg in st.session_state.dream_conversation:
                        role = "Dream Analyst" if msg["role"] == "analyst" else "User"
                        conversation_context += f"{role}: {msg['content']}\n\n"
                    
                    system_prompt = """Continue the dream analysis conversation naturally. 
                    Be supportive and insightful. Ask only one question per response.
                    Watch for any mental health concerns and provide appropriate resources if needed."""
                    
                    messages = [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"{conversation_context}User's latest message: {user_response}"}
                    ]
                    
                    try:
                        response = mistral_client.chat.complete(
                            model="mistral-large-latest",
                            messages=messages,
                            temperature=0.7
                        )
                        
                        ai_response = response.choices[0].message.content
                        st.session_state.dream_conversation.append({
                            "role": "analyst",
                            "content": ai_response
                        })
                        
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Error continuing conversation: {str(e)}")
            
            # Display conversation
            for msg in st.session_state.dream_conversation:
                if msg["role"] == "user":
                    st.markdown(f'<div class="chat-message user-message"><strong>You:</strong> {msg["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-message analyst-message"><strong>&#128302; Dream Analyst:</strong> {msg["content"]}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="dream-card">', unsafe_allow_html=True)
        st.subheader("Talk to Our Therapist")
        st.write("Get emotional support and guidance from our AI therapist.")
        
        # Initialize therapist conversation
        if 'therapist_conversation' not in st.session_state:
            st.session_state.therapist_conversation = []
            
        if not st.session_state.therapist_conversation:
            welcome_message = "Hello! I'm here to provide support and a space for reflection. I'd love to understand how you're feeling today and what's on your mind. How are you doing?"
            st.session_state.therapist_conversation.append({
                "role": "therapist",
                "content": welcome_message
            })
        
        # Display conversation
        for msg in st.session_state.therapist_conversation:
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-message user-message"><strong>You:</strong> {msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message therapist-message"><strong>&#129489;&#8205;&#9877;&#65039; Therapist:</strong> {msg["content"]}</div>', unsafe_allow_html=True)
        
        # Chat input
        user_input = st.text_input("Your message:", key="therapist_input", placeholder="Share what's on your mind...")
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("Send", key="send_therapist"):
                if user_input.strip():
                    st.session_state.therapist_conversation.append({
                        "role": "user",
                        "content": user_input
                    })
                    
                    with st.spinner("Therapist is thinking..."):
                        response = therapist_chat(
                            user_input, 
                            st.session_state.therapist_conversation[:-1], 
                            mistral_client, 
                            st.session_state.user_email
                        )
                    
                    st.session_state.therapist_conversation.append({
                        "role": "therapist",
                        "content": response
                    })
                    
                    st.rerun()
        
        with col2:
            if st.button("Clear Conversation", key="clear_therapist"):
                st.session_state.therapist_conversation = []
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        st.markdown('<div class="dream-card">', unsafe_allow_html=True)
        st.subheader("Your Dream History")
        
        # Search and filter options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            search_term = st.text_input("&#128269; Search dreams:", placeholder="Enter keywords...")
        
        with col2:
            date_filter = st.date_input("&#128197; Filter by date:", value=None)
        
        with col3:
            mood_options = ["All", "Positive", "Neutral", "Negative", "Mysterious"]
            mood_filter = st.selectbox("&#128522; Filter by mood:", mood_options)
        
        if dreams_collection is not None:
            filtered_dreams = search_user_dreams(
                dreams_collection, 
                st.session_state.user_email, 
                search_term if search_term else None,
                date_filter,
                mood_filter
            )
            
            if filtered_dreams:
                st.write(f"Found {len(filtered_dreams)} dreams")
                
                for dream in filtered_dreams:
                    with st.expander(f"&#127769; Dream from {dream['date'].strftime('%Y-%m-%d %H:%M')}"):
                        # Dream content
                        st.write("**Dream:**")
                        st.write(dream['dream_text'][:300] + "..." if len(dream['dream_text']) > 300 else dream['dream_text'])
                        
                        # Mood and emotions
                        if dream.get('mood'):
                            st.markdown(f'<div class="mood-indicator mood-{dream["mood"]}">Mood: {dream["mood"].title()}</div>', unsafe_allow_html=True)
                        
                        if dream.get('emotions'):
                            for emotion in dream['emotions'][:3]:
                                st.markdown(f'<div class="mood-indicator mood-neutral">{emotion}</div>', unsafe_allow_html=True)
                        
                        # Actions
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            if st.button(f"View Full Analysis", key=f"view_{dream['_id']}"):
                                st.markdown(f"**Full Analysis:**\n\n{dream.get('analysis', 'No analysis available.')}")
                        
                        with col2:
                            dream_content = f"Dream from {dream['date'].strftime('%Y-%m-%d')}\n\nDream: {dream['dream_text']}\n\nAnalysis: {dream.get('analysis', '')}"
                            download_link = create_download_link(dream_content, f"dream_{dream['_id']}.txt")
                            st.markdown(download_link, unsafe_allow_html=True)
                        
                        with col3:
                            share_text = f"Dream from {dream['date'].strftime('%Y-%m-%d')}: {dream['dream_text'][:100]}..."
                            twitter_url = f"https://twitter.com/intent/tweet?text={share_text.replace(' ', '%20')}"
                            st.markdown(f'<a href="{twitter_url}" target="_blank" class="share-btn">&#128038; Share</a>', unsafe_allow_html=True)
            else:
                st.info("No dreams found matching your criteria. Try adjusting your filters or record your first dream!")
        else:
            st.error("Unable to connect to dream database.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab4:
        st.markdown('<div class="dream-card">', unsafe_allow_html=True)
        st.subheader("Dream Analytics & Insights")
        
        if stats and stats['total_dreams'] > 0:
            # Mood distribution pie chart
            if stats['mood_distribution']:
                st.markdown("#### &#128522; Mood Distribution")
                mood_df = pd.DataFrame(list(stats['mood_distribution'].items()), columns=['Mood', 'Count'])
                fig_mood = px.pie(mood_df, values='Count', names='Mood', 
                                color_discrete_sequence=px.colors.qualitative.Set3)
                fig_mood.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white'
                )
                st.plotly_chart(fig_mood, use_container_width=True)
            
            # Keyword frequency bar chart
            if stats['most_common_keywords']:
                st.markdown("#### &#128273; Most Common Dream Symbols")
                keywords_df = pd.DataFrame(stats['most_common_keywords'], columns=['Keyword', 'Frequency'])
                fig_keywords = px.bar(keywords_df, x='Keyword', y='Frequency',
                                    color='Frequency', color_continuous_scale='viridis')
                fig_keywords.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=False)
                )
                st.plotly_chart(fig_keywords, use_container_width=True)
            
            # Monthly dream frequency
            if stats['monthly_counts']:
                st.markdown("#### &#128197; Dreams Over Time")
                monthly_df = pd.DataFrame(list(stats['monthly_counts'].items()), columns=['Month', 'Dreams'])
                monthly_df['Month'] = pd.to_datetime(monthly_df['Month'])
                monthly_df = monthly_df.sort_values('Month')
                
                fig_monthly = px.line(monthly_df, x='Month', y='Dreams', 
                                    markers=True, line_shape='spline')
                fig_monthly.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=False)
                )
                fig_monthly.update_traces(line_color='#4ECDC4', marker_color='#FF6B6B')
                st.plotly_chart(fig_monthly, use_container_width=True)
            
            # Emotion analysis
            if stats['most_common_emotions']:
                st.markdown("#### &#10084;&#65039; Emotional Patterns")
                emotions_df = pd.DataFrame(stats['most_common_emotions'], columns=['Emotion', 'Frequency'])
                fig_emotions = px.bar(emotions_df, x='Emotion', y='Frequency', 
                                    color='Frequency', color_continuous_scale='plasma')
                fig_emotions.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=False)
                )
                st.plotly_chart(fig_emotions, use_container_width=True)
            
            # Dream insights
            st.markdown("#### &#129504; Personalized Insights")
            
            insights = []
            if stats['total_dreams'] >= 5:
                insights.append(f"&#127775; You're an active dreamer with {stats['total_dreams']} recorded dreams!")
            
            if stats['days_since_last'] == 0:
                insights.append("&#127381; You recorded a dream today - great job staying consistent!")
            elif stats['days_since_last'] <= 3:
                insights.append(f"&#9203; It's been {stats['days_since_last']} days since your last dream - keep up the good work!")
            
            if stats['most_common_keywords']:
                top_symbol = stats['most_common_keywords'][0][0]
                insights.append(f"&#128302; '{top_symbol}' appears frequently in your dreams - this might be a significant symbol for you.")
            
            if stats['mood_distribution']:
                dominant_mood = max(stats['mood_distribution'].items(), key=lambda x: x[1])[0]
                insights.append(f"&#128522; Your dreams tend to be {dominant_mood}, which may reflect your subconscious emotional state.")
            
            for insight in insights:
                st.info(insight)
            
            # Export full analytics
            st.markdown("#### &#128202; Export Your Data")
            
            full_analytics = {
                "user_email": st.session_state.user_email,
                "generated_at": datetime.now().isoformat(),
                "statistics": stats,
                "total_dreams_analyzed": stats['total_dreams']
            }
            
            analytics_link = create_download_link(full_analytics, "dream_analytics_report.json", "json")
            st.markdown(analytics_link, unsafe_allow_html=True)
        
        else:
            st.info("Record more dreams to unlock detailed analytics! Start by analyzing your first dream in the 'Analyze Dream' tab.")
        
        st.markdown('</div>', unsafe_allow_html=True)

# Main app logic
def main():
    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = "home"
    
    # Route to appropriate page
    if st.session_state.page == "home":
        show_homepage()
    elif st.session_state.page == "auth":
        show_auth_page()
    elif st.session_state.page == "free_analysis":
        show_free_analysis()
    elif st.session_state.page == "dashboard":
        show_dashboard()

if __name__ == "__main__":
    main()
