import re
import codecs
import streamlit as st

def clean_markdown(text):
    # Step 1: Remove triple backticks and language hint (```markdown)
    cleaned = re.sub(r"^```markdown|```$", "", text.strip(), flags=re.MULTILINE)

    # Step 2: Decode escape sequences (like \n)
    markdown = codecs.decode(cleaned, 'unicode_escape')
    return markdown

def export_md_with_extra_markdown(markdown, extra):
    final_md = f"""
    \n\n\n\n{extra}\n
    {markdown}
    """
    # export_md(final_md, f"snap-{uuid.uuid4().hex}.md")
    return final_md

def get_pdf_download_link(pdf_path, filename):
    with open(pdf_path, "rb") as f:
        pdf_data = f.read()
    return st.download_button(
        label="Download PDF",
        data=pdf_data,
        file_name=filename,
        mime="application/pdf",
    )