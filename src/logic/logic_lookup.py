import pandas as pd
from scraping.scraping_naver import scrape_naver_dict

def lookup_entry(korean_word):
    # 
    word_entry = scrape_naver_dict(korean_word)
    return word_entry
"""
Searches Naver for a Korean word or phrase's Hanja, English definition, and
an example sentence

Args:
    korean_word (string): The Korean word to search for

Returns:
    word_entry: A dictionary containing the scraped data.
          Returns None if the word is not found or an error occurs.
"""