import os
import httpx
import asyncio
from lxml import etree
import pprint
from typing import Dict, Optional, List
from db.models import KrdictAPIData

# The base URL for the Korean Basic Dictionary API search endpoint.
# The `key` and `q` parameters are required for a query.
API_URL = "https://krdict.korean.go.kr/api/search"

def get_api_key():
    """
    Retrieves the API key from an environment variable.
    
    Returns:
        str: The API key.
    
    Raises:
        ValueError: If the KRDICT_KEY environment variable is not set.
    """
    api_key = os.getenv("KRDICT_KEY")
    if not api_key:
        raise ValueError("Please set the 'KRDICT_KEY' environment variable with your API key.")
    return api_key

async def retrieve_word_data(api_key: str, word: str, part: str, trans_lang: Optional[str]):

    # Initialize dictionary to hold parameters for the API Call
    parameters = {
        "key": api_key,
        "q": word,
        "part": part,
    }

    """
    Asynchronously searches for a Korean word using the official API endpoint.
    
    Args:
        word (str): The Korean word to search for.
    
    Returns:
        str: The raw XML dictionary entry data, or None if an error occurs.
    """
    trans_lang_codes = {
        "all": 0,
        "english": 1,
        "japanese": 2,
        "french": 3,
        "spanish": 4,
        "arabic": 5,
        "mongolian": 6,
        "vietnamese": 7,
        "thai": 8,
        "indonesian": 9,
        "russian": 10,
        "chinese": 11
    }
    
    # Set translation codes if value provided, if not refrain from appending to parameters
    translated = ""
    trans_lang_code = ""
    if trans_lang:
        translation_params = {
            "translated": "y",
            "trans_lang": trans_lang_codes[trans_lang]
        }
        parameters.update(translation_params) 

    try:        
        # httpx.AsyncClient is the asynchronous equivalent of requests
        async with httpx.AsyncClient() as client:
            response = await client.get(
                API_URL,
                params=parameters,
                follow_redirects=True
            )
            # Raise an exception for bad status codes (4xx or 5xx)
            response.raise_for_status()
            
            # The API returns XML, so we return the raw text to be parsed later.
            return response.text
    except ValueError as e:
        print(f"API Key Error: {e}")
        return None
    except httpx.HTTPStatusError as e:
        print(f"HTTP Error: {e.response.status_code} - {e.response.text}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def _xml_to_dict_recursive(element):
    """
    A helper function to recursively convert an XML Element to a Python dictionary.
    """
    d = {}
    if element.text and element.text.strip():
        d['text'] = element.text.strip()
    
    for child in element:
        child_dict = _xml_to_dict_recursive(child)
        if child.tag in d:
            if not isinstance(d[child.tag], list):
                d[child.tag] = [d[child.tag]]
            d[child.tag].append(child_dict)
        else:
            d[child.tag] = child_dict
            
    if not d and element.text and element.text.strip():
        return element.text.strip()
    
    return d

def parse_xml_to_dict(xml_data):
    """
    Parses the XML data into a complete Python dictionary.
    
    Args:
        xml_data (str): The raw XML text data from the API response.
        
    Returns:
        dict: A nested dictionary representing the XML data.
    """
    if not xml_data:
        print("No data to parse.")
        return {}
    
    try:
        root = etree.fromstring(xml_data.encode('utf-8'))
        return {root.tag: _xml_to_dict_recursive(root)}
    except etree.XMLSyntaxError as e:
        print(f"Error parsing XML: {e}")
        return {}
    except Exception as e:
        print(f"An error occurred during data processing: {e}")
        return {}

async def retrieve_krdict_data(korean_word: str, language: "str"):
    '''
        Searches Naver Dictionary pages for specified Korean word and returns data scraped from pages
        as a list of dictionary data.

        Args:
            korean_word: Korean word intended to search for

        Returns:
            word_data: A list of dictionaries that contain data retrieved from each Korean Basic Dictionary search.
    '''
    api_key = get_api_key() # Retrieve API Key

    # Make the API Call to the Korean Basic Dictionary
    krdict_word_xml_data = await retrieve_word_data(api_key, korean_word, "word", language)
    krdict_exam_xml_data = await retrieve_word_data(api_key, korean_word, "exam", language)

    word_data = []

    # Parse XML Data and return as a Python Dictionary
    if krdict_word_xml_data:
        krdict_word_page_data = parse_xml_to_dict(krdict_word_xml_data)
        word_data.append(KrdictAPIData(
            source_url = "https://krdict.korean.go.kr",
            source_name = "Korean Basic Dictionary Open API",
            param_part = "word",
            param_trans_lang = language,
            page_data = krdict_word_page_data
        ))
        word_data.append(krdict_word_data) # Append to return list
    else:
        return None
    
    if krdict_exam_xml_data:
        krdict_exam_data = parse_xml_to_dict(krdict_exam_xml_data)
        word_data.append(krdict_exam_data) # Append to return list
    else:
        return None
    
    return word_data

def parse_word_data(word_data: List[Dict]):

    # 
    # 1. Get the content of the single root tag (i.e. "channel")
    root_content = list(word_data.values())[0]
    
    word_items = []
    # 2. Check if the 'item' key exists inside the root content
    if "item" in root_content:
        word_item_tag = root_content["item"]
        word_items = list(word_item_tag)

        # 3. 
        for item in word_items:
            word = item["word"]
            if item["origin"]:
                hanja = item["origin"]
            word_grade = item["word_grade"]
            pos = item["pos"]
            senses_tag = item["sense"]
            definition = None
            translation = None
            for sense in senses_tag:
                ko_definition = sense["definition"]
                translated_definition = sense["translation"]
            {}
    else:
        print("\n'item' key not found in the response, check if search returned any results.")
        return None

async def main():
    """
    The main asynchronous function to run the word search.
    """
    search_word = "완공"  # Meaning: tree or wood
    print(f"Searching for the word: '{search_word}'...")
    
    api_key = get_api_key()
    xml_data = await retrieve_word_data(api_key, search_word)
    
    if xml_data:
        word_data = parse_xml_to_dict(xml_data)
        # 1. Get the content of the single root tag (i.e. "channel")
        root_content = list(word_data.values())[0]
        
        word_items = []
        # 2. Check if the 'item' key exists inside the root content
        if "item" in root_content:
            word_item_tag = root_content["item"]
            word_items = list(word_item_tag)
        else:
            print("\n'item' key not found in the response, check if search returned any results.")

        pprint.pprint(word_items)
    else:
        print("\nCould not parse XML data.")

if __name__ == "__main__":
    # Example usage
    # This runs the main async function.
    asyncio.run(main())

    # To run this script, you must set your API key as an environment variable
    # KRDICT_KEY="your-api-key-here