import asyncio

# Python standard library imports
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

# Import methods from other pages
from scraping.scraping_dynamic import render_dynamic_page

async def scrape_page(korean_word: str, region: str, range: str):
    '''Scrapes a Naver dictionary page and returns the html as a
    BeautifulSoup object for further processing.
    
    Args:
        region (str): The region code for Naver dictionary (e.g. 'ko' for korean, 'en' for english, 'hanja' for hanja).
        range (str): The search range (e.g., 'word', 'meanings', 'examples').
        korean_word (str): The Korean word to search for.

    Returns:
        soup: A BeautifulSoup object containing the parsed HTML of the page.
              Returns None if an error occurs during the request.
    '''

    # Sets the range parameter, if none is provided, it will be an empty string
    if range:
        range = f"range={range}"
    else:
        range = ""

    # Set the url for Naver's dictionary search. The region, range, and query parameters needs to be URL-encoded.
    url = f"https://{region}.dict.naver.com/#/search?{range}&query={quote(korean_word)}"

    # Set a User-Agent header to mimic a web browser. This can help prevent
    # being blocked by the website.
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        # Send an HTTP GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)

        # Await dynamic page rendering
        html_content = await render_dynamic_page(url)

        # Parse the HTML content of the page
        soup = BeautifulSoup(html_content, 'html.parser')

        # Return the parsed soup object for further processing
        return soup

    # Print out error messages for debugging
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def scrape_naver_dict(korean_word: str):
    soup_ko_word = asyncio.run(scrape_page(korean_word, "ko", "word"))
    soup_ko_idioms = asyncio.run(scrape_page(korean_word, "ko", "idioms"))
    soup_ko_meanings = asyncio.run(scrape_page(korean_word, "ko", "meanings"))
    soup_ko_examples = asyncio.run(scrape_page(korean_word, "ko", "examples"))
    soup_ko_spelling = asyncio.run(scrape_page(korean_word, "ko", "spelling"))

# Test the test scrape function
entries = asyncio.run(scrape_page("거목", "ko", "word"))
