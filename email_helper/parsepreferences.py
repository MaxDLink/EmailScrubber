import json

def parse_preferences(file_path): #parses the preferences .json file
    with open(file_path, 'r') as file:
        data = json.load(file)
    preferences = data['ai_email_bot']['student preferences']
    return preferences
