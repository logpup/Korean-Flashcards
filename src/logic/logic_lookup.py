# Standard Python library imports
import asyncio

# Internal library methods imports
from scraping.scraping_naver_dict import scrape_naver_dict

def lookup_entry(korean_word):
    """
    Searches Naver for a Korean word or phrase's Hanja, English definition, and
    an example sentence

    Args:
        korean_word (string): The Korean word to search for

    Returns:
        document: A list containing dictionaries containing the scraped data.
            Returns None if the word is not found or an error occurs.
    """
    document = asyncio.run(scrape_naver_dict(korean_word))

    return document
