from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
import os
from werkzeug.utils import secure_filename
from agent_orchestrator import run_agent_from_api

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure key
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), 'outputs')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'csv'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET'])
def home():
    chat_history = []
    return render_template('layout.html', chat_history=chat_history, generated_content=None, download_url=None)

@app.route('/generate', methods=['POST'])
def generate():
    prompt = request.form.get('prompt', '')
    doc_type = request.form.get('doc_type', 'docx')
    file = request.files.get('document')
    filename = None
    file_path = None

    # Handle file upload
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        flash(f'File "{filename}" uploaded successfully.', 'success')
    elif file and file.filename != '':
        flash('Invalid file type. Allowed: txt, pdf, csv.', 'danger')
        file_path = None

    # Call your agent pipeline (API entry point)
    try:
        output_path = run_agent_from_api(prompt, file_path, output_format=doc_type)
        output_filename = os.path.basename(output_path)
        download_url = url_for('download', filename=output_filename)
        generated_content = f"Document generated successfully as <b>{output_filename}</b>."
    except Exception as e:
        generated_content = f"❌ Error generating document: {e}"
        download_url = None

    chat_history = []
    return render_template('layout.html',
                           chat_history=chat_history,
                           generated_content=generated_content,
                           download_url=download_url)

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port = 5001)
