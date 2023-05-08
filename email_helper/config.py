import configparser

def read_api_key():
    # Read and return the OpenAI API key from the config file
    config = configparser.ConfigParser()
    config.read('config.ini')
    api_key = config.get('DEFAULT', 'openai_api_key')
    return api_key

# Add other configuration-related functions as needed
