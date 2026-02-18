
# TODO:

# HW4
Goal
Build a functional RAG chatbot from scratch that can ingest and process a knowledge base from multiple file formats (PDFs and audio).

## Knowledge Base
- Source 1: The "Databases for GenAI" presentation PDF, available on the AI Academy Google Drive.
- Source 2: The video recordings of the corresponding lecture.

## Instructions
Build a complete RAG pipeline in Python that performs the following steps:
- Load and Process Data:
  - Write code to load the PDF and reliably extract its text content.
  - Use a speech-to-text library (e.g., OpenAI's Whisper, or a suitable Hugging Face model) to transcribe the audio recordings into text.

## Chunk the Text:
- Prepare the text from both the PDF and the audio transcription.
- Split the text into smaller, semantically meaningful chunks.

## Embed and Store in a Vector Database:
- Use any embedding model to convert your text chunks into vector embeddings.
- Set up a vector database to store these embeddings. As covered in the lecture, ChromaDB or Qdrant are excellent choices for this project due to their ease of use.

## Retrieve and Generate:
- Create a function that takes a user's question, converts it into a vector, and queries the database to find the most relevant text chunks.
- Pass the original question and the retrieved context chunks to an LLM to generate a final answer.


## Testing and Deliverables
Test Your Chatbot: Ask your chatbot at least three questions related to the lecture content, such as:
- "What are the production 'Do's' for RAG?"
- "What is the difference between standard retrieval and the ColPali approach?"
- "Why is hybrid search better than vector-only search?"
Submit Your Work: Provide the following in a link to a GitHub repository:
Your complete, runnable Python code.
A requirements.txt file listing all necessary libraries.
A log showing the answers your chatbot generated for the test questions.

## Reflection
Write a short reflection (1–2 paragraphs) on your experience:
What was the most challenging part of this project? (e.g., reliably extracting text from the PDF, transcribing the audio, choosing a chunking strategy, or integrating the database?)
What new things did you learn or understand from this challenge?
📌 This task is about demonstrating your ability to build an end-to-end RAG pipeline that handles a multi-format knowledge base.

## 📚Materials for the knowledge base
Link to recordings & slides from session 1 RAG:
Intro part:
Recording 1 part. RAG Intro.mp4
Slides RAG Intro

Databases for GenAI part:
Recording 2 part Databases for GenAI.mp4
Slides Databases for GenAI

Links to recordings & slides from session 2 RAG:
Productized & Enterprise RAG
Recording 1st Part_Productized Enterprise RAG.mp4
Slides Productized & Enterprise RAG
Architecture & Design Patterns
Recording 2nd Part_Architecture & Design Patterns.mp4
Slides Architecture & Design Patterns


# 📘 Capstone Project Overview
This is your final assignment in the AI Academy Engineering Track.
In this version, we’ve placed greater emphasis on the real-world foundations of AI-Agentic system development.
Our goal is to ensure you cover 80–90% of the core components involved in building modern AI agent systems. Your task is to design and implement an AI-Agentic system that addresses a real problem faced by you, your team, or the broader Ciklum community. Some example options are available here:
LinkedIn Agent: 	
 - Your agent should produce an output message formatted as a LinkedIn or other social platform post, explaining:

  -  What the agent does and how it was built
  -  The context of its creation — as part of the AI Academy @ Ciklum

You’ll work through every major stage, including:
- Data preparation and contextualization
- RAG pipeline design for information retrieval
- AI self-reflection and reasoning
- Tool-calling mechanisms, enabling the agent to take meaningful actions and self-reflect on its performance
- Evaluation and measurement of your agent’s effectiveness
- A demo video showcasing your system in action

This assignment combines engineering depth, system design, and practical evaluation, reflecting how modern agentic AI systems are built, tested, and deployed in real-world environments.

## Objective

Build upon your previous RAG chatbot and data preparation work (HW4) to develop an AI-Agentic system capable of performing autonomous reasoning, taking meaningful tool-based actions, and reflecting on its own decisions and performance. 
The goal is to demonstrate your ability to design a technically robust, self-reflective agentic system that integrates data retrieval, reasoning, action execution, and evaluation into a cohesive workflow.

## 📘 What to Do
Work through all major components of an agentic AI system:
- Data Preparation & Contextualization – prepare relevant data your agent will use.
- RAG Pipeline Design – design your retrieval mechanism (e.g., embeddings + vector store).
- Reasoning & Reflection – ensure your agent can analyse and self-correct.
- Tool-Calling Mechanisms – allow it to take actions or run tools based on reasoning.
- Evaluation – include a simple way to measure success (accuracy, relevance, clarity).

## 🧰 Technology Stack (flexible):
Use any preferred stack — Python, LangChain, CrewAI, OpenAI API, or a custom setup.
Keep it simple but functional: focus on reasoning, inspection, and message generation rather than complexity.
Your agent may use any preferred stack or framework (e.g., Python + OpenAI API, LangChain, CrewAI, or custom logic). It should be simple yet functional, focusing on reasoning, file inspection, and message generation rather than complexity.

## 📦 Deliverables
To complete the assignment, submit the following:
- Git Repository Link – A publicly accessible GitHub repository containing your working agent’s source code.
  - Include a short README.md and an architecture.mmd file that describes how to run the agent and what technologies or libraries you used.
  - The repository should contain enough documentation for mentors to test or review the logic.


A Demo video containing the overview and demonstration of your solution at work
Generated Post (Optional) – A short social-style message created by your agent itself, published on LinkedIn or another platform of your choice.


The post should explain, in the agent’s own words:
What it does and how it was built
That it was created as part of the Ciklum AI Academy
(Optional) Include a mention or tag for @Ciklum


Keep it professional, authentic, and concise (5–7 sentences).


Submission Form – Complete the official AI Academy submission form and include:


Link to your Git repository
Link to a short ~5 min demo video recording.
Link to your public post
Any additional comments or notes you’d like to share with the review team
Make sure all links are public and accessible.

📏 Evaluation Criteria

Criterion
Description
Functionality
The agent runs and successfully analyses its repository.
Creativity & Implementation
Thoughtful design choices, clear logic, and intelligent message generation.
Relevance
The agent clearly references its context (AI Academy, Ciklum).
Presentation
The generated post is coherent, professional, and aligned with the brief.
Accessibility
Links are valid, publicly viewable, and well-documented.

