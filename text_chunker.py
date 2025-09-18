def chunk_text(text, max_tokens=700):
    """
    Splits a long string into smaller chunks based on character length.
    This ensures it stays within token limits of most LLMs.
    """
    import textwrap

    # Approx: 1 token ≈ 4 characters (safe upper bound)
    max_chars = max_tokens * 4
    paragraphs = text.split('\n\n')

    chunks = []
    current_chunk = ""

    for para in paragraphs:
        if len(current_chunk) + len(para) < max_chars:
            current_chunk += para + "\n\n"
        else:
            chunks.append(current_chunk.strip())
            current_chunk = para + "\n\n"

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks
