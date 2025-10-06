import os
import httpx
import asyncio
from lxml import etree
import json
import pprint
from typing import Dict, Optional, List, Any
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

async def retrieve_api_data(api_key: str, word: str, part: str, trans_lang: Optional[str]) -> str | None:
    """
        Asynchronously searches for a Korean word using the official API endpoint.

        Args:
            api_key: The API key for the Korean Basic Dictionary.
            word: The Korean word to search for.
            part:The search part (e.g., 'word', 'exam').
            trans_lang (optional): The target translation language (e.g., 'english', 'japanese').
        
        Returns:
            response: The raw XML dictionary entry data.
    """
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
    
    # Set translation codes if value provided, if not refrain from appending translation parameters to the API call
    translated = ""
    trans_lang_code = ""
    
    if trans_lang:
        translation_params = {
            "translated": "y",
            "trans_lang": trans_lang_codes[trans_lang]
        }
        parameters.update(translation_params) 

    # Initialize response (or the return value) outside the try block
    response = None 

    try:        
        # httpx.AsyncClient is the asynchronous equivalent of requests
        async with httpx.AsyncClient() as client:
            response_tag = await client.get(
                API_URL,
                params=parameters,
                follow_redirects=True
            )
            # Raise an exception for bad status codes (4xx or 5xx)
            response_tag.raise_for_status()
            
            # The API returns XML, so we return the raw text to be parsed later.
            response = response_tag.text
            return response
    except ValueError as e:
        print(f"API Key Error: {e}")
        return response
    except httpx.HTTPStatusError as e:
        print(f"HTTP Error: {e.response.status_code} - {e.response.text}")
        return response
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return response

def _xml_to_dict_recursive(element) -> Dict | str:
    """
        A helper function to recursively convert an XML Element to a Python dictionary.
        Fixed version to handle recursion issues properly.

        Args:
            element (lxml,etree.Element): The current XML element to process.
        
        Returns:
            d: A dictionary or string representing the element's content.
    """
    # Get all child elements
    children = list(element)
    
    # If no children, return the text content directly
    if not children:
        text = element.text.strip() if element.text else ""
        return text if text else ""
    
    # If there are children, process them
    d = {}
    
    # Add text content if it exists and is not just whitespace
    if element.text and element.text.strip():
        d['text'] = element.text.strip()
    
    # Process each child element
    for child in children:
        child_result = _xml_to_dict_recursive(child)
        
        # Handle duplicate tag names by converting to list
        if child.tag in d:
            if not isinstance(d[child.tag], list):
                d[child.tag] = [d[child.tag]]
            d[child.tag].append(child_result)
        else:
            d[child.tag] = child_result
    
    return d

def parse_xml_to_dict(xml_data: str) -> Dict:
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

def parse_word_raw_data(word_raw_data: Dict) -> Optional[List[Dict[str, Any]]]:
    """
        Parses the raw dictionary data (parsed from XML) for the 'word' search part.
        It extracts key information like word, origin, part of speech, definitions, and translations.

        Args:
            word_raw_data: A dictionary containing the raw parsed XML data.
        
        Returns:
            word_data: A list of dictionaries, where each dictionary represents a distinct word entry.
    """
    # 1. Get the content of the single root tag (i.e. "channel")
    root_content = list(word_raw_data.values())[0]
    
    # 2. Check if the 'item' key exists inside the root content
    word_items = []  # Initialize list to hold "items"

    if "item" in root_content:
        item_tag_content = root_content["item"]
        if isinstance(item_tag_content, dict):
            word_items = [item_tag_content]  # Wrap single dictionary in a list
        elif isinstance(item_tag_content, list):
            word_items = item_tag_content
        else:
            print("\n'item' tag content is in an unexpected format.")
            return None
        
        word_data = []  # Initialize list to hold dictionary entries for each "item"
        
        # 3. Iterate through list and parse out valuable data
        for item_tag in word_items:
            item_data = {}  # Initialize dictionary to hold "item" data
            
            # word (i.e specified word)
            if "word" in item_tag:
                word_tag = item_tag["word"]
                word_text = word_tag if isinstance(word_tag, str) else word_tag.get("text", "")
                item_data["word"] = word_text
                
            # origin (i.e. hanja, root word)
            if "origin" in item_tag:
                origin_tag = item_tag["origin"]
                origin_text = origin_tag if isinstance(origin_tag, str) else origin_tag.get("text", "")
                item_data["origin"] = origin_text
                
            # word_grade (i.e. the difficulty of the specified vocabulary)
            if "word_grade" in item_tag:
                word_grade_tag = item_tag["word_grade"]
                word_grade_text = word_grade_tag if isinstance(word_grade_tag, str) else word_grade_tag.get("text", "")
                item_data["word_grade"] = word_grade_text

            # pos (i.e. the part of speech)
            if "pos" in item_tag:
                pos_tag = item_tag["pos"]
                pos_text = pos_tag if isinstance(pos_tag, str) else pos_tag.get("text", "")
                item_data["pos"] = pos_text
                
            # link (i.e. url to Korean Basic Dictionary page for specified word)
            if "link" in item_tag:
                link_tag = item_tag["link"]
                link_text = link_tag if isinstance(link_tag, str) else link_tag.get("text", "")
                item_data["link"] = link_text
                
            # sense (i.e. container for Korean definition and translated definition and idioms of the specified word)
            if "sense" in item_tag:
                sense_tag = item_tag["sense"]  # sense container holding Korean definition and translated entries  
                
                # ko_definition (i.e Korean definition)
                if "definition" in sense_tag:
                    ko_definition_tag = sense_tag["definition"]
                    ko_definition_text = ko_definition_tag if isinstance(ko_definition_tag, str) else ko_definition_tag.get("text", "")
                    item_data["ko_definition"] = ko_definition_text
                    
                # translation (i.e container for translate definition and idioms)
                if "translation" in sense_tag:
                    translation_tag = sense_tag["translation"]  # translation container holding translation data
                    
                    trans_lang_en_abbreviations = {  # trans_lang string to English abbreviations
                        "전체": "all",
                        "영어": "en",
                        "일본어": "jp",
                        "프랑스어": "fr",
                        "스페인어": "es",
                        "아랍어": "ar",
                        "몽골어": "mn",
                        "베트남어": "vn",
                        "타이어": "th",
                        "인도네시아어": "id",
                        "러시아어": "ru",
                        "중국어": "cn",
                    }
                    
                    # Initialize translated_abbr to a default value
                    translated_abbr = "en"  # default to English
                    
                    # translated_abbr (i.e. English abbreviation of chosen translate language)
                    if "trans_lang" in translation_tag:
                        trans_lang_tag = translation_tag["trans_lang"]
                        trans_lang_text = trans_lang_tag if isinstance(trans_lang_tag, str) else trans_lang_tag.get("text", "")
                        translated_abbr = trans_lang_en_abbreviations.get(trans_lang_text, "en")
                        
                    # translated_word (i.e. equivalent idiom in translated language)
                    if "trans_word" in translation_tag:
                        trans_word_tag = translation_tag["trans_word"]
                        trans_word_text = trans_word_tag if isinstance(trans_word_tag, str) else trans_word_tag.get("text", "")
                        item_data[f"{translated_abbr}_word"] = trans_word_text
                        
                    # translated_dfn (i.e translated definition)
                    if "trans_dfn" in translation_tag:
                        trans_dfn_tag = translation_tag["trans_dfn"]
                        trans_dfn_text = trans_dfn_tag if isinstance(trans_dfn_tag, str) else trans_dfn_tag.get("text", "")
                        item_data[f"{translated_abbr}_dfn"] = trans_dfn_text
                        
            word_data.append(item_data)  # Append to word_data list
        return word_data
    
    else:
        print("\n'item' key not found in the response, check if search returned any results.")
        return None

def parse_exam_raw_data(exam_raw_data: Dict) -> Optional[List[Dict[str, Any]]]:
    """
        Parses the raw example data (parsed from XML) for the 'exam' search part.
        It extracts the example sentence, the associated word, and a link to the word's page.

        Args:
            exam_raw_data: A dictionary containing the raw parsed XML data.

        Returns:
            exam_data: A list of dictionaries, where each dictionary represents a distinct example entry.
    """
    # 1. Get the content of the single root tag (i.e. "channel")
    root_content = list(exam_raw_data.values())[0]
    
    # 2. Check if the 'item' key exists inside the root content
    exam_items = [] # Initialize list to hold "items"

    if "item" in root_content:
        item_tag_content = root_content["item"]
        if isinstance(item_tag_content, dict):
            exam_items = [item_tag_content] # Wrap single dictionary in a list
        elif isinstance(item_tag_content, list):
            exam_items = item_tag_content
        else:
            print("\n'item' tag content is in an unexpected format.")
            return None 

        exam_data = [] # Initialize list to hold dictionary entries for each "item"
        # 3. Iterate through list and parse out valuable data
        for item_tag in exam_items:
            item_data = {} # Initialize dictionary to hold "item" data
            # word (p.s. this word may differ from one searched for in the initial API call)
            if "word" in item_tag:
                word_tag = item_tag["word"]
                # If it's a string, use the string itself; otherwise, try to get the 'text' key.
                word_text = word_tag if isinstance(word_tag, str) else word_tag.get("text", "")
                item_data["word"] = word_text
            # example
            if "example" in item_tag:
                example_tag = item_tag["example"]
                example_text = example_tag if isinstance(example_tag, str) else example_tag.get("text", "")
                item_data["example"] = example_text
            # link (i.e url to Korean Basic Dictionary page for associate word in the sentence)
            if "link" in item_tag:
                link_tag = item_tag["link"]
                link_text = link_tag if isinstance(link_tag, str) else link_tag.get("text", "")
                item_data["link"] = link_text
            exam_data.append(item_data) # Append to exam_data list
        return exam_data
    
    else:
        print("\n'item' key not found in the response, check if search returned any results.")
        return None

async def retrieve_krdict_data(korean_word: str, language: Optional[str]) -> Optional[List[Dict[str, Any]]]:
    '''
        Searches Naver Dictionary pages for specified Korean word and returns data scraped from pages
        as a list of dictionary data.

        Args:
            korean_word: Korean word intended to search for

        Returns:
            krdict_data: A list of dictionaries that contain data retrieved from each Korean Basic Dictionary search.
    '''
    api_key = get_api_key() # Retrieve API Key

    # Make the API Call to the Korean Basic Dictionary
    krdict_word_xml_data = await retrieve_api_data(api_key, korean_word, "word", language)
    krdict_exam_xml_data = await retrieve_api_data(api_key, korean_word, "exam", language)

    krdict_data = []

    # Parse XML Data and return as a Python Dictionary
    if krdict_word_xml_data:
        krdict_word_raw_data = parse_xml_to_dict(krdict_word_xml_data)
        krdict_word_page_data = parse_word_raw_data(krdict_word_raw_data)

        # Append to return list "krdict_data"
        if krdict_word_page_data:
            krdict_data.append(KrdictAPIData(
                source_url = "https://krdict.korean.go.kr",
                source_name = "Korean Basic Dictionary",
                param_part = "word",
                param_trans_lang = language,
                page_data = krdict_word_page_data
            ))

    # Parse XML Data and return as a Python Dictionary
    if krdict_exam_xml_data:
        krdict_exam_raw_data = parse_xml_to_dict(krdict_exam_xml_data)
        krdict_exam_page_data = parse_exam_raw_data(krdict_exam_raw_data)

        # Append to return list "krdict_data"
        if krdict_exam_page_data:
            krdict_data.append(KrdictAPIData(
                source_url = "https://krdict.korean.go.kr",
                source_name = "Korean Basic Dictionary",
                param_part = "exam",
                param_trans_lang = language,
                page_data = krdict_exam_page_data
            ))

    if krdict_data:
        return krdict_data
    else:
        return []

    # Example usage
    # This runs the main async function.
    asyncio.run(main())

    # To run this script, you must set your API key as an environment variable
    # KRDICT_KEY="your-api-key-here