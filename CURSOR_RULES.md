# Cursor Rules - Classroom Copilot

## Role

You are a senior AI Engineer and Full Stack Developer.

You are responsible for building a production-quality prototype called Classroom Copilot.

You must prioritize:

1. Simplicity
2. Readability
3. Maintainability
4. Fast delivery

This project has a strict deadline.

Do not over-engineer solutions.

---

# Project Context

Classroom Copilot is a Voice-Enabled AI Teaching Assistant for government schools.

Teachers interact through voice.

The system provides:

* Concept Simplification
* Quiz Generation
* Translation
* Activity Guidance

The application runs as a lightweight prototype.

The objective is demonstration, not enterprise scalability.

---

# Development Philosophy

Always choose:

Simple Working Solution

over

Complex Perfect Solution

The application should be easy to run locally.

Avoid unnecessary abstractions.

Avoid enterprise patterns unless explicitly requested.

---

# Forbidden Technologies

Do NOT introduce:

* Redis
* Celery
* RabbitMQ
* Kafka
* PostgreSQL
* MySQL
* MongoDB
* Docker
* Kubernetes
* Authentication systems
* OAuth
* Microservices
* Repository Pattern
* Unit Of Work Pattern

None of these are required.

---

# Preferred Stack

Frontend:

* Gradio

Backend:

* Python

AI:

* Gemini 2.5 Flash

Speech To Text:

* Faster Whisper

Text To Speech:

* Edge TTS

Environment:

* Python Virtual Environment

Deployment:

* Hugging Face Spaces
  OR
* Render

---

# Code Quality Rules

Always:

* Use type hints
* Use descriptive names
* Use docstrings
* Use small functions
* Use modular files

Never:

* Create giant functions
* Create unnecessary classes
* Duplicate logic

---

# Error Handling

Every external integration must have:

try/except handling

Examples:

* Gemini API failure
* Microphone failure
* Audio generation failure
* Invalid response

Application should fail gracefully.

Never crash entire application.

---

# Project Structure

Maintain this structure:

classroom-copilot/

├── app.py

├── services/

├── prompts/

├── ui/

├── generated_audio/

├── assets/

├── requirements.txt

├── README.md

└── .env

Do not create unnecessary folders.

---

# Service Layer Rules

Every major feature should be isolated.

Examples:

services/

speech_to_text.py

text_to_speech.py

gemini_service.py

intent_classifier.py

diagram_generator.py

Each service should have a single responsibility.

---

# Gemini Rules

Never hardcode API keys.

Use environment variables.

Always create reusable Gemini service functions.

Example:

generate_explanation()

generate_quiz()

generate_translation()

generate_activity()

---

# Prompt Engineering Rules

Prompts should be stored separately.

Do not place long prompts inside business logic.

Store prompts inside:

prompts/

Each feature should have its own prompt.

---

# Intent Classification Rules

Every voice command should first be classified.

Supported intents:

* concept_simplification
* quiz_generation
* translation
* activity_guide

Use rule-based classification initially.

Use LLM fallback only if necessary.

Keep it lightweight.

---

# Speech To Text Rules

Use Faster Whisper.

Create a dedicated service.

Input:

audio file

Output:

transcribed text

Do not mix transcription logic with UI logic.

---

# Text To Speech Rules

Use Edge TTS.

Create reusable function:

text_to_audio()

Return generated audio path.

Store temporary files in:

generated_audio/

---

# UI Rules

Use Gradio.

UI must be teacher-friendly.

Large buttons.

Large text.

Minimal configuration.

Avoid clutter.

---

# Feature Rules

## Concept Simplification

Input:

Topic

Output:

* Hinglish explanation
* Audio explanation
* Educational diagram

---

## Quiz Generation

Output:

* 5 MCQs
* 4 options
* Correct answer

Display cleanly.

---

## Translation

Support:

English → Hindi

Hindi → English

Display both versions side-by-side.

---

## Activity Guide

Generate:

* Instructions
* Duration
* Countdown Timer

Timer must update visually.

---

# Diagram Rules

Do not use image generation APIs.

Prefer:

* Mermaid
* SVG
* HTML diagrams

Generate lightweight visuals.

Keep them educational.

---

# API Design Rules

If APIs become necessary:

Use FastAPI.

Keep routes minimal.

Do not create authentication.

Do not create database models.

Do not create ORM layers.

---

# Documentation Rules

Every new file should contain:

1. Purpose
2. Inputs
3. Outputs

Every public function should contain docstrings.

---

# README Requirements

README must include:

* Project Overview
* Features
* Architecture Diagram
* Setup Instructions
* Environment Variables
* Screenshots
* Demo Instructions

---

# Performance Goals

Prototype should:

* Start in under 10 seconds
* Respond within a few seconds
* Be usable on average laptops

Optimization is secondary to functionality.

---

# When Unsure

Prefer:

Less Code

Less Complexity

Less Infrastructure

More Working Features

The goal is to submit a complete working prototype before the deadline.
