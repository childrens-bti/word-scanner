import streamlit as st
from docx import Document
from docx.shared import Pt, RGBColor
import fitz  # PyMuPDF
import io
import re
import pandas as pd
import os

st.set_page_config(page_title="Banned Word Scanner", layout="wide")
st.title("🔍 Banned Word Scanner for DOCX and PDF")

# --- Helper Functions ---
def extract_text_from_docx(file):
    doc = Document(file)
    return "\n".join([p.text for p in doc.paragraphs])

def extract_text_from_pdf(file):
    pdf = fitz.open(stream=file.read(), filetype="pdf")
    return "\n".join([page.get_text() for page in pdf])

def highlight_banned_words(text, banned_words):
    pattern = r"\b(" + "|".join(map(re.escape, banned_words)) + r")\b"
    matches = list(re.finditer(pattern, text, flags=re.IGNORECASE))

    spans = []
    for m in matches:
        span_start = max(0, m.start() - 40)
        span_end = min(len(text), m.end() + 40)
        context = text[span_start:span_end].replace(m.group(), f"**{m.group()}**")
        spans.append({
            "word": m.group(),
            "start_pos": m.start(),
            "end_pos": m.end(),
            "context": context
        })
    return spans

def generate_word_doc(results):
    doc = Document()
    doc.add_heading('Banned Words Report', level=1)
    for entry in results:
        p = doc.add_paragraph()
        p.add_run("Word: ").bold = True
        p.add_run(entry['word'] + "\n")
        p.add_run("Location: ").bold = True
        p.add_run(f"{entry['start_pos']} - {entry['end_pos']}\n")
        p.add_run("Context: ").bold = True
        # Highlight banned word in context
        context = entry['context']
        match = re.search(r"\*\*(.+?)\*\*", context)
        if match:
            before, word, after = context.split("**", 2)
            r = p.add_run(before)
            r = p.add_run(word)
            r.font.highlight_color = 3  # Yellow highlight
            r = p.add_run(after)
        else:
            p.add_run(context)
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

def parse_banned_words(file):
    if file is None:
        return []
    content = file.read().decode("utf-8")
    return parse_banned_words_from_string(content)

def parse_banned_words_from_string(content):
    words = []
    for line in content.splitlines():
        line = line.strip()
        if line.startswith('"') and line.endswith('"'):
            words.append(line.strip('"'))
        elif line:
            words.append(line)
    return words

def load_default_banned_words_from_file(path="default_words.txt"):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return parse_banned_words_from_string(f.read())
    return []

# --- Precompiled Banned Words ---
DEFAULT_BANNED_WORDS = load_default_banned_words_from_file()

# --- Sidebar Inputs ---
st.sidebar.header("⚙️ Options")
use_default = st.sidebar.checkbox("Use default banned words", value=True)
text_input = st.sidebar.text_area("Enter additional banned words (one per line or quoted phrase)")
text_file = st.sidebar.file_uploader("Or upload a .txt file with banned words", type=["txt"])

uploaded_file = st.file_uploader("Upload a DOCX or PDF file", type=["docx", "pdf"])

if uploaded_file and (use_default or text_input or text_file):
    custom_words = [w.strip() for w in text_input.splitlines() if w.strip()]
    file_words = parse_banned_words(text_file)

    banned_words = DEFAULT_BANNED_WORDS if use_default else []
    banned_words += custom_words + file_words

    if uploaded_file.name.endswith(".docx"):
        text = extract_text_from_docx(uploaded_file)
    elif uploaded_file.name.endswith(".pdf"):
        uploaded_file.seek(0)
        text = extract_text_from_pdf(uploaded_file)
    else:
        st.error("Unsupported file type.")
        st.stop()

    st.subheader("📄 Full Text Preview")
    with st.expander("Show Document Text"):
        st.text_area("Extracted Text", value=text[:10000], height=300)

    st.subheader("🚫 Banned Words Found")
    results = highlight_banned_words(text, banned_words)

    if results:
        df = pd.DataFrame(results)
        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download Results as CSV", data=csv, file_name="banned_word_hits.csv")

        word_buffer = generate_word_doc(results)
        st.download_button("Download Results as Word Document", data=word_buffer, file_name="banned_word_hits.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    else:
        st.success("No banned words found in the document.")

elif uploaded_file:
    st.info("Please enter or enable at least one banned word list to scan the document.")
