# Classroom Copilot

## Project Overview

Classroom Copilot is a Voice-Enabled AI Teaching Assistant designed for government schools.

The target user is a teacher conducting a live classroom session using a smart board.

Students primarily speak Hinglish (Hindi + English), so all AI responses should support natural bilingual communication.

The objective is to create a functional AI-powered classroom copilot that helps teachers explain concepts, conduct quizzes, translate content, and guide classroom activities entirely through voice commands.

This is a prototype project being built for an AI assignment.

The focus is:

* Human-centered design
* Fast response time
* Voice-first interaction
* Educational usefulness
* Demonstration of AI capabilities

Production-grade infrastructure is NOT required.

---

# Assignment Requirements

Implement ALL FOUR features:

## Feature 1: Live Concept Simplification

Teacher speaks:

"Explain photosynthesis to class 6"

System should:

1. Convert speech to text.
2. Understand educational intent.
3. Generate a simplified Hinglish explanation.
4. Speak the explanation aloud.
5. Display explanation visually.
6. Generate a simple educational diagram.

Example:

Input:

Explain photosynthesis to class 6 students.

Output:

* Hinglish explanation
* Diagram showing sunlight → plant → food production
* Audio explanation

---

## Feature 2: Voice Triggered Quizzing

Teacher speaks:

"Create a quiz on photosynthesis"

System should:

1. Detect quiz intent.
2. Generate 5 multiple choice questions.
3. Display questions visually.
4. Read questions aloud.
5. Show answers when requested.

Output:

Question
Options
Correct Answer

---

## Feature 3: Bilingual Dictation and Translation

Teacher speaks:

"Translate this paragraph"

System should:

1. Transcribe spoken content.
2. Translate English ↔ Hindi.
3. Display both versions side by side.
4. Read translated content aloud.

Output:

English Text

Hindi Translation

---

## Feature 4: Hands-Free Activity Guide

Teacher speaks:

"Start a 3 minute group discussion activity"

System should:

1. Generate activity instructions.
2. Display instructions.
3. Read instructions aloud.
4. Start countdown timer.
5. Show remaining time on screen.

Output:

Step-by-step activity instructions

Countdown timer

Completion notification

---

# User Flow

Teacher clicks microphone.

Teacher speaks command.

Speech is converted to text.

System classifies intent.

System routes request to appropriate module.

AI generates response.

Response is displayed visually.

Response is spoken aloud.

Teacher continues teaching.

---

# Intent Detection

System should classify user requests into one of:

* concept_simplification
* quiz_generation
* translation
* activity_guide

Examples:

"Explain photosynthesis"

→ concept_simplification

"Create a quiz on photosynthesis"

→ quiz_generation

"Translate this paragraph"

→ translation

"Start a 5 minute activity"

→ activity_guide

---

# Technical Architecture

Voice Input
↓
Speech To Text
↓
Intent Detection
↓
Feature Router
↓
Gemini AI
↓
Visual Response
↓
Text To Speech
↓
Audio Output

---

# Tech Stack

Frontend:

* Gradio

Backend:

* Python

AI Model:

* Gemini 2.5 Flash

Speech To Text:

* Faster Whisper

Text To Speech:

* Edge TTS

Deployment:

* Hugging Face Spaces preferred
  OR
* Render

---

# Design Principles

The application should be:

* Simple
* Fast
* Classroom-friendly
* Large smart-board UI
* Minimal clicks
* Teacher-focused

Avoid complicated workflows.

Teacher should be able to operate system with almost no training.

---

# UI Requirements

Single page application.

Layout:

---

Title

Classroom Copilot

---

Voice Input Section

Microphone Button

Recognized Speech Text

---

Response Section

Generated Content

---

Visual Section

Educational Diagram
Quiz
Translation
or Activity Instructions

---

Audio Controls

Play Audio

---

Timer Section

Visible only for activity mode

---

# Diagram Generation

Do NOT generate complex AI images.

Use simple Mermaid diagrams or SVG diagrams.

Examples:

Photosynthesis

Sunlight
↓
Plant
↓
Food Production

Water Cycle

Evaporation
↓
Clouds
↓
Rain
↓
Collection

Diagrams must be generated dynamically.

---

# Prompt Engineering Rules

All educational explanations should:

* Be age appropriate.
* Be concise.
* Use Hinglish.
* Avoid complex terminology.
* Be engaging.

Prompt should accept:

* Topic
* Grade Level
* Language Preference

Example:

Explain photosynthesis for Class 6 students in simple Hinglish.

---

# Quiz Rules

Generate:

* 5 MCQs
* 4 options each
* Correct answer

Difficulty:

Easy

Student friendly

Classroom appropriate

---

# Translation Rules

Support:

English → Hindi

Hindi → English

Preserve educational meaning.

Avoid literal word-by-word translation.

---

# Activity Guide Rules

Generate:

* Activity title
* Instructions
* Suggested duration

Support:

2 min
3 min
5 min
10 min

Countdown timer should run automatically.

---

# Folder Structure

classroom-copilot/

├── app.py

├── requirements.txt

├── .env

├── services/

│   ├── speech_to_text.py

│   ├── text_to_speech.py

│   ├── gemini_service.py

│   ├── intent_classifier.py

│   └── diagram_generator.py

├── prompts/

│   ├── concept_prompt.py

│   ├── quiz_prompt.py

│   ├── translation_prompt.py

│   └── activity_prompt.py

├── ui/

│   └── gradio_ui.py

├── assets/

├── generated_audio/

└── README.md

---

# Environment Variables

GEMINI_API_KEY=

---

# Non Goals

Do NOT build:

* Authentication
* Database
* User accounts
* Redis
* Docker
* Payments
* Analytics
* Complex backend architecture

This is a prototype.

Keep implementation lightweight.

---

# Success Criteria

A teacher should be able to:

Speak a command.

Receive a useful classroom response.

See visual content.

Hear audio feedback.

Continue teaching without touching the keyboard.

If all four educational features work through voice interaction, the prototype is successful.
