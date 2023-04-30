from generate_definition import generate_definition


def main():
    word = input("Enter a word to define: ")
    api_key = input("Enter your OpenAI API key: "); 
    definition = generate_definition(word, api_key); 
    
    if definition is None:
        print(f"Unable to generate definition for '{word}'")
    else:
        print(f"Here's your definition:\n{definition}")


if __name__ == "__main__":
    main()
