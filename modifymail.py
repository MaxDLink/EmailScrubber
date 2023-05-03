import openai
import re
import configparser
# Set up OpenAI API key and model
config = configparser.ConfigParser()
config.read('config.ini')
api_key = config.get('DEFAULT', 'openai_api_key')
openai.api_key = api_key
model_engine = "text-davinci-002"

# Initialize email content
email_content = ""

while True:
    # Prompt the user for an action
    action = input("What do you want to do? (a)dd to email, (p)rint email, (b)egin new email, or (q)uit: ")

    # Add to the email
    if action.lower() == 'a':
        addition = input("What do you want to add to the email? ")
        email_content += addition

    # Print the email
    elif action.lower() == 'p':
        print("Email content:\n%s\n" % email_content)

    # Begin a new email
    elif action.lower() == 'b':
        # Get initial prompt for the email from the user
        prompt = input("Please enter a prompt for AgentGPT to generate an email: ")
        try:
            response = openai.Completion.create(
                engine=model_engine,
                prompt=prompt,
                max_tokens=1024,
                n=1,
                stop=None,
                temperature=0.7,
            )
        except openai.error.OpenAIError:
            print("Error generating email with OpenAI.")
            continue

        # Extract email from OpenAI response
        try:
            continuation = response.choices[0].text.strip()
        except IndexError:
            print("Error extracting email from OpenAI response.")
            continue

        # Print the generated email to the console
        print("Generated email:\n%s\n" % continuation)

        # Prompt the user to edit the email
        edit_email = input("Do you want to modify the email? (y/n): ")
        if edit_email.lower() == 'y':
            # Prompt the user for the modification they want to make
            prompt = input("Please enter a prompt for AgentGPT to modify the email: ")

            # Generate a continuation with OpenAI
            try:
                response = openai.Completion.create(
                    engine=model_engine,
                    prompt=email_content,
                    max_tokens=1024,
                    n=1,
                    stop=None,
                    temperature=0.7,
                )
            except openai.error.OpenAIError:
                print("Error generating continuation with OpenAI.")
                continue

            # Extract continuation from OpenAI response
            try:
                continuation = response.choices[0].text.strip()
            except IndexError:
                print("Error extracting continuation from OpenAI response.")
                continue

            # Modify the continuation based on user input
            modified_continuation = re.sub(prompt, "", continuation)
            email_content = modified_continuation

            # Print the modified email to the console
            print("Modified email content:\n%s\n" % email_content)

        else:
            print("Email not modified. Using generated email.")

    # Quit the program
    elif action.lower() == 'q':
        break

    # Invalid input
    else:
        print("Invalid action. Please enter 'a', 'p', 'b', or 'q'.")
