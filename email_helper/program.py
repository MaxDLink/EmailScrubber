
import  gmail #importing the gmail.py file
import config #importing the config.py file
import openai_helper #importing the openai_helper.py file
import userPreferences #function for parsing the .json file for user preferences 
import json #handles json.dumps 

if __name__ == "__main__":

        # Parses preferences from behavior.json file
        preferences, features = userPreferences.parse_preferences('behavior.json')
        print(preferences, features)

        # Update the preferences based on user input
        updated_preferences = userPreferences.set_prompts_for_preferences(preferences, features)
        # Print out the updated preferences
        print(updated_preferences)

        # Convert preferences, features, and updated_preferences to strings
        preferences_str = json.dumps(preferences)
        features_str = json.dumps(features)
        updated_preferences_str = json.dumps(updated_preferences)

        # Concatenate the preference strings to create finalizedPreferences
        finalizedPreferences = preferences_str + features_str + updated_preferences_str

        # Credentials creation and GMAIL API service building
        api_key, service = gmail.build_service()


        while True: 
                print("Welcome to EmailHelper!\n")

                userDecision = input("Would you like to email helper to M) Monitor email inbox passively, A) Organize your email inbox, W) Write an email, F) Forward Emails, C) Copy an email, or Q) Quit? ")

                if userDecision.lower() == 'm': #user chooses to monitor their inbox
                        print("Monitoring your inbox...\n")
                        gmail.monitor_mail(api_key, service)
                elif userDecision.lower() == 'a': #user chooses to organize their inbox
                        print("Organizing your inbox...\n")
                        print("You can move to the trash/delete emails based on: \n")
                        choice = input("subject header, sender, or unstarred status. Enter S for subject header, F for sender, E for emptying trash, or T for moving unstarred emails to trash: ")
                        if choice.lower() == 's': #user chooses to delete emails based on subject header
                                gmail.delete_mail(service,choice); #call to delete mail function 
                        elif choice.lower() == 'f': #user chooses to delete emails based on sender
                                gmail.delete_mail(service,choice); #call to delete mail function
                        elif choice.lower() == 'e': #user chooses to empty trash 
                                gmail.delete_mail(service,choice); #call to delete mail function
                        elif choice.lower() == 't': #user chooses to move all unstarred emails to the trash 
                                gmail.delete_mail(service,choice); #call to delete mail function



                elif userDecision.lower() == 'w':  # user chooses to write an email
                        gmail.write_mail(api_key, service, finalizedPreferences) #call to write mail function
                elif userDecision.lower() == 'f': #user chooses to forward emails
                        gmail.forward_mail(service) #call to forward mail function
                elif userDecision.lower() == 'c': #user chooses to copy an email
                        gmail.copy_mail(service) #call to copy mail function
                elif userDecision.lower() == 'q': 
                        print("Quitting program")
                        break; #exits program