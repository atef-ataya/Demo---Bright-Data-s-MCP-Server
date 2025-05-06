from dotenv import load_dotenv
import os
import requests
from bs4 import BeautifulSoup
from openai import OpenAI

load_dotenv()
api_token = os.getenv("API_TOKEN")
zone = os.getenv("WEB_UNLOCKER_ZONE", "mcp_unlocker") 
browser_auth = os.getenv("BROWSER_AUTH")

openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI()

def scrape_page_with_mcp(url):
    """Scrape the target page via Bright Data MCP."""
    print("🔎 Scraping target URL via MCP...")

    payload = {
        "zone": zone,
        "url": url,
        "format": "raw"
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_token}"
    }

    try:
        response = requests.post("https://api.brightdata.com/request", json=payload, headers=headers)
        response.raise_for_status()
        print("✅ Scrape complete. Sending to OpenAI for summarization...")
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"❌ Scrape failed: {e}")
        return None

def clean_html_to_text(html_content):
    """Convert raw HTML content to clean plain text."""
    soup = BeautifulSoup(html_content, "html.parser")
    text = soup.get_text(separator="\n")
    return text.strip()

def summarize_with_openai(text):
    """Send plain text to OpenAI GPT-4o for summarization."""
    messages = [
        {"role": "system", "content": "You're a helpful assistant that summarizes news articles or web page content."},
        {"role": "user", "content": f"Summarize the main points of the following content:\n\n{text}"}
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.4,
        max_tokens=800
    )

    return response.choices[0].message.content

if __name__ == "__main__":
    target_url = "https://news.google.com/search?q=artificial%20intelligence&hl=en-US&gl=US&ceid=US%3Aen"

    html_content = scrape_page_with_mcp(target_url)
    if html_content:
        cleaned_text = clean_html_to_text(html_content)
        print("\n📝 Cleaned page content (first 1000 characters):\n")
        print(cleaned_text[:1000])

        print("\n🟢 Summary of the scraped page:\n")
        summary = summarize_with_openai(cleaned_text)
        print(summary)
