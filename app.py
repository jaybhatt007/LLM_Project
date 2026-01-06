import os
from dotenv import load_dotenv
from pathlib import Path
import streamlit as st
from google import genai

from utils.extract import extract_text_from_docx, extract_text_from_pdf
from utils.summarizer import summarize, SummarizeConfig
from utils.exports import to_markdown_bytes, to_docx_bytes, to_pdf_bytes
from utils.db import init_db, save_summary, search_history, get_summary

st.set_page_config(page_title="Note Summarizer V2", page_icon="📝", layout="wide")

# Load .env
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    st.error("GOOGLE_API_KEY not found in .env. Add it and restart Streamlit.")
    st.stop()

client = genai.Client(api_key=GOOGLE_API_KEY)

# Sidebar history
st.sidebar.title("📚 History")
init_db()
q = st.sidebar.text_input("Search history", "")
items = search_history(q, limit=50)

selected_id = None
if items:
    labels = ["(none)"]
    mapping = {}
    for it in items:
        fname = it.get("filename") or it.get("source_type")
        label = f"#{it['id']} • {fname} • {it['mode']} • {it['created_at']}"
        labels.append(label)
        mapping[label] = it["id"]

    choice = st.sidebar.selectbox("Load previous summary", labels)
    if choice != "(none)":
        selected_id = mapping[choice]

st.title("📝 Note Summarizer V2")
st.write("Upload PDF/DOCX or paste text. Choose mode, length, citations. Export to MD/DOCX/PDF + save history.")

# Controls
c1, c2, c3, c4 = st.columns([1.2, 1, 1, 1])

with c1:
    mode = st.selectbox("Mode", ["Bullets", "Key Takeaways", "Action Items", "Study Notes", "Flashcards"], index=0)
with c2:
    length = st.selectbox("Length", ["Short", "Medium", "Long"], index=1)
with c3:
    include_citations = st.checkbox("PDF page citations", value=True)
with c4:
    model_name = st.selectbox("Model", ["gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-2.5-pro"], index=0)

st.divider()

uploaded = st.file_uploader("Upload a file (.docx, .pdf):", type=["docx", "pdf"])

note_text = ""
pages = None
source_type = "text"
filename = None
MAX_PDF_PAGES = 120

if uploaded:
    filename = uploaded.name
    if uploaded.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        extracted = extract_text_from_docx(uploaded)
        note_text, pages = extracted.text, None
        source_type = "docx"
    elif uploaded.type == "application/pdf":
        extracted = extract_text_from_pdf(uploaded, max_pages=MAX_PDF_PAGES)
        note_text, pages = extracted.text, extracted.pages
        source_type = "pdf"
        if (pages and len(pages) >= MAX_PDF_PAGES):
            st.info(f"PDF limited to first {MAX_PDF_PAGES} pages for safety/performance.")
else:
    note_text = st.text_area("Or paste your notes:", "", height=220)

with st.expander("Preview extracted text"):
    st.write(note_text[:2000] + ("..." if len(note_text) > 2000 else ""))

cfg = SummarizeConfig(
    model=model_name,
    mode=mode,
    length=length,
    include_citations=(include_citations and source_type == "pdf")
)

@st.cache_data(show_spinner=False)
def cached_run(text: str, cfg_dict: dict, pages_small):
    cfg_obj = SummarizeConfig(**cfg_dict)
    return summarize(client, text, cfg_obj, pages=pages_small)

run = st.button("✨ Summarize", type="primary")
summary = None

if run:
    if not note_text.strip():
        st.warning("Please upload a file or paste text.")
        st.stop()

    with st.spinner("Summarizing..."):
        pages_small = pages if cfg.include_citations else None
        summary = cached_run(
            note_text,
            cfg_dict={
                "model": cfg.model,
                "mode": cfg.mode,
                "length": cfg.length,
                "include_citations": cfg.include_citations,
            },
            pages_small=pages_small,
        )

    st.subheader("✅ Summary")
    st.write(summary)

    save_summary(filename, source_type, mode, length, model_name, len(note_text), summary)

    st.subheader("⬇️ Export")
    e1, e2, e3 = st.columns(3)

    md_name = f"{Path(filename).stem}_summary.md" if filename else "summary.md"
    docx_name = f"{Path(filename).stem}_summary.docx" if filename else "summary.docx"
    pdf_name = f"{Path(filename).stem}_summary.pdf" if filename else "summary.pdf"

    with e1:
        st.download_button("Download .md", to_markdown_bytes(summary), file_name=md_name, mime="text/markdown")
    with e2:
        st.download_button("Download .docx", to_docx_bytes("Summary", summary), file_name=docx_name,
                           mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    with e3:
        st.download_button("Download .pdf", to_pdf_bytes("Summary", summary), file_name=pdf_name, mime="application/pdf")

# Show loaded history
if selected_id and not run:
    saved = get_summary(int(selected_id))
    if saved:
        st.subheader(f"📌 Loaded Summary #{saved['id']}")
        st.write(saved["summary"])
