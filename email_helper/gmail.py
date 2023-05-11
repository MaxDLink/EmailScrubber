from google.oauth2.credentials import Credentials
from email.mime.text import MIMEText
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from urllib.parse import urlparse
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio

import os
import config #reads in api key from config.ini file
import openai_helper #openai api function 
import base64
import email 
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
import binascii
import chardet



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

def create_attachments(service, path_or_url):
    print("Attachments")

    # Create a MIMEMultipart message to hold the email body and the attachment
    msg = MIMEMultipart()

    # Check if the input is a URL or a file path
    if urlparse(path_or_url).scheme in ['http', 'https']:
        # The input is a URL, create a hyperlink
        part = MIMEText('<a href="{}">{}</a>'.format(path_or_url, path_or_url), 'html')
    else:
        # The input is a file path
        with open(path_or_url, 'rb') as f:
            file_content = f.read()
            
        # Check the file type and create the corresponding MIME part
        if path_or_url.endswith('.txt'):
            part = MIMEText(file_content, 'plain')
        elif path_or_url.endswith('.jpg') or path_or_url.endswith('.png'):
            part = MIMEImage(file_content)
        elif path_or_url.endswith('.mp3'):
            part = MIMEAudio(file_content)
        else:  # for .mp4 or other file types
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(file_content)
            encoders.encode_base64(part)

        part.add_header('Content-Disposition', 'attachment', filename=path_or_url)
    
    # Attach the part to the message
    msg.attach(part)

    return msg

def write_mail(api_key, service, parsedPreferences):
    
    prompt = input("Enter a prompt for the email: ")    
    if api_key is None:
        print("API key not found. Please set the 'OPENAI_API_KEY' environment variable.")
        exit(1)

    # Generate initial email content with OpenAI based on preferences 
    email_content = openai_helper.generate_email(prompt, api_key, parsedPreferences)

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
        action = input("Choose an action - S) send the email, B) modify the email, C) clear the email & rewrite, D) redisplay the email, or E) Exit to main screen: ")

        if action.lower() == 's':
            # Create a multipart message
            message = MIMEMultipart()

            # Set the email content to the modified email_content (if it was modified)
            message.attach(MIMEText(email_content, "html"))  # changing "plain" to "html" to allow links

            # Ask the user if they want to attach files or links
            attach_files = input("Do you want to attach files or links? (yes/no) ")
            if attach_files.lower() == "yes":
                # Prompt the user for the file paths of the attachments or links
                attachments = input("Enter the paths of the files to attach, separated by commas, or enter the links: ").split(',')

                # Attach each file or URL to the email
                for path_or_url in attachments:
                    attachment_part = create_attachments(service, path_or_url.strip())  # strip to remove leading/trailing white space
                    # Add a new line before each attachment
                    message.attach(MIMEText("\n", 'plain'))

                    #add the attachment to the email message
                    message.attach(attachment_part)

            print("\nMessage Body: " + str(message.get_payload(0).get_payload()))

            #Prompt the user for the subject header 
            subject = input("Enter the subject header: ")
            message['Subject'] = subject
            # Prompt the user to enter the email address
            to_address = input("Enter the email address to send the email to: ")
            message['To'] = to_address
            
            # Send the email to the entered email address
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
        elif action.lower() == 'a': 
            #Attach picture or video to email
            print("Attaching picture or video to email\n")
            attachments(service) #call to attachments function 
        elif action.lower() == 'e':
            # Delete the email
            print("Exiting to main screen")
            break; #reprompts main screen 
        else:
            print("Invalid action. Please choose A, B, C, or D.")

def forward_mail(service):
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

    # Check if 'raw' exists in the original message
    if 'raw' not in original_message:
        print("Error: No raw data in the email.")
        return

    # Decode and parse the original email
    raw_data = original_message['raw']
    msg_bytes = base64.urlsafe_b64decode(raw_data)
    encoding = chardet.detect(msg_bytes)['encoding']
    msg_str = msg_bytes.decode(encoding)
    mime_msg = email.message_from_string(msg_str)

    # Extract the text and HTML from the MIME message, and save any images or videos
    text = ""
    html = ""
    media_parts = []
    for part in mime_msg.walk():
        if part.get_content_type() == 'text/plain':
            text += part.get_payload()
        elif part.get_content_type() == 'text/html':
            html += part.get_payload()
        elif part.get_content_type().startswith('image/') or part.get_content_type().startswith('video/'):
            media_parts.append(part)

    # Set up the forwarded message
    forwarded_msg = MIMEMultipart('related')
    if html:
        msg_alternative = MIMEMultipart('alternative')
        forwarded_msg.attach(msg_alternative)
        msg_alternative.attach(MIMEText(html, "html"))
    else:
        forwarded_msg.attach(MIMEText(text, "plain"))

    for part in media_parts:
        if part.get_content_type().startswith('image/'):
            msg_image = MIMEImage(part.get_payload(decode=True), part.get_content_subtype())
        elif part.get_content_type().startswith('video/'):
            msg_image = MIMEBase(part.get_content_type(), part.get_content_subtype())
            msg_image.set_payload(part.get_payload(decode=True))
        else:
            continue
        msg_image.add_header('Content-Disposition', 'inline', filename=part.get_filename())
        msg_image.add_header('Content-ID', '<' + part.get_filename() + '>')
        forwarded_msg.attach(msg_image)

    forwarded_subject = input("Enter the subject header for the forwarded email (leave blank to use the original subject): ")
    if not forwarded_subject:
        forwarded_subject = mime_msg['subject']
    forwarded_msg['Subject'] = forwarded_subject
    forwarded_msg['To'] = input("Enter the email address to forward the email to: ")

    # Forward the email
    create_message = {'raw': base64.urlsafe_b64encode(forwarded_msg.as_bytes()).decode()}
    sent_message = service.users().messages().send(userId="me", body=create_message).execute()
    print(f"Message forwarded to {forwarded_msg['To']}. Message Id: {sent_message['id']}")

def copy_mail(service):
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

    # Extract the text and HTML from the MIME message, and save any images or videos
    text = ""
    html = ""
    media_parts = []
    for part in mime_msg.walk():
        if part.get_content_type() == 'text/plain':
            text += part.get_payload()
        elif part.get_content_type() == 'text/html':
            html += part.get_payload()
        elif part.get_content_type().startswith('image/') or part.get_content_type().startswith('video/'):
            media_parts.append(part)

    # Set up the copied message
    copied_msg = MIMEMultipart('related')
    if html:
        msg_alternative = MIMEMultipart('alternative')
        copied_msg.attach(msg_alternative)
        msg_alternative.attach(MIMEText(html, "html"))
    else:
        copied_msg.attach(MIMEText(text, "plain"))

    for part in media_parts:
        if part.get_content_type().startswith('image/'):
            msg_image = MIMEImage(part.get_payload(decode=True), part.get_content_subtype())
        elif part.get_content_type().startswith('video/'):
            msg_image = MIMEBase(part.get_content_type(), part.get_content_subtype())
            msg_image.set_payload(part.get_payload(decode=True))
        else:
            continue
        msg_image.add_header('Content-Disposition', 'inline', filename=part.get_filename())
        msg_image.add_header('Content-ID', '<' + part.get_filename() + '>')
        copied_msg.attach(msg_image)

    copied_subject = input("Enter the subject header for the copied email (leave empty to use the original subject): ")
    copied_msg['Subject'] = copied_subject if copied_subject else mime_msg['subject']
    copied_msg['To'] = input("Enter the email address to send the copied email to: ")

    # Send the copied email
    create_message = {'raw': base64.urlsafe_b64encode(copied_msg.as_bytes()).decode()}
    sent_message = service.users().messages().send(userId="me", body=create_message).execute()
    print(f"Copied message sent to {copied_msg['To']}. Message Id: {sent_message['id']}")

def monitor_mail(api_key, service): 
    print("Monitoring email inbox")