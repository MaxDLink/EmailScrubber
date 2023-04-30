from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

import os
import base64
import openai
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.text import MIMEText

def generate_email(prompt, api_key):
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/gmail.compose'])

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                os.environ.get('CREDENTIALS_FILE'), ['https://www.googleapis.com/auth/gmail.compose'])
            creds = flow.run_local_server(port=0)

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    # Set up OpenAI API client
    openai.api_key = api_key
    model_engine = "text-davinci-002"

    # Generate email with OpenAI GPT-3
    response = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.7,
    )

    # Extract email from OpenAI response
    try:
        email = response.choices[0].text.strip()
    except IndexError:
        email = None

    return email


if __name__ == "__main__":
    prompt = "Compose an email to send to your professor explaining that you will be unable to attend class next week due to a family emergency."
    api_key = os.environ.get("OPENAI_API_KEY")

    if api_key is None:
        print("API key not found. Please set the 'OPENAI_API_KEY' environment variable.")
        exit(1)

    # Generate email content with OpenAI
    email_content = generate_email(prompt, api_key)

    # Create Gmail API client and authenticate
    credentials = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/gmail.compose'])
    service = build('gmail', 'v1', credentials=credentials)

    # Construct the email message
    message = MIMEText(email_content)
    message['to'] = 'recipient@example.com'
    message['subject'] = 'Absent from Class Next Week'

    # Send the email
    create_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
    sent_message = service.users().messages().send(userId="me", body=create_message).execute()

    print("Message sent to %s. Message Id: %s" % (message['to'], sent_message['id']))


