import os
import re
import time
import uuid

from input_handler import get_user_input, parse_file_only
from llm_agent import query_llama
from doc_writer import generate_docx
from pdf_writer import generate_pdf
from ppt_writer import generate_ppt
from text_chunker import chunk_text


# === Output Format Prompt ===

def get_output_format():
    print("\n📤 Choose output format:")
    print("1. Word Document (.docx)")
    print("2. PDF Document (.pdf)")
    print("3. Presentation (.pptx)")
    choice = input("Enter 1, 2, or 3: ").strip()
    if choice == "1":
        return "docx"
    elif choice == "2":
        return "pdf"
    elif choice == "3":
        return "pptx"
    else:
        raise ValueError("❌ Invalid output format choice.")

# === Filename Sanitizer ===

def sanitize_filename(text, extension):
    base = re.sub(r'[^\w\s-]', '', text).strip().lower()
    base = re.sub(r'[\s\-]+', '_', base)
    filename = base[:] if base else str(uuid.uuid4())[:8]
    return f"outputs/{filename}.{extension}"

# === Overwrite Prompt or Autoversion ===

def confirm_or_version(path):
    if not os.path.exists(path):
        return path
    while True:
        choice = input(f"\n⚠️ File '{path}' exists. Overwrite? (y/n): ").strip().lower()
        if choice == "y":
            return path
        elif choice == "n":
            base, ext = os.path.splitext(path)
            i = 2
            while os.path.exists(f"{base}({i}){ext}"):
                i += 1
            new_path = f"{base}({i}){ext}"
            print(f"📁 Creating new file: {new_path}")
            return new_path
        else:
            print("Please enter 'y' or 'n'")

# === Title & Body Extractor ===

def extract_title_and_body(response):
    """
    Expects the first line of response to be the markdown title: '# ...'
    Returns (title, body) tuple.
    If not found, uses a fallback.
    """
    lines = response.splitlines()
    title = None
    title_line_index = None
    for i, line in enumerate(lines):
        if line.strip().startswith("# "):
            title = re.sub(r'^#\s+', '', line.strip())
            title_line_index = i
            break
    if title:
        body_lines = lines[:title_line_index] + lines[title_line_index + 1 :]
        body = "\n".join(body_lines).strip()
        return title.strip(), body
    # fallback - use first non-empty line
    for line in lines:
        if line.strip():
            return line.strip(), "\n".join(lines[1:]).strip()
    return "Untitled Document", response.strip()

# === CLI Entry Point ===

def run_agent_pipeline():
    print("🔧 Starting AI document generation pipeline...")
    output_format = get_output_format()
    user_input = get_user_input()

    if isinstance(user_input, str):
        final_prompt = user_input
    else:
        final_prompt = f"{user_input['prompt']}\n\nHere is the file content:\n{user_input['content']}"

    print("\n🧠 Generating response...")
    response = query_llama(final_prompt)
    title, body = extract_title_and_body(response)

    os.makedirs("outputs", exist_ok=True)
    output_path = sanitize_filename(title, output_format)
    output_path = confirm_or_version(output_path)

    print("\n📄 Generating document...")
    if output_format == "docx":
        generate_docx(body=body, output_path=output_path, title=title.strip())
    elif output_format == "pdf":
        generate_pdf(body=body, output_path=output_path, title=title.strip())
    elif output_format == "pptx":
        generate_ppt(content=body, output_path=output_path, filename_title=title.strip())
    else:
        raise ValueError("Unsupported output format.")

    print(f"\n✅ Document saved to: {output_path}")
    print("✅ Document generation complete!")

# === API Entry Point ===

def run_agent_from_api(prompt, file_path=None, output_format='docx'):
    if file_path:
        ext = os.path.splitext(file_path)[1]
        file_content = parse_file_only(file_path, ext)
        full_prompt = f"{prompt}\n\n{file_content}"
    else:
        full_prompt = prompt

    # Chunk large input to respect token limits
    chunks = chunk_text(full_prompt, max_tokens=700)  # cautious chunk size
    combined_response = ""
    for chunk in chunks:
        response = query_llama(chunk)
        combined_response += response + "\n\n"
        time.sleep(2)  # delay to avoid rate limit

    title, body = extract_title_and_body(combined_response)

    os.makedirs('outputs', exist_ok=True)

    output_path = sanitize_filename(title, output_format)
    if os.path.exists(output_path):
        base, ext = os.path.splitext(output_path)
        i = 2
        while os.path.exists(f"{base}({i}){ext}"):
            i += 1
        output_path = f"{base}({i}){ext}"

    if output_format == 'docx':
        generate_docx(body, output_path, title)
    elif output_format == 'pdf':
        generate_pdf(body, output_path, title)
    elif output_format == 'pptx':
        generate_ppt(body, output_path, title)
    else:
        raise ValueError("Unsupported format.")

    return output_path