📝 Note Summarizer V2

A modern, AI-powered note summarizer web app built with **Python**, **Streamlit**, and **Google Gemini**.  
This tool allows you to upload notes in **plain text**, **DOCX**, or **PDF** format and generate **clear, structured summaries** using multiple output styles, preview extracted content, and export results — all while operating on the **free Gemini API tier**.

---

🚀 Features

📂 File Upload  
- Supports **.docx** and **.pdf** files  
- Preview extracted PDF text before summarization  

✍️ Text Input  
- Paste or type notes directly  

🧠 AI Summarization  
- Powered by **Google Gemini** for high-quality results  
- Multiple summary modes:
  - Bullets
  - Key Takeaways
  - Action Items
  - Study Notes
  - Flashcards (Q&A)
- Adjustable summary length: **Short / Medium / Long**
- Optional **PDF page citations**

📤 Export & Productivity  
- Export summaries as **Markdown**, **DOCX**, or **PDF**
- Local history storage to revisit past summaries
- Free-tier friendly design with retries and caching

🌐 Interactive Web App  
- Built with **Streamlit** for a clean, responsive UI  
- Graceful handling of API rate limits and model overloads  

---

⚙️ Setup Instructions

1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

3️⃣ Get a Google Gemini API Key  
- Sign up for **Google AI Studio**  
- Create a new API key under your project settings  

4️⃣ Configure Environment Variables  

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_google_gemini_api_key_here
```

> ⚠️ Do not commit `.env` to GitHub.  
> Use `.env.example` as a reference.

5️⃣ Run the App

```bash
streamlit run app.py
```

---

💡 Usage

- Open the app in your browser (Streamlit will provide a local URL)
- Upload a **.docx** or **.pdf** file, or paste your notes
- Choose summary mode, length, and options
- Click **Summarize**
- View and export your summary

---

🛠️ How It Works

- **File Handling:** Uses `python-docx` and `PyPDF2` to extract text from uploaded files  
- **Chunking:** Long documents are split into smaller chunks for reliable processing  
- **Summarization:** Each chunk is processed by Gemini and combined into a final summary  
- **Streamlit UI:** Provides an intuitive interface for interacting with the summarizer  

---

🧩 Troubleshooting

- **API Key Issues:** Ensure your `.env` file exists and contains a valid key  
- **503 / Model Overloaded:** Try shorter summaries, disable citations, or retry after a short wait  
- **PDF Issues:** Scanned (image-only) PDFs may not extract text correctly  

---

📜 License

This project is for **educational and demonstration purposes only**.

---

Happy Summarizing! 🎉
