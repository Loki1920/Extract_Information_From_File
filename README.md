
Document Parser with LLM

This project implements a document parser using a Large Language Model (LLM) to extract structured information from documents in PDF, DOCX, or TXT format. The parser processes each page, extracts sections and entities, and outputs a structured JSON file. The solution ensures no page is skipped, even if the LLM does not detect a section.

📂 Files Included
Colab Notebook / Python Script:

Sample Output JSON:
parsed_document.json (generated from sample_document.pdf)
README.md:
(This file)
🚀 LLM Choice

Model Used:
llama3-70b-8192 via Groq API (OpenAI-compatible endpoint)

Why this model?

Strong performance on document understanding and information extraction tasks.
OpenAI API compatibility for easy integration.
Cost-effective and fast for batch processing.
🛠️ Design Decisions & Challenges
Chunked Page Processing:
To avoid token limit errors, the document is processed one page at a time. This ensures compatibility with large documents and prevents API errors.
No Data Loss:
Every page is represented in the output. If the LLM does not detect a section, a placeholder entry is added with the raw text.
Flexible File Support:
Supports PDF, DOCX, and TXT files, automatically detecting the file type and extracting text accordingly.
Robust JSON Parsing:
Handles various LLM output formats and ensures the final output is valid JSON.
User-Friendly:
The notebook provides clear instructions and allows easy upload and download of files.

Challenges:

Token Limit Errors:
Sending the entire document at once exceeded the LLM’s token limit. This was solved by processing each page individually.
Section Boundary Detection:
Some sections span multiple pages. Processing per page may split such sections, but this approach ensures no data is missed and every page is accounted for.
📝 How to Run
Open the Colab notebook (insert link here) or run the Python script.
Upload your document (PDF, DOCX, or TXT) when prompted.
The code will extract text from each page and send it to the LLM for parsing.
Every page is processed:
If a section is detected, it is added to the output.
If no section is detected, a placeholder with the raw text is added.
The final structured JSON output is saved as parsed_document.json and can be downloaded directly from the notebook.
📊 Example Output
[
  {
    "subject_title": "Section Title",
    "section_type": "Section Header",
    "starting_page_no": 1,
    "ending_page_no": 1,
    "entities": [{"author": "John Doe"}],
    "subsections": []
  },
  {
    "subject_title": null,
    "section_type": "No Section Detected",
    "starting_page_no": 2,
    "ending_page_no": 2,
    "entities": [],
    "subsections": [],
    "raw_text": "Raw text from page 2..."
  }
]

🧑‍💻 Instructions for Evaluators
Upload any supported document and run all cells in the notebook.
Check the output JSON to verify that every page is represented.
Review the code comments and documentation for clarity and design rationale.
📬 Contact

For any questions or clarifications, please contact:
Lucky Tiwari
luckysandilya19@gmail.com

Thank you for evaluating this submission!
