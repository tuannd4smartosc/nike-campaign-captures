import streamlit as st
from serper import search_web, scrape_web_page
from llm import query_gpt
from files import markdown_to_pdf, export_md
import uuid
from utils import clean_markdown, export_md_with_link, get_pdf_download_link
import os
from logger import StreamlitLogger  # Assuming StreamlitLogger is in this file

# Instantiate the logger
logger = StreamlitLogger()

allowed_regions = ["sg", "kr", "us", "in", "jp", "vn", "au", "my", "id"]

def generate_prompt(company_name):
    return f"""
       All {company_name}'s promotion campaigns
    """

def list_markdown_files():
    """List all markdown files in the /markdowns directory."""
    markdown_dir = "markdowns"
    if not os.path.exists(markdown_dir):
        os.makedirs(markdown_dir)
    
    # Get list of all markdown files in the directory
    markdown_files = [f for f in os.listdir(markdown_dir) if f.endswith('.md')]
    return markdown_files

def load_markdown_file(file_name):
    """Load the content of a markdown file."""
    markdown_dir = "markdowns"
    file_path = os.path.join(markdown_dir, file_name)
    
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return f.read()
    else:
        return "File not found."

def main():
    # Main Panel: Input fields at the top
    st.title("Promotion Campaigns Snapshot Generator")
    
    # Create columns for input fields (Company name and region)
    col1, col2 = st.columns(2)
    
    with col1:
        company_name = st.text_input("What company do you want to capture in the past week?", "")
        
    with col2:
        region = st.selectbox("What is the focused region?", allowed_regions)
    
    # Action button for generating snapshot
    if st.button("Generate Snapshot"):
        if region not in allowed_regions:
            logger.log("Invalid region selected! We only accept: sg, kr, us, in, jp, vn, au, my, id", level="ERROR")
            st.error("Invalid region! Please select a valid region.")
            return

        query = generate_prompt(company_name)
        logger.log(f"Searching for promotions related to {company_name} in {region}...", level="INFO")
        
        # Search and get results
        search_results = search_web(query, region)
        logger.log(f"Found {len(search_results)} search results.", level="INFO")
        
        urls = [result['link'] for result in search_results]
        logger.log(f"Extracted URLs: {urls}", level="INFO")

        mds = []
        for url in urls:
            data = scrape_web_page(url)
            if "markdown" in data:
                markdown = data["markdown"]
                logger.log(f"Start extracting: {url}")
                extracted_markdown = query_gpt(markdown, company_name)
                os.makedirs("snaps", exist_ok=True)
                cleaned_markdown = clean_markdown(extracted_markdown)
                combined_md = export_md_with_link(cleaned_markdown, url)
                mds.append(combined_md)
                logger.log(f"Finished extracting: {url}")
        
        final_md = '\n\n---\n\n'.join(mds)
        filename = f"snap-{uuid.uuid4().hex}.md"
        export_md(final_md, filename)
        
        logger.log(f"Snapshot saved as {filename}", level="INFO")
        st.success(f"Snapshot successfully saved as {filename}!")
    
    # Display selected markdown files below the inputs
    st.subheader("Click on the button below to download all snapshots")
    
    # Sidebar: List all markdown files in the /markdowns directory
    st.sidebar.title("Markdown Files")
    markdown_files = list_markdown_files()
    
    if markdown_files:
        selected_file = st.sidebar.selectbox("Select a Markdown file", markdown_files)
        
        # Display the selected markdown content in the main panel
        markdown_content = load_markdown_file(selected_file)
        if st.button("Generate PDF"):
            # Convert the markdown content to a PDF
            if not os.path.exists("pdfs"):
                os.makedirs("pdfs")
            pdf_path = os.path.join("pdfs", selected_file.replace(".md", ".pdf"))
            markdown_to_pdf(markdown_content, pdf_path)
            
            # Provide the download link for the PDF file
            st.markdown(get_pdf_download_link(pdf_path, selected_file.replace(".md", ".pdf")), unsafe_allow_html=True)
        st.divider()
        st.markdown(markdown_content)
        
    else:
        st.sidebar.warning("No markdown files found in '/markdowns' directory.")
    
# Run the Streamlit app
if __name__ == "__main__":
    main()
