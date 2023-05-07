from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client import file, client, tools
from google.oauth2 import service_account


import ast
import json
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

    # Read the api_key from config.ini file
    config = configparser.ConfigParser()
    config.read('config.ini')
    api_key = config.get('DEFAULT', 'openai_api_key')

    while True: 
        print("Welcome to EmailHelper!\n")

        userDecision = input("Would you like to A) Organize your email inbox, B) Write an email, or Q) Quit? ")

        if userDecision.lower() == 'a': #user chooses to organize their inbox
                print("Organizing your inbox...\n")
                # Load the credentials from the credentials file. Handles the Oath2 flow
                creds = None  # Initialize creds to None to avoid creds not defined error 

                # Read the config.ini file
                config = configparser.ConfigParser()
                config.read('config.ini')
                credentials_file = config.get('DEFAULT', 'gmail_cred_file')

                if os.path.exists('token.json'):
                    #creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/gmail.modify'])
                    #creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/gmail.modify', 'https://www.googleapis.com/auth/gmail.settings.basic'])
                    creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/gmail.modify'])
                  

                if not creds or not creds.valid:
                    if creds and creds.expired and creds.refresh_token:
                        creds.refresh(Request())
                    else:
                        flow = InstalledAppFlow.from_client_secrets_file(credentials_file, [
                            'https://www.googleapis.com/auth/gmail.modify' #gives permission to delete emails 
                        ])




                        creds = flow.run_local_server(port=0)

                    with open('token.json', 'w') as token:
                        token.write(creds.to_json())

                service = build('gmail', 'v1', credentials=creds)

                #prompt the user for the subject header for which email to delete 
                subjectheader = input("Enter the subject header for email you want to delete: ")
                query = "subject:" + subjectheader
                result = service.users().messages().list(userId='me', q=query).execute()
                messages = result.get('messages', [])

                #delete the email with the chosen subject header 
                if not messages:
                    print("No emails found with the subject header:", subjectheader)

                else:
                    for message in messages:
                        message_id = message['id']
                        service.users().messages().delete(userId='me', id=message_id).execute()
                        print(f"Deleted email with ID: {message_id}")

                    print(f"Deleted {len(messages)} email(s) with the subject header: {subjectheader}")


        elif userDecision.lower() == 'b':  # user chooses to write an email
                prompt = input("Enter a prompt for the email: ")
                # api_key = os.environ.get("OPENAI_API_KEY")
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
                        #credentials_file = config['DEFAULT']['gmail_cred_file']
                        credentials_file = config['DEFAULT']['gmail_cred_file'].strip('"')

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
                    action = input("Choose an action - A) send the email, B) modify the email, C) clear the email & rewrite, D) redisplay the email, E) Exit to main screen: ")

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
                    elif action.lower() == 'e':
                        # Delete the email
                        print("Exiting to main screen")
                        break; #reprompts main screen 
                    else:
                        print("Invalid action. Please choose A, B, C, or D.")

        elif userDecision.lower() == 'q': 
                print("Quitting program")
                break; #exits program