import openai

model_engine = "text-davinci-002"

def generate_email(prompt, api_key):
    # Set up OpenAI API client
    openai.api_key = api_key
    # model_engine = "text-davinci-002"

    # Generate email with OpenAI GPT-3
    try:
        response = openai.Completion.create(
            engine=model_engine,
            prompt=prompt,
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0.7,
        )
    except openai.error.APIError:
        print("Error generating email with OpenAI.")
        return None

    # Extract email from OpenAI response
    try:
        email = response.choices[0].text.strip()
    except IndexError:
        print("Error extracting email from OpenAI response.")
        return None

    return email
