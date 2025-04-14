import os
from dotenv import load_dotenv
import google.generativeai as genai
import streamlit as st
from docx import Document
from PyPDF2 import PdfReader

# Loading the APi from .env #
load_dotenv()
API_KEY = os.getenv("API_KEY")

# defining the model of GenAi Model #
genai.configure(api_key = API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# Writhing the Prompt what is needed from the model #
def summarize_note(note_text):
    prompt = f""" 
    you are a helpful assistance. your task is to summarize the following notes in a clear, concise and easy ti understand format.
    Pleaser summarize the key points while preserving the important information. avoid unnecessary details.

    Note:
    {note_text}
    """
    response = model.generate_content(prompt)
    result = response.text
    return result

# Using Streamlit UI for web interface #

st.title("Note Summarizer")
st.write("Enter your notes and get a summarized version of it.")

note_text = st.text_area("Enter your note here:","")    # User input #

if st.button("Summarize"):
    if note_text:
        summary = summarize_note(note_text)
        st.subheader("Summary:")
        st.write(summary)
    else:
        st.warning("Please enter a note to summarize.")

# Extracting the text from the doc file #

def extract_text_from_docx(file):
    document = Document(file)
    full_text = [paragraph.text for paragraph in document.paragraphs]
    return "\n".join(full_text)

# Extracting  the text from the PDF file #

def  extract_text_from_pdf(file):
    pdf_reader = PdfReader(file)
    full_text = [page.extract_text() for page in pdf_reader.page]
    return "\n".join(full_text)


# Determing the file type #

uploaded_file = st.file_uploader("Upload a file (.docx, .pdf):" , type=["docx","pdf"]) # Uploading a file #

if uploaded_file:
    if uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        note_text = extract_text_from_docx(uploaded_file)
    elif uploaded_file == "application/pdf":
        note_text = extract_text_from_pdf(uploaded_file)
    else:
        st.error("Unsupported file type.")
        note_text = None
else:
    note_text = st.text_area("Or enter your note here:", "")
