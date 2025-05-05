import streamlit as st
from docx import Document
import fitz  # PyMuPDF
import io
import re
import pandas as pd

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
    # Escape and join into regex
    pattern = r"\\b(" + "|".join(map(re.escape, banned_words)) + r")\\b"
    matches = list(re.finditer(pattern, text, flags=re.IGNORECASE))
    
    spans = []
    for m in matches:
        span_start = max(0, m.start() - 40)
        span_end = min(len(text), m.end() + 40)
        context = text[span_start:span_end].replace(m.group(), f"**{m.group()}**")
        spans.append({"word": m.group(), "context": context})
    return spans

# --- Sidebar Inputs ---
st.sidebar.header("⚙️ Options")
banned_input = st.sidebar.text_area("Enter banned words (one per line)")

uploaded_file = st.file_uploader("Upload a DOCX or PDF file", type=["docx", "pdf"])

if uploaded_file and banned_input:
    banned_words = [w.strip() for w in banned_input.splitlines() if w.strip()]
    
    if uploaded_file.name.endswith(".docx"):
        text = extract_text_from_docx(uploaded_file)
    elif uploaded_file.name.endswith(".pdf"):
        # Reopen file for reading as it was read by fitz
        uploaded_file.seek(0)
        text = extract_text_from_pdf(uploaded_file)
    else:
        st.error("Unsupported file type.")
        st.stop()

    st.subheader("📄 Full Text Preview")
    with st.expander("Show Document Text"):
        st.text_area("Extracted Text", value=text[:5000], height=200)

    st.subheader("🚫 Banned Words Found")
    results = highlight_banned_words(text, banned_words)

    if results:
        df = pd.DataFrame(results)
        st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download Results as CSV", data=csv, file_name="banned_word_hits.csv")
    else:
        st.success("No banned words found in the document.")

elif uploaded_file:
    st.info("Please enter at least one banned word in the sidebar to scan the document.")

