from markdown import markdown
from weasyprint import HTML
import os

def markdown_to_pdf(markdown_text, output_path):
    html_text = markdown(markdown_text, extensions=['markdown.extensions.tables', 'markdown.extensions.extra', 'markdown.extensions.nl2br'])
    styled_html = f"""
    <body>
        <style>
            body {{
            font-family: 'Arial', sans-serif;
            padding: 30px;
            background: #fefefe;
            }}
            .banner {{
            border: 2px solid #ddd;
            border-radius: 12px;
            padding: 30px;
            background-color: #fffbe6;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            text-align: center;
            }}
            img {{
            max-width: 100%;
            }}
            h1, h2, h3 {{
            color: #d6336c;
            }}
        </style>
        <div class="banner">
            {html_text}
        </div>
    </body>
    </html>
    """
    HTML(string=styled_html).write_pdf(output_path)
    
    
def export_md(markdown_content, output_filename):
    os.makedirs("markdowns", exist_ok=True)
    file_path = os.path.join("markdowns", output_filename)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)