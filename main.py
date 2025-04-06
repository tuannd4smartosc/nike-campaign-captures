from serper import search_web, scrape_web_page
from llm import query_gpt
from files import markdown_to_pdf, export_md
import uuid
from utils import clean_markdown, export_md_with_link
import os

def generate_prompt(company_name):
    return f"""
       All {company_name}'s promotion campaigns
    """

allowed_regions = ["sg", "kr", "us", "in", "jp", "vn", "au", "my", "id"]

def main():
    company_name = input("What company do you want to capture in the past week? ")
    region = input("What is the focused region? ")
    
    if region not in allowed_regions:
        print("Invalid regions! We only accept: sg, kr, us, in, jp, vn, au, my, id")
        return
    
    query = generate_prompt(company_name)
    search_results = search_web(query, region)
    print("search_results", search_results)
    urls = [result['link'] for result in search_results]
    print("urls: ", urls)
    mds = []
    for url in urls:
        data = scrape_web_page(url)
        if "markdown" in data:
            markdown = data["markdown"]
            extracted_markdown = query_gpt(markdown, company_name)
            os.makedirs("snaps", exist_ok=True)
            cleaned_markdown = clean_markdown(extracted_markdown)
            combined_md = export_md_with_link(cleaned_markdown, url)
            mds.append(combined_md)
    export_md('\n\n---\n\n'.join(mds), f"snap-{uuid.uuid4().hex}.md")
    print("DONE!")
    
if __name__ == "__main__":
    main()