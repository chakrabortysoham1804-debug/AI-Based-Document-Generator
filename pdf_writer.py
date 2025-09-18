import os
import re
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, black
from reportlab.lib.units import inch

PAGE_WIDTH, PAGE_HEIGHT = LETTER
LEFT_MARGIN = RIGHT_MARGIN = inch * 0.7
TOP_MARGIN = BOTTOM_MARGIN = inch * 0.7
CONTENT_WIDTH = PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN
LINE_HEIGHT = 16

TITLE_COLOR = HexColor("#00205b")
SUBHEADING_COLOR = TITLE_COLOR
SUBSUBHEADING_COLOR = black
BODY_COLOR = black
FOOTER_COLOR = HexColor("#e4002b")
FOOTER_Y = 0.5 * inch

def generate_pdf(body, output_path="outputs/output.pdf", title="AI Generated PDF"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    c = canvas.Canvas(output_path, pagesize=LETTER)
    width, height = PAGE_WIDTH, PAGE_HEIGHT

    y = height - TOP_MARGIN

    # Draw centered title
    if title:
        clean_title = re.sub(r'^[#*\-_=\s]+|[#*\-_=\s]+$', '', title).strip()
        c.setFont("Helvetica-Bold", 16)
        c.setFillColor(TITLE_COLOR)
        c.drawCentredString(width / 2, y, clean_title)
        y -= 36

    body_clean = clean_text(body)
    sections = parse_sections(body_clean)

    c.setFont("Helvetica", 12)
    c.setFillColor(BODY_COLOR)

    for sec in sections:
        level = sec['level']
        heading = sec['heading']
        content = sec['body']

        if level == 1:
            y = draw_heading(c, heading, y, 16, TITLE_COLOR)
        elif level == 2:
            y = draw_heading(c, heading, y, 14, SUBHEADING_COLOR)
        elif level == 3:
            y = draw_heading(c, heading, y, 12, SUBSUBHEADING_COLOR)

        y = draw_body_content(c, content, y)

        # Add extra line gap between sections
        y -= LINE_HEIGHT

        # Create new page if reaching bottom margin
        if y < BOTTOM_MARGIN + 50:
            draw_footer(c)
            c.showPage()
            y = height - TOP_MARGIN
            c.setFont("Helvetica", 12)
            c.setFillColor(BODY_COLOR)

    draw_footer(c)
    c.save()
    print(f"📝 PDF saved to: {output_path}")

def clean_text(text):
    lines = text.splitlines()
    cleaned_lines = []
    in_table = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith('|') and stripped.endswith('|'):
            in_table = True
            cleaned_lines.append(line)
            continue
        elif in_table and stripped == '':
            in_table = False
            cleaned_lines.append(line)
            continue
        elif in_table:
            cleaned_lines.append(line)
            continue

        heading_match = re.match(r'^(#{1,3})\s+(.*)$', line)
        if heading_match:
            hashes, header_text = heading_match.groups()
            header_text = re.sub(r'[*=_\-\s]+$', '', header_text)
            header_text = re.sub(r'[*_]+', '', header_text)
            cleaned_lines.append(f"{hashes} {header_text.strip()}")
            continue

        if re.match(r'^[=\-*_]{3,}$', stripped):
            continue  # skip horizontal rules

        # Remove stray asterisks and underscores in other lines
        clean_line = re.sub(r'[*_]+', '', line)
        cleaned_lines.append(clean_line)

    return "\n".join(cleaned_lines)

def parse_sections(text):
    pattern = re.compile(r'^(#{1,3})\s+(.*)$', re.MULTILINE)
    matches = list(pattern.finditer(text))

    if not matches:
        return [{'level': 0, 'heading': '', 'body': text.strip()}]

    sections = []

    # Text before first heading
    if matches[0].start() > 0:
        pre = text[:matches[0].start()].strip()
        if pre:
            sections.append({'level': 0, 'heading': '', 'body': pre})

    for i, match in enumerate(matches):
        level = len(match.group(1))
        heading = match.group(2).strip()
        start = match.end()
        end = matches[i+1].start() if (i+1) < len(matches) else len(text)
        body = text[start:end].strip()
        sections.append({'level': level, 'heading': heading, 'body': body})

    return sections

def draw_heading(c, text, y, size, color):
    c.setFont("Helvetica-Bold", size)
    c.setFillColor(color)
    c.drawString(LEFT_MARGIN, y, text)
    return y - size - 6

def wrap_text(text, max_width, c, font_name, font_size):
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = f"{current_line} {word}".strip()
        if c.stringWidth(test_line, font_name, font_size) <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines

def draw_body_content(c, text, y):
    c.setFont("Helvetica", 12)
    c.setFillColor(BODY_COLOR)
    max_width = PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN

    for line in text.splitlines():
        line = line.strip()
        if not line:
            y -= 12
            continue
        is_bullet = bool(re.match(r'^[-+•]\s+', line))
        if is_bullet:
            bullet_width = c.stringWidth("• ", "Helvetica", 12) + 6
            text = re.sub(r'^[-+•]\s+', '', line)
            wrapped = wrap_text(text, max_width - bullet_width, c, "Helvetica", 12)
            for i, wline in enumerate(wrapped):
                x = LEFT_MARGIN + bullet_width if i == 0 else LEFT_MARGIN + bullet_width + 6
                c.drawString(x, y, wline)
                y -= LINE_HEIGHT
        else:
            wrapped = wrap_text(line, max_width, c, "Helvetica", 12)
            for wline in wrapped:
                c.drawString(LEFT_MARGIN, y, wline)
                y -= LINE_HEIGHT

        if y < BOTTOM_MARGIN + 50:
            draw_footer(c)
            c.showPage()
            y = PAGE_HEIGHT - TOP_MARGIN
            c.setFont("Helvetica", 12)
            c.setFillColor(BODY_COLOR)

    return y

def draw_footer(c):
    c.saveState()
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(FOOTER_COLOR)

    # Left-aligned branding
    c.drawString(LEFT_MARGIN, FOOTER_Y, "HPGPT")

    # Right-aligned page number
    page_num = f"Page {c.getPageNumber()}"
    text_width = c.stringWidth(page_num, "Helvetica-Bold", 10)
    c.drawString(PAGE_WIDTH - RIGHT_MARGIN - text_width, FOOTER_Y, page_num)

    c.restoreState()
