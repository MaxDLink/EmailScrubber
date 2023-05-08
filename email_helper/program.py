
import  gmail #importing the gmail.py file
import config #importing the config.py file
import openai_helper #importing the openai_helper.py file
if __name__ == "__main__":
    # Credentials creation and GMAIL API service building
    api_key, service = gmail.build_service()


    while True: 
        print("Welcome to EmailHelper!\n")

        userDecision = input("Would you like to A) Organize your email inbox, B) Write an email, or Q) Quit? ")

        if userDecision.lower() == 'a': #user chooses to organize their inbox
                print("Organizing your inbox...\n")
                choice = input("You can delete emails based on subject header, sender, or unstarred status. Enter S for subject header, F for sender, E for emptying trash, or T for moving unstarred emails to trash: ")
                if choice.lower() == 's': #user chooses to delete emails based on subject header
                    gmail.delete_mail(service,choice); #call to delete mail function 
                elif choice.lower() == 'f': #user chooses to delete emails based on sender
                    gmail.delete_mail(service,choice); #call to delete mail function
                elif choice.lower() == 'e': #user chooses to empty trash 
                    gmail.delete_mail(service,choice); #call to delete mail function
                elif choice.lower() == 't': #user chooses to move all unstarred emails to the trash 
                    gmail.delete_mail(service,choice); #call to delete mail function



        elif userDecision.lower() == 'b':  # user chooses to write an email
                gmail.write_mail(api_key, service) #call to write mail function
        elif userDecision.lower() == 'q': 
                print("Quitting program")
                break; #exits program