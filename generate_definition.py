import openai

def generate_definition(word, api_key):
    # Set up OpenAI API client
    openai.api_key = api_key
    model_engine = "text-davinci-002"

    # Generate definition with OpenAI GPT-3
    prompt = f"Define the word '{word}'"
    response = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.7,
    )

    # Extract definition from OpenAI response
    try:
        definition = response.choices[0].text.strip()
    except IndexError:
        definition = None
        printf("Unable to generate definition for '{word}'"); 

    return definition
