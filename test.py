import requests
import os

# Set your API key here or export it as an environment variable
api_key = os.getenv("GROQ_API_KEY", "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")

url = "https://api.groq.com/openai/v1/chat/completions"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

data = {
    "model": "llama-3.3-70b-versatile",
    "messages": [
        {
            "role": "user",
            "content": "Explain the importance of fast language models"
        }
    ]
}

response = requests.post(url, headers=headers, json=data)

print(f"Status Code: {response.status_code}")
if response.ok:
    print("Response JSON:")
    print(response.json())
else:
    print("Error Response:")
    print(response.text)
