# Standard Python library imports
from typing import Dict, List, Optional, Any

# Internal library methods imports
from api.krdict.api_krdict import retrieve_krdict_data
from scraping.scraping_naver_dict import scrape_naver_dict

async def lookup_entry(korean_word: str, language: Optional[str] = None) -> Optional[List[Dict[str, Any]]]:
    """
    Searches Naver for a Korean word or phrase's Hanja, English definition, and
    an example sentence

    Args:
        korean_word (string): The Korean word to search for

    Returns:
        document: A list containing dictionaries containing the scraped data.
            Returns None if the word is not found or an error occurs.
    """
    # Initialize list to hold data aggregated across sources
    document = []

    # Set language to English if none provided
    if language is None:
        language = "english"

    # Aggregate data from sources
    krdict_document = await retrieve_krdict_data(korean_word, language)
    naver_dict_document = await scrape_naver_dict(korean_word)

    # Apend to list "document"
    if krdict_document:
        document += krdict_document
    if naver_dict_document:
        document += naver_dict_document
    
    return document
