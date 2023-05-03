from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

import re
import os
import base64
import openai
import configparser #reads in api key from config.ini file 

# Define model engine
model_engine = "text-davinci-002"


def generate_email(prompt, api_key):
    # Set up OpenAI API client
    openai.api_key = api_key
    #model_engine = "text-davinci-002"

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
    except openai.error.OpenAIError:
        print("Error generating email with OpenAI.")
        return None

    # Extract email from OpenAI response
    try:
        email = response.choices[0].text.strip()
    except IndexError:
        print("Error extracting email from OpenAI response.")
        return None

    return email
   
if __name__ == "__main__":

    prompt = input("Enter a prompt for the email: ")
    #api_key = os.environ.get("OPENAI_API_KEY")
    config = configparser.ConfigParser()
    config.read('config.ini')
    api_key = config.get('DEFAULT', 'openai_api_key')

    if api_key is None:
        print("API key not found. Please set the 'OPENAI_API_KEY' environment variable.")
        exit(1)

    # Generate initial email content with OpenAI
    email_content = generate_email(prompt, api_key)

    if email_content is None:
        print("Unable to generate email content.")
        exit(1)

    # Print the email content to the console
    print("Generated email content:\n%s\n" % email_content)

    # Create Gmail API client and authenticate
    credentials = None
    if os.path.exists('token.json'):
        credentials = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/gmail.compose'])

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            credentials_file = config['DEFAULT']['gmail_cred_file']
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, ['https://www.googleapis.com/auth/gmail.compose'])
            credentials = flow.run_local_server(port=0)

        with open('token.json', 'w') as token:
            token.write(credentials.to_json())

    service = build('gmail', 'v1', credentials=credentials)

    # Construct the email message
    message = MIMEText(email_content)
    
    #message['subject'] = 'Email Generated by AgentGPT'

    # Save the initial email content to a variable for modification later
    original_email_content = email_content

    # Print the available actions and prompt the user to choose one
    while True:
        action = input("Choose an action - A) send the email, B) modify the email, C) clear the email, D) redisplay the email, Q) Quit: ")

        if action.lower() == 'a':
            # Set the email content to the modified email_content (if it was modified)
            message.set_payload(payload=email_content)

            print("\nMessage Body: " + str(message.get_payload()))
            #Prompt the user for the subject header 
            subject = input("Enter the subject header: ")
            message['subject'] = subject
            # Prompt the user to enter the email address
            to_address = input("Enter the email address to send the email to: ")
            message['to'] = to_address
            
            # Send the email to the entered email address
            message['to'] = to_address
            create_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
            sent_message = service.users().messages().send(userId="me", body=create_message).execute()
            print("Message sent to %s. Message Id: %s" % (to_address, sent_message['id']))
            break

        if action.lower() == 'b':
            # Modify the email
            print("Current email content:\n%s\n" % email_content)

            # Prompt the user to make changes to the email
            suggestedChanges = input("\nWhat would you like to change about this email? ")

            # Regenerate initial email content with user suggested changes 
            # Update the email content with the user's changes
            email_content = generate_email("Take this email: " + email_content + "\n and change it to: " + suggestedChanges, api_key)
            print("Modified email content:\n%s\n" % email_content)



        elif action.lower() == 'c':
        # Regenerate email content
            print("Clearing Email Content")
            prompt = input("Enter a prompt for the email: ")
            email_content = generate_email(prompt, api_key)
            if email_content is None:
                print("Unable to generate email content.")
                exit(1)
            print("New email content:\n%s\n" % email_content)

        elif action.lower() == 'd':
            # Display email to console
            print("Current email content:\n%s\n" % email_content)
        elif action.lower() == 'q':
            # Delete the email
            print("Quitting")
            break; #reprompts 
        else:
            print("Invalid action. Please choose A, B, C, or D.")

