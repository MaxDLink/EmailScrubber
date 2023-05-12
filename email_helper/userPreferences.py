import json
import os

# Parses the preferences .json file
def parse_preferences(file): 
    with open(file, 'r') as file:
        data = json.load(file)
    preferences = data['ai_email_bot']['user preferences']
    features = data['ai_email_bot']['features']['personalization']
    return preferences, features

# Asks the user to adjust the preferences based on what they want
def set_prompts_for_preferences(preferences, features):
    # Get current depth level
    current_depth = preferences["depth"]
    print(f"Current depth level is: {current_depth}")

    while True:
        try:
            new_depth = int(input("Please enter a new depth level (from 1 to 3): "))
            if new_depth not in [1, 2, 3]:
                print("Invalid depth level. Please enter a number between 1 and 3.")
                continue
            preferences["depth"] = new_depth
            break
        except ValueError:
            print("Invalid input. Please enter a number.")

    # Get current communication styles
    available_comm_styles = list(features["communication_styles"].keys())
    print(f"Available communication styles are: {available_comm_styles}")
    while True:
        new_comm_styles = input("Please enter new communication styles (separated by commas): ").split(',')
        # Validate new communication styles
        if all(style in available_comm_styles for style in new_comm_styles):
            preferences["communication_style"] = new_comm_styles
            break
        else:
            print("Invalid communication style. Please enter one or more of the following (separated by commas): " + ', '.join(available_comm_styles))

    # Get current tone styles
    available_tone_styles = list(features["tone_styles"].keys())
    print(f"Available tone styles are: {available_tone_styles}")

    while True:
        new_tone_styles = input("Please enter new tone styles (separated by commas): ").split(',')
        # Validate new tone styles
        if all(style in available_tone_styles for style in new_tone_styles):
            preferences["tone_style"] = new_tone_styles
            break
        else:
            print("Invalid tone style. Please enter one or more of the following (separated by commas): " + ', '.join(available_tone_styles))

    # Get current emoji usage
    current_emoji_usage = preferences["use_emojis"]
    print(f"Current emoji usage is: {'Yes' if current_emoji_usage else 'No'}")

    while True:
        new_emoji_usage = input("Do you want to use emojis? (Yes/No): ")
        if new_emoji_usage.lower() in ['yes', 'no']:
            preferences["use_emojis"] = new_emoji_usage.lower() == 'yes'
            break
        else:
            print("Invalid input. Please enter 'Yes' or 'No'.")

    # Get current language
    current_language = preferences["language"]
    print(f"Current language is: {current_language}")

    new_language = input("Please enter a new language: ")
    preferences["language"] = new_language

    return preferences

def set_preferences(choice):

    
    if(choice.lower() == 'y'): #if the user wants to set preferences 
        print("Setting preferences...")
        # Parses preferences from behavior.json file
        preferences, features = parse_preferences('behavior.json')

        # Update the preferences based on user input
        updated_preferences = set_prompts_for_preferences(preferences, features)
        # Convert preferences, features, and updated_preferences to strings
        preferences_str = json.dumps(preferences)
        features_str = json.dumps(features)
        updated_preferences_str = json.dumps(updated_preferences)
        
        # Concatenate the preference strings to create finalizedPreferences
        finalizedPreferences = preferences_str + features_str + updated_preferences_str
        save_preferences(finalizedPreferences, 'user_preferences.json') #save the preferences to a json file
    else: #if the user wants to load saved preferences
        print("Loading preferences...")
        prefs = load_preferences('user_preferences.json')
        prefs_str = json.dumps(prefs)
        finalizedPreferences = prefs_str
        
    return finalizedPreferences

# Save preferences to a JSON file
def save_preferences(preferences, file):
    with open(file, 'w') as f:
        json.dump(preferences, f)

# Load preferences from a JSON file
def load_preferences(file):
    if os.path.exists(file):
        with open(file, 'r') as f:
            return json.load(f)
    else:
        return None
