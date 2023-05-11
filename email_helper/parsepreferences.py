import json

#parses the preferences .json file
def parse_preferences(preferences): 
    with open(preferences, 'r') as file:
        data = json.load(preferences)
    preferences = data['ai_email_bot']['student preferences']
    return preferences

#asks the user to adjust the preferences based on what they want 
def prompt_for_preferences(file):
    # Get current depth level
    current_depth = file["ai_email_bot"]["user preferences"]["depth"]
    print(f"Current depth level is: {current_depth}")

    while True:
        try:
            new_depth = int(input("Please enter a new depth level (from 1 to 3): "))
            if new_depth not in [1, 2, 3]:
                print("Invalid depth level. Please enter a number between 1 and 3.")
                continue
            file["ai_email_bot"]["user preferences"]["depth"] = new_depth
            break
        except ValueError:
            print("Invalid input. Please enter a number.")

    # Define valid communication and tone styles
    valid_comm_styles = ["stochastic", "Formal", "Textbook", "Layman", "Story Telling", "Socratic", "Humorous"]
    valid_tone_styles = ["Debate", "Encouraging", "Neutral", "Informative", "Friendly"]

    # Get current communication styles
    current_comm_styles = file["ai_email_bot"]["user preferences"]["communication_style"]
    print(f"Current communication styles are: {current_comm_styles}")

    while True:
        new_comm_styles = input("Please enter new communication styles (separated by commas): ").split(',')
        if all(style in valid_comm_styles for style in new_comm_styles):
            file["ai_email_bot"]["user preferences"]["communication_style"] = new_comm_styles
            break
        else:
            print("Invalid communication style. Please enter one or more of the following (separated by commas): " + ', '.join(valid_comm_styles))

    # Get current tone styles
    current_tone_styles = file["ai_email_bot"]["user preferences"]["tone_style"]
    print(f"Current tone styles are: {current_tone_styles}")

    while True:
        new_tone_styles = input("Please enter new tone styles (separated by commas): ").split(',')
        if all(style in valid_tone_styles for style in new_tone_styles):
            file["ai_email_bot"]["user preferences"]["tone_style"] = new_tone_styles
            break
        else:
            print("Invalid tone style. Please enter one or more of the following (separated by commas): " + ', '.join(valid_tone_styles))

    # Get current emoji usage
    current_emoji_usage = file["ai_email_bot"]["user preferences"]["use_emojis"]
    print(f"Current emoji usage is: {'Yes' if current_emoji_usage else 'No'}")

    while True:
        new_emoji_usage = input("Do you want to use emojis? (Yes/No): ")
        if new_emoji_usage.lower() in ['yes', 'no']:
            file["ai_email_bot"]["user preferences"]["use_emojis"] = new_emoji_usage.lower() == 'yes'
            break
        else:
            print("Invalid input. Please enter 'Yes' or 'No'.")

    # Get current language
    current_language = file["ai_email_bot"]["user preferences"]["language"]
    print(f"Current language is: {current_language}")

    new_language = input("Please enter a new language: ")
    file["ai_email_bot"]["user preferences"]["language"] = new_language

    return file
