import requests
import json
import openai

def generate_poem(prompt, api_key):
    # Set up OpenAI API client
    openai.api_key = api_key
    model_engine = "text-davinci-002"

    # Generate poem with OpenAI GPT-3
    response = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.7,
    )

    # Extract poem from OpenAI response
    try:
        poem = response.choices[0].text.strip()
    except IndexError:
        poem = None

    return poem

