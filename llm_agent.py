import requests
from custom_secrets import GROQ_API_KEY  # securely imported API key

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

def query_llama(prompt: str, model="llama3-70b-8192"):
    enhanced_prompt = (
        "You are an expert AI document generator.\n"
        "Please format your output with proper markdown headings:\n"
        "- Use '#' for main titles\n"
        "- Use '##' for subheadings\n"
        "- Use '###' for sub-subheadings\n"
        "Avoid unnecessary special characters such as asterisks or hashes except for markdown headings.\n"
        "Output a clean, readable document structure.\n"
        "Generate a unique title for the documents and powerpoint presentations. Make sure to follow grammatical rules while doing so."
        "The title for the powerpoint presentation should be generated just like the title for the word and pdf documents."
        "When asked for a Word or PDF file, explain the topics in details. Everything should be well-explained."
        "When asked for a Powerpoint presentation, give content in a proper point-wise format"
        "Explain in about 100 words, the points properly in the ppt"
        "The pointers for the Powerpoint presentations should be clear."
        "Design tables as and when required."
        "Give well formatted equations as and when required"
        "\n"
        + prompt
    )
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": enhanced_prompt},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
    }
    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except requests.exceptions.RequestException as e:
        return f"❌ Groq API error: {e} - {getattr(e.response, 'text', 'No response')}"

