# Python standard library imports
import datetime
import asyncio
import re

# Third-party Python library imports
import httpx
from bs4 import BeautifulSoup
from urllib.parse import quote

# Internal library methods imports
from data_sources.scraping.scraping_utils.scraping_dynamic import render_dynamic_page
from db.models import NaverDictionaryPage

# Initialize a semaphore to limit concurrent requests
# Adjust the value (e.g., 5) to control the number of simultaneous tasks.
REQUEST_SEMAPHORE = asyncio.Semaphore(5)

# Method to set the elector for page.await_for_selector
def _set_selector(region: str, url_range: str):
    """
    Returns the appropriate CSS selector for a given region and URL range.
    Returns None if no matching selector is found.
    """
    selector = None
    if region == "en":
        if url_range == "word":
            selector = "#searchPage_entry"
        elif url_range == "example":
            selector = "#searchPage_example"
        else:
            selector = None
    else:
        # Handle other regions or return None for unsupported case
        selector = None

    print(f"Selector: {selector}")
    return selector

# Asynchronous function to scrape Naver dictionary pages
async def scrape_page(korean_word: str, region: str, url_range: str):
    '''Scrapes a Naver dictionary page and returns the html as a
    BeautifulSoup object for further processing.
    
    Args:
        region (str): The region code for Naver dictionary (e.g. 'ko' for korean, 'en' for english, 'hanja' for hanja).
        url_range (str): The search range (e.g., 'word', 'meanings', 'examples').
        korean_word (str): The Korean word to search for.

    Returns:
        soup: A BeautifulSoup object containing the parsed HTML of the page.
              Returns None if an error occurs during the request.
    '''

    # Sets the range parameter, if none is provided, it will be an empty string
    if url_range:
        range_tag = f"range="
        url_range = f"{url_range}"
    else:
        range_tag = ""
        url_range = ""
    
    # Set the url for Naver's dictionary search. The region, range, and query parameters needs to be URL-encoded.
    url = f"https://{region}.dict.naver.com/#/search?{range_tag}{url_range}&query={quote(korean_word)}"

    # Set a User-Agent header to mimic a web browser. This can help prevent
    # being blocked by the website.
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # Retry parameters
    retries = 5 # The number of retry attempts
    delay = 2 # The initial delay in seconds between retries
    backoff_factor = 2 # Multiples the delay for each subsequent retry

    async with httpx.AsyncClient() as client:
        for attempt in range(retries):
            async with REQUEST_SEMAPHORE:
                try:
                    # Set a timeout for the request to avoid indefinite waiting.
                    # A longer timeout gives the server more time to respond.
                    response = await client.get(url, timeout=10, headers=headers) 

                    # Raise an HTTPError for bad responses (4xx or 5xx)
                    response.raise_for_status() 

                    # Await dynamic page rendering
                    print(f"url_range: {url_range}")
                    selector = _set_selector(region, url_range) # Set page selector to wait to load for

                    if selector:
                        # Await playwright to render javascript elements
                        html_content = await render_dynamic_page(url, selector)

                        # Parse the HTML content of the page
                        soup = BeautifulSoup(html_content, 'html.parser')

                        # Return the parsed soup object for further processing
                        return soup

                # Print out error messages for debugging
                except httpx.RequestError as e:
                    # Handle different types of request errors, including timeouts
                    print(f"Attempt {attempt + 1}/{retries} failed for {url}: {e}")
                    if attempt < retries - 1:
                        print(f"Retrying in {delay} seconds...")
                        await asyncio.sleep(delay)
                        delay *= backoff_factor
                    else:
                        print(f"All {retries} attempts failed. Giving up.")
                        return None
                except Exception as e:
                    print(f"An unexpected error occurred: {e}")
                    return None

def parse_english_word_idiom(soup: BeautifulSoup):
    '''Parses the English dictionary "Word · Idiom" page to extract relevant information.

    Args:
        soup (BeautifulSoup): The BeautifulSoup object containing the parsed HTML of the page.

    Returns:
        entries_data: A list containing the extracted information, where each entry is represented
            as a dictionary.

    '''
    # Isolate the main content area of the dictionary page
    content_tag = soup.find("div", id="searchPage_entry")

    # Return an empty list if the content tag is not found
    if not content_tag:
        return []
    
    # Filter content from content_tag
    content = content_tag.find("div", class_="component_keyword")
    
    # Find all entry rows within the content
    entries_tag = content.find_all("div", class_="row")

    # Initialize variable to store extracted entry data
    entries_data = []

    # Loop through each entry and extract relevant information
    for entry_tag in entries_tag:
        print("\n--- New Entry ---")
        # Extract the Korean word
        origin_tag = entry_tag.find("div", class_="origin")
        korean_word_tag = origin_tag.find("a", attrs={"lang": "ko"})
        if korean_word_tag:
            korean_word = korean_word_tag.text.strip()
        print(f"Korean Word: {korean_word}")
        # Extract the hanja if available
        origin_tag = entry_tag.find("div", class_="origin")
        hanja_tag = origin_tag.find("span", attrs={"lang": "zh_CN"})
        if hanja_tag:
            hanja = hanja_tag.text.strip()
            print(f"Hanja: {hanja if hanja else 'N/A'}")
        # Extract meanings and its possible senses
        senses_tag = entry_tag.find("ul", class_="mean_list")
        sense_tags = senses_tag.find_all("li", class_="mean_item", attrs={"lang": "en"})
        if sense_tags:
            senses = [sense_tag.text.strip() for sense_tag in sense_tags]
            # Remove leading numbering from senses
            if len(sense_tags) > 1:
                pattern = r'^\d+\.\s*'
                senses = [re.sub(pattern, '', sense) for sense in senses]
        for idx, sense in enumerate(senses, start=1):
            print(f"Sense {idx}: {sense}")
        # Extract information source
        source_tag = entry_tag.find(class_="source")
        source = source_tag.text.strip()
        print(f"Source: {source}")

        # Compile extracted data into a dictionary
        entry_data = {
            "korean_word": korean_word,
            "hanja": hanja if hanja_tag else None,
            "senses": senses,
            "source": source,
            "extracted_at": datetime.datetime.now() # Add the current timestamp here
        }
        # Append the entry data to the main data list
        entries_data.append(entry_data)

    return entries_data

def parse_english_examples(soup: BeautifulSoup):

    '''Parses the English dictionary "Examples" page to extract relevant information.

    Args:
        soup (BeautifulSoup): The BeautifulSoup object containing the parsed HTML of the page.

    Returns:
        page_data: A list containing the extracted information, where each example is represented as a dictionary.
    '''
    # Isolate the main content area of the dictionary page
    content_tag = soup.find("div", id="searchPage_example")

    # Return an empty list if the content tag is not found
    if not content_tag:
        return []
    
    content = content_tag.find("div", class_="component_example")

    # Find all example rows within the content
    examples_tag = content.find_all("div", class_="row")

    # Initialize variable to store extracted example data
    page_data = []

    # Loop through each example and extract relevant information
    for example_tag in examples_tag:
        print("\n--- New Example ---")
        # Extract the English sentence
        eng_sentence = None
        origin_tag = example_tag.find(class_="origin")
        eng_sentence_tag = origin_tag.find(attrs={"lang": "en"})
        if eng_sentence_tag:
            eng_sentence = eng_sentence_tag.text.strip()
        print(f"English Sentence: {eng_sentence}")
        # Extract the Korean sentence
        kor_sentence = None
        translate_tag = example_tag.find(class_="translate")
        kor_sentence_tag = translate_tag.find("p", attrs={"lang": "ko"})
        if kor_sentence_tag:
            kor_sentence = kor_sentence_tag.text.strip()
        print(f"Korean Sentence: {kor_sentence}")
        # Extract audio files (if available) ---- DO THIS LATER ----
        # 
        # Extract information source
        source = None
        source_tag = example_tag.find(class_="source")
        if source_tag:
            source = source_tag.text.strip()
            print(f"Source: {source}")
        
        # Compile extracted data into a dictionary
        example_data = {
            "english_sentence": eng_sentence,
            "korean_sentence": kor_sentence,
            "source": source,
            "extracted_at": datetime.datetime.now() # Add the current timestamp here
        }

        # Append the example data to the main data list
        page_data.append(example_data)

    return page_data

async def scrape_naver_dict(korean_word):
    '''
        Searches Naver Dictionary pages for specified Korean word and returns data scraped from pages
        as a list of dictionary data.

        Args:
            korean_word: Korean word intended to search for

        Returns:
            scraped_data: A list of dictionaries that contain data scraped from each Naver page.
    '''
    # Initialize variables to save scraped page data
    page_data = []
    en_word_idiom_page_data = None
    en_example_page_data = None
    
    # Scrape Naver's Korean-English Dictionary's "Word·Idiom" page
    en_word_idiom_soup = await scrape_page(korean_word, "en", "word")
    if en_word_idiom_soup:
        en_word_idiom_page_data = parse_english_word_idiom(en_word_idiom_soup)
        page_data.append(NaverDictionaryPage(
            source_name = "Naver Dictionary",
            source_url = "naver.dict.com",
            source_region = "en",
            source_page = "word_idiom",
            page_data = en_word_idiom_page_data
        ))
    
    # Scrape Naver's Korean-English Dictionary's "Examples" page
    en_example_soup = await scrape_page(korean_word, "en", "example")
    if en_example_soup:
        en_example_page_data = parse_english_examples(en_example_soup)
        page_data.append(NaverDictionaryPage(
            source_name = "Naver Dictionary",
            source_url = "naver.dict.com",
            source_region = "en",
            source_page = "example",
            page_data = en_example_page_data))
    
    # Prepare return data as a list    
    return page_data