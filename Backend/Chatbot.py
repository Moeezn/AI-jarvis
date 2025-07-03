import os
import json
import datetime
import requests
from json import load, dump
from dotenv import dotenv_values
from groq import Groq
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# Load environment variables
env_vars = dotenv_values(".env")

Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "AI Assistant")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Check if API key exists
if not GroqAPIKey:
    print(Fore.RED + "GroqAPIKey not found in .env file. Please set it first.")
    exit()

# Initialize Groq Client
client = Groq(api_key=GroqAPIKey)

# Create folder for chat logs if not exists
os.makedirs("Data", exist_ok=True)
log_path = r"Data\ChatLog.json"

# Load or create chat log
try:
    with open(log_path, "r") as f:
        messages = load(f)
except (FileNotFoundError, json.JSONDecodeError):
    with open(log_path, "w") as f:
        dump([], f)
    messages = []

# System Prompt
SystemPrompt = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

SystemChatBot = [{"role": "system", "content": SystemPrompt}]

def RealtimeInformation():
    now = datetime.datetime.now()
    return (
        f"Please use this real-time information if needed:\n"
        f"Day: {now.strftime('%A')}\nDate: {now.strftime('%d')}\nMonth: {now.strftime('%B')}\n"
        f"Year: {now.strftime('%Y')}\nTime: {now.strftime('%H')} hours, {now.strftime('%M')} minutes.\n"
    )

def AnswerModifier(answer):
    return '\n'.join(line for line in answer.split('\n') if line.strip())

def ChatBot(query):
    try:
        # Load chat history
        with open(log_path, "r") as f:
            messages = load(f)

        messages.append({"role": "user", "content": query})

        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + [{"role": "system", "content": RealtimeInformation()}] + messages,
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=True
        )

        answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                answer += chunk.choices[0].delta.content

        answer = AnswerModifier(answer).replace("</s>", "")
        messages.append({"role": "assistant", "content": answer})

        with open(log_path, "w") as f:
            dump(messages, f, indent=4)

        return answer

    except requests.exceptions.RequestException as e:
        return Fore.RED + f"Connection error: {e}"
    except Exception as e:
        return Fore.RED + f"An error occurred: {e}"

if __name__ == "__main__":
    print(Fore.CYAN + f"\n🤖 Welcome! {Assistantname} is ready to assist you.")
    print(Fore.YELLOW + "Type 'exit' to quit, or 'clear' to reset chat history.\n")

    while True:
        user_input = input(Fore.GREEN + "You: ")

        if user_input.lower() in ["exit", "quit"]:
            print(Fore.CYAN + "Goodbye!")
            break
        elif user_input.lower() == "clear":
            with open(log_path, "w") as f:
                dump([], f)
            print(Fore.YELLOW + "Chat history cleared.")
            continue
        elif user_input.strip() == "":
            continue

        response = ChatBot(user_input)
        print(Fore.BLUE + f"{Assistantname}: " + Fore.WHITE + response)
