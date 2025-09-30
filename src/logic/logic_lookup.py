# Standard Python library imports
from typing import Dict, List, Optional, Any

# Internal library methods imports
from data_sources.api.krdict.api_krdict import retrieve_krdict_data
from data_sources.scraping.naver_dict.scraping_naver_dict import scrape_naver_dict

async def lookup_entry(korean_word: str, language: Optional[str] = None) -> Optional[List[Dict[str, Any]]]:
    """
    Searches Naver for a Korean word or phrase's Hanja, English definition, and
    an example sentence

    Args:
        korean_word (string): The Korean word to search for

    Returns:
        word_data: A list containing dictionaries containing the scraped data.
            Returns None if the word is not found or an error occurs.
    """
    # Initialize list to hold data aggregated across sources
    word_data = []

    # Set language to English if none provided
    if language is None:
        language = "english"

    # Aggregate data from sources
    krdict_word_data = await retrieve_krdict_data(korean_word, language)
    naver_dict_word_data = await scrape_naver_dict(korean_word)

    # Apend to list "document"
    if krdict_word_data:
        word_data += krdict_word_data
    if naver_dict_word_data:
        word_data += naver_dict_word_data
    
    return word_data
