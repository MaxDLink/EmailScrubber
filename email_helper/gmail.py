from google.oauth2.credentials import Credentials
from email.mime.text import MIMEText
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from email.mime.multipart import MIMEMultipart

import os
import config #reads in api key from config.ini file
import openai_helper #openai api function 
import base64
import email 

import PySimpleGUI as sg #importing the PySimpleGUI library 
#TODO - add GUI for user to interact with program

def build_service():
    #credentials creation and GMAIL API service building 
    #define the scopes 
    SCOPES = ['https://mail.google.com/']

    # Read the api_key from config.ini file
    api_key = config.read_api_key()

    # Create credentials and Gmail API service once, before the while loop
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            credentials_file = config.get('DEFAULT', 'gmail_cred_file')
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)
    return api_key, service


def delete_mail(service, choice): 

    if(choice.lower() == 's'): #delete by subject header 
        #prompt the user for the subject header for which email to delete 
        subjectheader = input("Enter the subject header for email you want to delete: ")
        query = "subject:" + subjectheader
        result = service.users().messages().list(userId='me', q=query).execute()
        messages = result.get('messages', [])

        # delete the email with the chosen subject header
        if not messages:
            print("No emails found with the subject header:", subjectheader)

        else:
            for message in messages:
                message_id = message['id']
                try:
                    #service.users().messages().modify(userId='me', id=message_id, body={'removeLabelIds': [], 'addLabelIds': ['TRASH']}).execute()
                    #print(f"Moved to trash bin - email with ID: {message_id}")
                    service.users().messages().delete(userId='me', id=message_id).execute()

                    #service.users().messages().delete(userId='me', id=message_id).execute()
                    print(f"Deleted email with ID: {message_id}")
                except HttpError as error:
                    print(f"An error occurred while deleting the email with ID: {message_id}")
                    print(f"Error: {error}")

            print(f"Deleted {len(messages)} email(s) with the subject header: {subjectheader}")
    elif(choice.lower() == 'f'): #delete email by sender 
        sender = input("Enter the sender's email address for the email(s) you want to move to the trash: ")
        query = "from:" + sender
        result = service.users().messages().list(userId='me', q=query).execute()
        messages = result.get('messages', [])

        if not messages:
            print("No emails found from the sender:", sender)
        else:
            for message in messages:
                message_id = message['id']
                try:
                    service.users().messages().trash(userId='me', id=message_id).execute()
                    print(f"Moved email with ID: {message_id} " + "to trash bin")
                except HttpError as error:
                    print(f"An error occurred while deleting the email with ID: {message_id}")
                    print(f"Error: {error}")
            print(f"Deleted {len(messages)} email(s) from the sender: {sender}")
    elif(choice.lower() == 'e'): #empty trash 
        try:
            messages = service.users().messages().list(userId='me', labelIds=['TRASH']).execute()
            while 'messages' in messages:
                for message in messages['messages']:
                    service.users().messages().delete(userId='me', id=message['id']).execute()
                    print(f"Deleted message with ID: {message['id']}")
                page_token = messages.get('nextPageToken')
                if page_token:
                    messages = service.users().messages().list(userId='me', labelIds=['TRASH'], pageToken=page_token).execute()
                else:
                    break
            print("Trash bin emptied successfully.")
        except HttpError as error:
            print("An error occurred while emptying the trash bin.")
            print(f"Error: {error}")

    elif(choice.lower() == 't'): # move all unstarred emails to the trash
        query = "is:unread -is:starred"
        page_token = None
        trash_full = False

        while True:
            result = service.users().messages().list(userId='me', q=query, pageToken=page_token).execute()
            messages = result.get('messages', [])

            if not messages:
                print("No unstarred emails found.")
                break

            for message in messages:
                message_id = message['id']
                try:
                    service.users().messages().trash(userId='me', id=message_id).execute()
                    print(f"Moved unstarred email with ID: {message_id} to trash")
                except HttpError as error:
                    print(f"An error occurred while moving the unstarred email with ID: {message_id} to trash")
                    print(f"Error: {error}")
                    trash_full = True
                    break  # Exit the loop if the trash is full

            if trash_full:
                break  # Exit the loop if the trash is full

            page_token = result.get('nextPageToken')
            if not page_token:
                break  # Exit the loop if there are no more pages

        if trash_full:
            deleteChoice = input("The trash bin has been completely filled up with unstarred emails. Would you like to continue moving unstarred emails to your trash bin with C, empty the trash bin with E, or return to the main menu with B?")
            if deleteChoice.lower() == 'c':
                delete_mail(service)  # Go back through with the same function and keep moving unstarred emails to trash
            elif deleteChoice.lower() == 'e':
                empty_trash(service)  # User chooses to empty the trash bin
            elif deleteChoice.lower() == 'b':
                print("Returning to the main menu.")  # Return user to the main menu
            else:
                print("Invalid choice. Please try again.")  # Invalid choice, return user to the main menu

def write_mail(api_key, service):
    
    prompt = input("Enter a prompt for the email: ")    
    if api_key is None:
        print("API key not found. Please set the 'OPENAI_API_KEY' environment variable.")
        exit(1)

    # Generate initial email content with OpenAI
    email_content = openai_helper.generate_email(prompt, api_key)

    if email_content is None:
        print("Unable to generate email content.")
        exit(1)

    # Print the email content to the console
    print("Generated email content:\n%s\n" % email_content)

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
            create_message = {'raw': base64.urlsafe_b64encode(message.as_bytes('utf-8')).decode()}
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
            email_content = openai_helper.generate_email("Take this email: " + email_content + "\n and change it to: " + suggestedChanges, api_key)
            print("Modified email content:\n%s\n" % email_content)



        elif action.lower() == 'c':
        # Regenerate email content
            print("Clearing Email Content")
            prompt = input("Enter a prompt for the email: ")
            email_content = openai_helper.generate_email(prompt, api_key)
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

def forward_mail(api_key, service):
    print("Forwarding email")

    # Get the subject header of the email to forward
    subject_header = input("Enter the subject header of the email you want to forward: ")
    query = "subject:" + subject_header
    result = service.users().messages().list(userId='me', q=query).execute()
    messages = result.get('messages', [])

    if not messages:
        print("No emails found with the subject header:", subject_header)
        return

    # Choose the first email with the matching subject header
    message_id = messages[0]['id']
    original_message = service.users().messages().get(userId='me', id=message_id, format='raw').execute()

    # Decode and parse the original email
    msg_str = base64.urlsafe_b64decode(original_message['raw'].encode('ASCII'))
    mime_msg = email.message_from_bytes(msg_str)

    # Extract the text from the MIME message
    text = ""
    for part in mime_msg.walk():
        if part.get_content_type() == 'text/plain':
            text += part.get_payload()
    
    # Set up the forwarded message
    forwarded_msg = MIMEText(text)
    forwarded_subject = input("Enter the subject header for the forwarded email: ")
    forwarded_msg['subject'] = forwarded_subject
    forwarded_msg['to'] = input("Enter the email address to forward the email to: ")

    # Forward the email
    create_message = {'raw': base64.urlsafe_b64encode(forwarded_msg.as_bytes('utf-8')).decode()}
    sent_message = service.users().messages().send(userId="me", body=create_message).execute()
    print(f"Message forwarded to {forwarded_msg['to']}. Message Id: {sent_message['id']}")
    
def copy_mail(api_key, service): 
    print("Copying email")

    # Get the subject header of the email to copy
    subject_header = input("Enter the subject header of the email you want to copy: ")
    query = "subject:" + subject_header
    result = service.users().messages().list(userId='me', q=query).execute()
    messages = result.get('messages', [])

    if not messages:
        print("No emails found with the subject header:", subject_header)
        return

    # Choose the first email with the matching subject header
    message_id = messages[0]['id']
    original_message = service.users().messages().get(userId='me', id=message_id, format='raw').execute()

    # Decode and parse the original email
    msg_str = base64.urlsafe_b64decode(original_message['raw'].encode('ASCII'))
    mime_msg = email.message_from_bytes(msg_str)

    # Extract the text from the MIME message
    text = ""
    for part in mime_msg.walk():
        if part.get_content_type() == 'text/plain':
            text += part.get_payload()

    # Set up the copied message
    copied_msg = MIMEText(text)
    copied_subject = input("Enter the subject header for the copied email (leave empty to use the original subject): ")
    copied_msg['subject'] = copied_subject if copied_subject else mime_msg['subject']
    copied_msg['to'] = input("Enter the email address to send the copied email to: ")

    # Send the copied email
    create_message = {'raw': base64.urlsafe_b64encode(copied_msg.as_bytes('utf-8')).decode()}
    sent_message = service.users().messages().send(userId="me", body=create_message).execute()
    print(f"Copied message sent to {copied_msg['to']}. Message Id: {sent_message['id']}")