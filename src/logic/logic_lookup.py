# Standard Python library imports
from typing import Dict, List, Optional, Any

# Internal library methods imports
from scraping.scraping_naver_dict import scrape_naver_dict

async def lookup_entry(korean_word: str) -> Optional[List[Dict[str, Any]]]:
    """
    Searches Naver for a Korean word or phrase's Hanja, English definition, and
    an example sentence

    Args:
        korean_word (string): The Korean word to search for

    Returns:
        document: A list containing dictionaries containing the scraped data.
            Returns None if the word is not found or an error occurs.
    """
    document = await scrape_naver_dict(korean_word)

    return document
