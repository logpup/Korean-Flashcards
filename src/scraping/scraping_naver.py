import asyncio

# Python standard library imports
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

# Import methods from other pages
from scraping.scraping_dynamic import scrape_dynamic_page

async def scrape_naver_korea(korean_word: str):
    # Set the url for Naver's dictionary search. The query parameter needs to be URL-encoded.
    url = f"https://ko.dict.naver.com/#/search?query={quote(korean_word)}"

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
        html_content = await scrape_dynamic_page(url)

        # Parse the HTML content of the page
        soup = BeautifulSoup(html_content, 'html.parser')

        # Initialize list to store the scraped data
        entries = []

        # --- Scraping Protocol ---
        # 1. Scrape the word entry section
        word_content = soup.find(
            'div',
            id='searchPage_entry'
        )
        if word_content:
            rows = word_content.find_all('div', class_='row')
            for row in rows:
                entries.append(row)
            #print(f"Scraped {len(entries)} rows.")
            #print(f"First row content: {entries[0] if entries else 'No entries found'}")  # Print the first row for debugging
            return entries
        else:
            print("No word entries found.")
            return None
        
    # Print out error messages for debugging
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def scrape_naver_hanja(entries):
    # --- Scrape Hanja ---

    # Initialize variables to store the scraped data
    hanjas = []
    hanja_entries = []

    # Initalize counting variable
    count = 0

    # Loop through each entry, isolating the hanja section
    for entry in entries:

        print(f"{count+1}.")
        count += 1

         # Look for a span tag with the class 'mark' and lang attribute set to 'zh_CN'
        hanja_entry = entry.find(
            'span',
            class_='mark',
            attrs={'lang': 'zh_CN'}
        )
        
        # For debugging purposes, print out the entire entry being processed
        # print(f"Processing entry: {hanja_entry}")

        # If a hanja section is found, extract the hanja symbols found within that row
        if hanja_entry:
            hanja = hanja_entry.get_text(strip=True)
        # If no hanja section is found, set to "Not Available"
        else:
            hanja = "Not Available"
        print(f"Extracted Hanja text: {hanja}")
        hanjas.append(hanja)
    
    return hanjas

def scrape_naver_english_idiom(korean_word: str):
     # The base URL for Naver's dictionary search. The query parameter needs to be URL-encoded.
    url = f"https://en.dict.naver.com/#/search?range=word&query={quote(korean_word)}"

    # Set a User-Agent header to mimic a web browser. This can help prevent
    # being blocked by the website.
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        # Send an HTTP GET request to the URL
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)

        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, 'html.parser')

        # --- Scrape English Definition ---
        # English definitions are typically found in a specific tag.
        english_tag = soup.find('div', class_='mean')
        if english_tag:
            english_definition = english_tag.get_text(strip=True)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def scrape_naver_english_definition(korean_word: str):
    # The base URL for Naver's dictionary search. The query parameter needs to be URL-encoded.
    url = f"https://en.dict.naver.com/#/search?range=meaning&query={quote(korean_word)}"

    # Set a User-Agent header to mimic a web browser. This can help prevent
    # being blocked by the website.
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        # Send an HTTP GET request to the URL
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)

        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, 'html.parser')

        # --- Scrape English Definition ---
        # English definitions are typically found in a specific tag.
        english_tag = soup.find('div', class_='mean')
        if english_tag:
            english_definition = english_tag.get_text(strip=True)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None
    
def scrape_naver_example_sentence(korean_word: str):
    # The base URL for Naver's dictionary search. The query parameter needs to be URL-encoded.
    url = f"https://en.dict.naver.com/#/search?range=word&query={quote(korean_word)}"

    # Set a User-Agent header to mimic a web browser. This can help prevent
    # being blocked by the website.
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        # Send an HTTP GET request to the URL
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)

        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, 'html.parser')

        # --- Scrape English Definition ---
        # English definitions are typically found in a specific tag.
        english_tag = soup.find('div', class_='mean')
        if english_tag:
            english_definition = english_tag.get_text(strip=True)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def scrape_naver_dict(korean_word: str):
    """
    Scrapes the Naver dictionary for a given Korean word and returns
    its Hanja, English definition, and an example sentence.

    Args:
        korean_word (str): The Korean word to search for.

    Returns:
        dict: A dictionary containing the scraped data.
              Returns None if the word is not found or an error occurs.
    """

    hanja = scrape_naver_hanja(korean_word)
    english_definition = scrape_naver_english_definition(korean_word)
    example_sentence = scrape_naver_example_sentence(korean_word)

    return {
        "korean_word": korean_word,
        "hanja": hanja if hanja else "Not Available",
        "english_definition": english_definition if english_definition else "Not Available",
        "example_sentence": example_sentence if example_sentence else "Not Available"
    }
    
# Run the test scrape function
entries = asyncio.run(scrape_naver_korea("거목"))
scrape_naver_hanja(entries)
