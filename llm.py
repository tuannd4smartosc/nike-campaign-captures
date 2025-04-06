import llm
from dotenv import load_dotenv
import os
import openai

load_dotenv()

def get_prompt(markdown_text: str, competitor_names: str):
    return f"""
    **Context**
    Given this full webpage markdown text:
    {markdown_text}
    
    **Your task**
    Your task is to extract only the markdown section that represents a promotion campaign banner of {competitor_names}.

    A promotion banner typically includes:
    - Bold headlines (e.g., **SALE**, **LIMITED OFFER**, etc.)
    - Promotional images (e.g., ![alt text](image-url))
    - Short descriptions or discount text (like "30% OFF", "Shop Now")
    - Clear visual separation (surrounded by horizontal rules, emojis, or spacing)

    Extract only the markdown for the banner section. It should be standalone and readable without any extra content. Output only the cleaned markdown block.
    """


def query_gpt(markdown_text, competitor_names:str):
    try:
        # Set the API key
        llm.api_key = os.environ['OPENAI_API_KEY']
        
        # Make the API call to GPT-3.5-turbo
        client = openai.OpenAI()

        response = client.chat.completions.create(
            model="gpt-4o-mini",  
            messages=[
                {"role": "user", "content": get_prompt(markdown_text, competitor_names)}
            ]
        )
        
        # Extract and return the text from the response
        return response.choices[0].message.content
    
    except Exception as e:
        # Return an error message if something goes wrong
        return f"Error: {str(e)}"