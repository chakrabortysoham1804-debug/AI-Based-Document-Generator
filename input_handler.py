import os
import pandas as pd
from transformers import BlipProcessor, BlipForConditionalGeneration
from pdfminer.high_level import extract_text
from dotenv import load_dotenv

load_dotenv()

# === Text Reader ===
def read_txt(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read().strip()


# === Improved PDF Reader (pdfminer) ===
def read_pdf(file_path):
    try:
        text = extract_text(file_path)
        if not text.strip():
            return "⚠️ No readable text found in PDF. It might be scanned or image-based."
        return text.strip()
    except Exception as e:
        return f"❌ Failed to extract text from PDF: {str(e)}"


# === CSV Analyzer ===
def read_csv(file_path):
    df = pd.read_csv(file_path)
    summary = df.describe(include='all').to_string()
    columns = ", ".join(df.columns)
    missing = df.isnull().sum()
    missing_report = "\n".join([f"{col}: {count} missing" for col, count in missing.items() if count > 0])
    return f"📊 CSV Summary:\n\n{summary}\n\nColumns: {columns}" + (f"\n\nMissing Values:\n{missing_report}" if missing_report else "")


# === Input Handler ===
def get_user_input():
    print("📥 Choose input type:")
    print("1. Type your prompt manually")
    print("2. Load from a file (.txt, .pdf, .csv")
    choice = input("Enter 1 or 2: ").strip()

    if choice == "1":
        prompt = input("📝 Enter your prompt:\n>>> ").strip()
        return prompt

    elif choice == "2":
        instruction = input("📝 Describe what the AI should do with this file:\n>>> ").strip()
        file_path = input("📄 Enter full path to the file: ").strip().strip('"').strip("'")

        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".txt":
            content = read_txt(file_path)
        elif ext == ".pdf":
            content = read_pdf(file_path)
        elif ext == ".csv":
            content = read_csv(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")

        return {
            "prompt": instruction,
            "content": content
        }

    else:
        raise ValueError("Invalid input choice.")


# === File Parser for Backend Use ===
def parse_file_only(file_path, file_ext):
    ext = file_ext.lower()

    if ext == ".txt":
        return read_txt(file_path)
    elif ext == ".pdf":
        return read_pdf(file_path)
    elif ext == ".csv":
        return read_csv(file_path)
    else:
        raise ValueError(f"Unsupported file extension: {ext}")
