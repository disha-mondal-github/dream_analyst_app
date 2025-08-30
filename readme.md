# Dream Analyst App

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Technical Stack](#technical-stack)
4. [Setup](#setup)
5. [Deployment](#deployment)

## 🚀 Project Overview

**Dream Analyst** is an AI-powered web application that helps users analyze and interpret their dreams using advanced natural language processing. The app provides psychological insights, emotional tone analysis, and personalized dream interpretation through conversational AI.

### Key Value Propositions:
- **AI-Powered Analysis**: Leverages Mistral AI's advanced language models for accurate dream interpretation
- **Mental Health Awareness**: Built-in crisis detection with immediate mental health resource provision
- **Personalized Experience**: User accounts with dream history, analytics, and personalized insights
- **Beautiful Interface**: Dream-themed UI with smooth animations and intuitive design

## 🌟 Features

### Core Functionality
- **Dream Analysis**: AI-powered interpretation of dream content with psychological insights
- **Emotional Analysis**: Mood and emotion detection from dream narratives
- **Conversational Interface**: Natural follow-up conversations about dreams
- **Crisis Detection**: Automatic detection of concerning content with mental health resources

### User Management
- **Secure Authentication**: Email/password registration and login with password validation
- **Dream Journal**: Personal dream history with search and filtering capabilities
- **Analytics Dashboard**: Visual insights into dream patterns, moods, and common themes

### Additional Features
- **Export Functionality**: Download dreams as text or JSON files
- **Social Sharing**: Share insights on social media platforms
- **Therapist Chat**: AI-powered therapeutic conversations for emotional support
- **Responsive Design**: Works seamlessly on desktop and mobile devices

## 🛠️ Technical Stack

### Frameworks & Libraries
- **Streamlit** (1.49.1) - Web application framework
- **Mistral AI** (1.7.0) - Large language model API for dream analysis
- **PyMongo** (4.12.1) - MongoDB database connector
- **Plotly** (6.3.0) - Interactive data visualizations
- **Pandas** (2.3.2) - Data manipulation and analysis

### Advanced Techniques Used
- **Function Calling**: Structured JSON responses from Mistral AI for mood analysis and keyword extraction
- **Prompt Engineering**: Carefully crafted system prompts for different AI roles (analyst, therapist)
- **Conversation Memory**: Context-aware follow-up conversations
- **Real-time Analytics**: Dynamic charts and statistics based on user data
- **Security**: Password hashing, input validation, and secure authentication

### Infrastructure
- **MongoDB Atlas**: Cloud database for user data and dream storage
- **Streamlit Community Cloud**: Deployment platform
- **Environment Management**: Secure handling of API keys and configuration

## Setup

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file with your API keys (see `.env.example`)
4. Run: `streamlit run app.py`

## Deployment

This app is deployed on [Streamlit Community Cloud](https://streamlit.io/cloud)