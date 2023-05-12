import openai

def generate_response(prompt, model="gpt-3.5-turbo"): #gpt-3.5-turbo
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
    )
    
    return response['choices'][0]['message']['content'].strip()

def generate_email(prompt, api_key, finalizedPreferences):
    openai.api_key = api_key

    # Append the finalizedPreferences to the prompt
    finalizedPrompt = "Please follow these preferences: " + finalizedPreferences + " If emojis are enabled then please use emojis." + "\n" + "Here is the email I would like you to write based on the above preferences:" + "\n" + prompt
    print("FINALIZED PROMPT: \n" + finalizedPrompt)

    # Generate response with ChatGPT
    try:
        response = generate_response(finalizedPrompt)
    except openai.error.APIError:
        print("Error generating response with ChatGPT.")
        return None

    # Extract email from the response
    try:
        email = response.strip()
    except IndexError:
        print("Error extracting email from ChatGPT response.")
        return None

    return email
