import os
import httpx
import asyncio
from lxml import etree
import pprint

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

async def retrieve_word_data(api_key: str, word: str):
    """
    Asynchronously searches for a Korean word using the official API endpoint.
    
    Args:
        word (str): The Korean word to search for.
    
    Returns:
        str: The raw XML dictionary entry data, or None if an error occurs.
    """
    try:        
        # httpx.AsyncClient is the asynchronous equivalent of requests
        async with httpx.AsyncClient() as client:
            response = await client.get(
                API_URL,
                params={
                    "key": api_key,
                    "q": word,
                    "translated": "y",
                    "trans_lang": 1
                    },
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

def print_word_info_with_translations(xml_data):
    """
    Parses the XML data and prints definitions, pronunciations, examples, and English translations.
    
    Args:
        xml_data (str): The raw XML text data from the API response.
    """
    if not xml_data:
        print("No data to display.")
        return
    
    try:
        # Parse the XML string into an ElementTree object
        root = etree.fromstring(xml_data.encode('utf-8'))
        
        # Find all 'item' elements, which represent a single word entry
        word_entries = root.xpath(".//item")
        
        if not word_entries:
            print("No word entries found in the API response.")
            return

        for i, entry in enumerate(word_entries):
            print(f"--- Result {i+1} ---")
            
            # Use XPath to find specific elements and extract their text
            word = entry.findtext(".//word_info/word", default="N/A")
            pronunciation = entry.findtext(".//pronunciation_info/pronunciation", default="N/A")
            
            print(f"Word: {word}")
            print(f"Pronunciation: {pronunciation}")
            
            # Find all sense elements which contain definitions and their translations
            senses = entry.xpath(".//sense")
            if senses:
                print("\nDefinitions:")
                for j, sense in enumerate(senses):
                    # Get Korean definition
                    definition_text = sense.findtext(".//definition", default="No definition available.")
                    print(f"  {j+1}. {definition_text}")
                    
                    # Get English translation of definition
                    trans_dfn = sense.findtext(".//trans_dfn", default="")
                    if trans_dfn:
                        print(f"     Translation: {trans_dfn}")
                    
                    # Get examples with translations
                    examples = sense.xpath(".//example")
                    if examples:
                        print(f"     Examples:")
                        for k, example in enumerate(examples):
                            example_text = example.findtext(".", default="")
                            if example_text:
                                print(f"       • {example_text}")
                                
                                # Look for translated example
                                trans_example = example.findtext(".//trans_example", default="")
                                if trans_example:
                                    print(f"         Translation: {trans_example}")
            else:
                print("No definitions found.")
                
            print("-" * 40)

    except etree.XMLSyntaxError as e:
        print(f"Error parsing XML: {e}")
    except Exception as e:
        print(f"An error occurred during data processing: {e}")

def print_word_info(xml_data):
    """
    Original function - kept for compatibility.
    Parses the XML data and prints only the definitions, pronunciations, and examples.
    
    Args:
        xml_data (str): The raw XML text data from the API response.
    """
    if not xml_data:
        print("No data to display.")
        return
    
    try:
        # Parse the XML string into an ElementTree object
        root = etree.fromstring(xml_data.encode('utf-8'))
        
        # Find all 'item' elements, which represent a single word entry
        word_entries = root.xpath(".//item")
        
        if not word_entries:
            print("No word entries found in the API response.")
            return

        for i, entry in enumerate(word_entries):
            print(f"--- Result {i+1} ---")
            
            # Use XPath to find specific elements and extract their text
            word = entry.findtext(".//word_info/word", default="N/A")
            pronunciation = entry.findtext(".//pronunciation_info/pronunciation", default="N/A")
            
            print(f"Word: {word}")
            print(f"Pronunciation: {pronunciation}")
            
            # Find all 'definition' elements
            definitions = entry.xpath(".//definition")
            if definitions:
                print("\nDefinitions:")
                for j, definition_element in enumerate(definitions):
                    definition_text = definition_element.findtext(".//sense/definition", default="No definition available.")
                    print(f"  {j+1}. {definition_text}")
            else:
                print("No definitions found.")
            
            # Find all 'example' elements
            examples = entry.xpath(".//example")
            if examples:
                print("\nExample Sentences:")
                for k, example_element in enumerate(examples):
                    example_text = example_element.findtext(".//sense/example", default="No example available.")
                    print(f"  {k+1}. {example_text}")
            else:
                print("No examples found.")
                
            print("-" * 20)

    except etree.XMLSyntaxError as e:
        print(f"Error parsing XML: {e}")
    except Exception as e:
        print(f"An error occurred during data processing: {e}")

async def main():
    """
    The main asynchronous function to run the word search.
    """
    search_word = "나무"  # Meaning: tree or wood
    print(f"Searching for the word: '{search_word}'...")
    
    api_key = get_api_key()
    xml_data = await retrieve_word_data(api_key, search_word)

    pprint.pprint(xml_data)
    
    if xml_data:
        # Using the new function to show parsed results with translations
        print("=== Results with Translations ===")
        print_word_info_with_translations(xml_data)

        # Optionally, show the complete dictionary structure
        print("\n--- Complete Dictionary Data ---")
        word_dict = parse_xml_to_dict(xml_data)
        if word_dict:
            import json
            print(json.dumps(word_dict, indent=2, ensure_ascii=False))
    

if __name__ == "__main__":
    # Example usage
    # This runs the main async function.
    asyncio.run(main())

    # To run this script, you must set your API key as an environment variable
    # KRDICT_KEY="your-api-key-here