from generate_poem import generate_poem


def main():
    prompt = "Write a poem about how the polder family in Duff-field Virginia think Dr. Seuss works for the FBI."
    api_key = input("Enter your OpenAI API key: ")

    poem = generate_poem(prompt, api_key)

    if poem is None:
        print(f"Unable to generate poem for '{prompt}'")
    else:
        print(f"Here's your poem:\n{poem}")


if __name__ == "__main__":
    main()
