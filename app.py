import streamlit as st
from serper import search_web, scrape_web_page
from llm import query_gpt
from files import export_md
import uuid
from utils import clean_markdown, export_md_with_extra_markdown
import os
from logger import StreamlitLogger

# Instantiate the logger
logger = StreamlitLogger()

allowed_regions = ["sg", "kr", "us", "in", "jp", "vn", "au", "my", "id"]

def generate_prompt(company_name):
    return f"""
       All {company_name}'s promotion campaigns
    """

def list_folders():
    """List all folders in the /reports directory."""
    markdown_dir = "reports"
    if not os.path.exists(markdown_dir):
        os.makedirs(markdown_dir)
    return [d for d in os.listdir(markdown_dir) if os.path.isdir(os.path.join(markdown_dir, d))]

def list_markdown_files(folder_name):
    """List all markdown files in the specified folder within /reports."""
    folder_path = os.path.join("reports", folder_name)
    if os.path.exists(folder_path):
        return [f for f in os.listdir(folder_path) if f.endswith('.md')]
    return []

def load_markdown_file(folder_name, file_name):
    """Load the content of a markdown file from the specified folder."""
    file_path = os.path.join("reports", folder_name, file_name)
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return f.read()
    return "File not found."

def display_carousel(contents, label, index_key):
    """Display a carousel for the given contents with navigation buttons."""
    if not contents:
        return
    
    # Initialize index in session state
    if index_key not in st.session_state:
        st.session_state[index_key] = 0
    
    # Navigation buttons
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        if st.button("Previous", key=f"{index_key}_prev"):
            st.session_state[index_key] = (st.session_state[index_key] - 1) % len(contents)
    with col3:
        if st.button("Next", key=f"{index_key}_next"):
            st.session_state[index_key] = (st.session_state[index_key] + 1) % len(contents)
    
    # Display current content
    with col2:
        st.write(f"Showing {st.session_state[index_key] + 1} of {len(contents)}")
    st.markdown(contents[st.session_state[index_key]])

def main():
    st.title("Promotion Campaigns Snapshot Generator")
    
    # Initialize session state variables
    if 'selected_folder' not in st.session_state:
        st.session_state.selected_folder = None
    if 'generated_mds' not in st.session_state:
        st.session_state.generated_mds = []
    
    # Create columns for input fields
    col1, col2 = st.columns(2)
    
    with col1:
        company_name = st.text_input("What company do you want to capture in the past week?", "")
        
    with col2:
        region = st.selectbox("What is the focused region?", allowed_regions)
    
    # Sidebar: List folders
    st.sidebar.title("Campaign Folders")
    folders = list_folders()
    
    if folders:
        st.session_state.selected_folder = st.sidebar.selectbox(
            "Select a Campaign Folder", 
            folders,
            index=len(folders)-1 if st.session_state.selected_folder is None else folders.index(st.session_state.selected_folder)
        )
    
    # Action button for generating snapshot with unique key
    if st.button("Generate Snapshot", key="generate_snapshot"):
        if region not in allowed_regions:
            logger.log("Invalid region selected! We only accept: sg, kr, us, in, jp, vn, au, my, id", level="ERROR")
            st.error("Invalid region! Please select a valid region.")
            return

        query = generate_prompt(company_name)
        logger.log(f"Searching for promotions related to {company_name} in {region}...", level="INFO")
        
        search_results = search_web(query, region)
        logger.log(f"Found {len(search_results)} search results.", level="INFO")
        
        urls = [result['link'] for result in search_results]
        logger.log(f"Extracted URLs: {urls}", level="INFO")

        mds = []
        folder_name = f"snap-{uuid.uuid4().hex}"
        folder_path = os.path.join("reports", folder_name)
        os.makedirs(folder_path, exist_ok=True)

        for i, result in enumerate(search_results):
            url = result['link']
            title = result['title']
            data = scrape_web_page(url)
            if "markdown" in data:
                markdown = data["markdown"]
                logger.log(f"Start extracting: {url}")
                extracted_markdown = query_gpt(markdown, company_name)
                cleaned_markdown = clean_markdown(extracted_markdown)
                combined_md = export_md_with_extra_markdown(cleaned_markdown, f"## {title}\n*Reference: [{url}]({url})*")
                mds.append(combined_md)
                
                # Save individual markdown file
                filename = f"result_{i+1}.md"
                export_md(combined_md, filename, folder_path)
                logger.log(f"Finished extracting and saved: {url} as {filename}")
        
        if mds:
            st.session_state.generated_mds = mds
            st.session_state.selected_folder = folder_name
            logger.log(f"Snapshot saved in folder {folder_name}", level="INFO")
            st.success(f"Snapshot successfully saved in folder {folder_name}!")
        else:
            st.warning("No markdown content generated from search results.")

    # Display generated reports with carousel if they exist
    if st.session_state.generated_mds:
        st.subheader("Generated Promotion Campaigns")
        display_carousel(st.session_state.generated_mds, "Generated Campaigns", "generated_carousel_index")

    # Display content from selected folder with carousel
    st.subheader(f"Weekly promotion campaigns")
    if st.session_state.selected_folder and folders:
        markdown_files = list_markdown_files(st.session_state.selected_folder)
        if markdown_files:
            markdown_contents = [load_markdown_file(st.session_state.selected_folder, f) for f in markdown_files]
            if markdown_contents:
                display_carousel(markdown_contents, "Folder Contents", "folder_carousel_index")
            else:
                st.warning("No valid markdown content found in selected folder.")
        else:
            st.warning("No markdown files found in selected folder.")
    elif not folders:
        st.sidebar.warning("No folders found in '/reports' directory.")

if __name__ == "__main__":
    main()