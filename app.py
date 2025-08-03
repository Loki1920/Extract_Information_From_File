import streamlit as st
import os
import json
import PyPDF2
import docx
import openai
import re
import ast

from dotenv import load_dotenv

load_dotenv()

# Set page config
st.set_page_config(page_title="Document Section Extractor", layout="wide")

# Load API key from environment variable
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    st.error("API key not found. Please set the GROQ_API_KEY environment variable.")
    st.stop()

# Initialize OpenAI client for Groq API
client = openai.OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=GROQ_API_KEY,
)

def extract_text(filename):
    ext = os.path.splitext(filename)[1].lower()
    pages = []

    if ext == ".pdf":
        with open(filename, "rb") as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for i, page in enumerate(pdf_reader.pages):
                text = page.extract_text()
                pages.append({"page_num": i + 1, "text": text or ""})

    elif ext == ".docx":
        doc = docx.Document(filename)
        full_text = [para.text for para in doc.paragraphs]
        pages.append({"page_num": 1, "text": "\n".join(full_text)})

    elif ext == ".txt":
        with open(filename, "r", encoding="utf-8") as f:
            text = f.read()
            pages.append({"page_num": 1, "text": text})

    else:
        raise ValueError(f"Unsupported file type: {ext}")

    return pages

def parse_sections_with_llm_chunked_all_pages(pages):
    all_sections = []

    for page in pages:
        if not page['text'].strip():
            all_sections.append({
                "subject_title": None,
                "section_type": "No Content",
                "starting_page_no": page['page_num'],
                "ending_page_no": page['page_num'],
                "entities": [],
                "subsections": [],
                "raw_text": ""
            })
            continue

        prompt = f"""
You are a document parser. Given the following page, extract its main sections and for each section, provide:
- subject_title (section header)
- section_type (guess if not explicit)
- starting_page_no
- ending_page_no
- entities (list of key named entities, e.g. company names, dates, financial figures, etc.)
- subsections (leave empty for now)

Format your output as a JSON list, as in this example:
[
  {{
    "subject_title": "<section_header>",
    "section_type": "Document Title",
    "starting_page_no": 1,
    "ending_page_no": 1,
    "entities": [{{"company name": "Amazon", "publication year": "2024"}}],
    "subsections": []
  }},
  ...
]

Page {page['page_num']}:
{page['text']}
"""

        try:
            response = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )
            content = response.choices[0].message.content

            # Extract JSON from response
            json_str = re.search(r'(\[.*\])', content, re.DOTALL)
            if json_str:
                parsed = json.loads(json_str.group(1))
            else:
                parsed = ast.literal_eval(content)

            if isinstance(parsed, list) and parsed:
                all_sections.extend(parsed)
            else:
                all_sections.append({
                    "subject_title": None,
                    "section_type": "No Section Detected",
                    "starting_page_no": page['page_num'],
                    "ending_page_no": page['page_num'],
                    "entities": [],
                    "subsections": [],
                    "raw_text": page['text']
                })

        except Exception as e:
            st.error(f"Error parsing page {page['page_num']}: {e}")
            all_sections.append({
                "subject_title": None,
                "section_type": "Parsing Error",
                "starting_page_no": page['page_num'],
                "ending_page_no": page['page_num'],
                "entities": [],
                "subsections": [],
                "raw_text": page['text']
            })

    return all_sections

def main():
    st.title("Document Section Extractor with LLM")

    uploaded_file = st.file_uploader("Upload a PDF, DOCX, or TXT file", type=["pdf", "docx", "txt"])

    if uploaded_file:
        # Save uploaded file temporarily
        with open(uploaded_file.name, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.info(f"Extracting text from {uploaded_file.name}...")
        try:
            pages = extract_text(uploaded_file.name)
        except Exception as e:
            st.error(f"Failed to extract text: {e}")
            return

        st.success(f"Extracted text from {len(pages)} page(s).")

        if st.button("Parse Document with LLM"):
            with st.spinner("Parsing document..."):
                structured_json = parse_sections_with_llm_chunked_all_pages(pages)

            st.success("Parsing complete!")

            # Display JSON output
            st.subheader("Parsed Document Structure")
            st.json(structured_json)

            # Provide download button for JSON
            json_str = json.dumps(structured_json, indent=2, ensure_ascii=False)
            st.download_button(
                label="Download JSON",
                data=json_str,
                file_name="parsed_document.json",
                mime="application/json"
            )

        # Clean up temp file
        try:
            os.remove(uploaded_file.name)
        except Exception:
            pass

if __name__ == "__main__":
    main()