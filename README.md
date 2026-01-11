# Realty Agent Project Documentation

## Overview

Realty Agent is an LLM-based chatbot designed to assist users with purchasing their dream home. The project leverages OpenAI's LLMs (specifically gpt-4.1-mini) to create an interactive conversational agent specialized in real estate assistance.

## Setup Instructions

### Prerequisites
- Python environment (version specified in `.python-version`)
- OpenAI API key

### Installation Steps

**Step 1: Configure Environment Variables**

Create a `.env` file in the root of the repository and fill out the required credentials:

```zsh
cp -r .env.example .env
```

After copying, edit the `.env` file to add your OpenAI API key and any other required credentials.

**Step 2: Run the Application**

Execute the run script to start the chatbot:

```zsh
./run.sh
```