import asyncio
import httpx
from typing import Optional, List, Dict
from bs4 import BeautifulSoup, Tag, NavigableString
from urllib.parse import quote
import re
import time # For time.sleep during retries

# Internal library methods imports
from data_sources.scraping.scraping_utils.scraping_dynamic import render_dynamic_page

# Initialize a semaphore to limit concurrent requests
# This controls how many simultaneous HTTP requests can be active at any time.
REQUEST_SEMAPHORE = asyncio.Semaphore(5)

# Helper function that strip content from tags
def _strip_tag_content(soup: BeautifulSoup | Tag) -> BeautifulSoup | Tag:
    '''
    Removes all NavigableString content (text nodes) from a BeautifulSoup object 
    or Tag, leaving only the structural tags and their attributes.

    Args:
        soup (BeautifulSoup | Tag): The parsed HTML object or a specific tag.

    Returns:
        BeautifulSoup | Tag: The modified object with only tags remaining.
    '''
    # We iterate over a copy of the contents to avoid issues with modification during iteration
    for content in list(soup.contents):
        # Check if the content item is a text node (NavigableString)
        if isinstance(content, NavigableString):
            # If it's a string (text), decompose it (remove it from the tree)
            content.decompose()
    return soup

# Helper function that filters out attribute by a regex
def _attribute_regex_filter(pattern_str: str):
    '''
    Creates and returns a custom filter function for BeautifulSoup's find_all().
    The returned function checks if ANY attribute (key or value) of the given tag 
    matches the provided regex pattern string.
    
    Args:
        pattern_str (str): The regex pattern string to match against attributes.

    Returns:
        function: The actual filter function (which takes only a Tag argument).
    '''
    # Compile the pattern once using the provided string
    PATTERN = re.compile(pattern_str, re.IGNORECASE)

    def filter_func(tag: Tag):
        '''
        The actual filter applied by soup.find_all() to each tag.
        This function has access to the PATTERN compiled in the outer function.
        '''
        # 1. Check the attribute keys (the attribute names, e.g., 'class', 'href')
        for attr_key in tag.attrs.keys():
            if PATTERN.search(attr_key):
                # print(f"MATCH (Key): {attr_key} in tag <{tag.name}>") # Uncomment for debugging
                return True

        # 2. Check the attribute values (e.g., the actual class name, link URL, etc.)
        for attr_value in tag.attrs.values():
            # BeautifulSoup often converts multi-valued attributes like 'class' 
            # into a list, so we must handle lists as well as strings.
            
            # If the value is a list (like class=['one', 'two']), iterate through it
            if isinstance(attr_value, list):
                for item in attr_value:
                    if isinstance(item, str) and PATTERN.search(item):
                        # print(f"MATCH (Value List): {item} in tag <{tag.name}>") # Uncomment for debugging
                        return True
            # If the value is a simple string (like id="main-content")
            elif isinstance(attr_value, str) and PATTERN.search(attr_value):
                # print(f"MATCH (Value String): {attr_value} in tag <{tag.name}>") # Uncomment for debugging
                return True
                
        return False
        
    return filter_func

def _tag_attribute_matches(tags: List[Tag], search_string: str) -> List[Dict]:
    '''
    Searches through a list of BeautifulSoup Tags and returns a list of dictionaries 
    containing the attribute name and value whenever the attribute name OR value 
    contains the search string.
    
    Args:
        tags (list[Tag]): A list of BeautifulSoup Tag objects to search.
        search_string (str): The string or regex pattern to match against attributes.

    Returns:
        list[dict]: A list of dictionaries, where each dict is 
                    {'tag_name': str, 'attribute': str, 'value': str}.
    '''
    # Compile the pattern once for efficient searching
    PATTERN = re.compile(search_string, re.IGNORECASE)
    matching_attributes = []
    
    for tag in tags:
        for attr_key, attr_value in tag.attrs.items():
            
            # Convert single values and lists of values into a single list of strings to process
            values_to_check = []
            if isinstance(attr_value, list):
                values_to_check.extend([str(v) for v in attr_value if isinstance(v, (str, int, float))])
            else:
                values_to_check.append(str(attr_value))
            
            # 1. Check if the attribute KEY matches the pattern
            if PATTERN.search(attr_key):
                matching_attributes.append({
                    'tag_name': tag.name,
                    'attribute': attr_key,
                    'value': attr_value if not isinstance(attr_value, list) else ' '.join(attr_value),
                    'match_type': 'Key'
                })
                # Optimization: continue to the next attribute key/value pair in this tag
                continue 
            
            # 2. Check if any of the attribute VALUES matches the pattern
            for value in values_to_check:
                if PATTERN.search(value):
                    matching_attributes.append({
                        'tag_name': tag.name,
                        'attribute': attr_key,
                        'value': value,
                        'match_type': 'Value'
                    })
                    # Found a match in this attribute's values, break and check the next attribute key/value pair
                    break 

    return matching_attributes

# Asynchronous function to scrape Naver general search pages
async def scrape_naver_search_page(query: str, pattern: Optional[str] = None):
    '''
    Scrapes the main Naver search results page for a given query, 
    using httpx and an asyncio semaphore for concurrent requests control.
    
    Args:
        query (str): The search term (e.g., 'BTS' or '네이버').

    Returns:
        content:  The content from the web scrape (BeautifulSoup object or None).
    '''
    
    # 1. URL Construction
    encoded_query = quote(query)
    # The general Naver search URL:
    url = f"https://search.naver.com/search.naver?query={encoded_query}"

    # 2. Request Configuration
    headers = {
        # Using a standard desktop user agent to mimic a regular browser visit.
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # Retry parameters
    retries = 3 
    initial_delay = 2 # Initial delay in seconds
    backoff_factor = 2 
    
    html_content = None

    async with httpx.AsyncClient() as client:
        for attempt in range(retries):
            # Wait for the semaphore before proceeding with the request
            async with REQUEST_SEMAPHORE:
                current_delay = initial_delay * (backoff_factor ** attempt)
                
                if attempt > 0:
                    # Implement exponential backoff delay before retrying
                    print(f"Attempt {attempt + 1}/{retries}: Retrying '{query}' in {current_delay:.1f} seconds...")
                    await asyncio.sleep(current_delay)

                try:
                    # Make the GET request with a timeout
                    response = await client.get(url, timeout=10, headers=headers) 
                    response.raise_for_status() # Raise an HTTPError for 4xx/5xx responses

                    wait_selector = "#main_content"
                    
                    # If a pattern is provided, try to find a more specific selector
                    if pattern:
                        soup = BeautifulSoup(response.text, 'lxml')
                        # Don't strip tag content - we need the structure to search
                        all_tags = soup.find_all(True)  # Find all tags
                        html_tags = _tag_attribute_matches(all_tags, pattern)
                        
                        # Check if we found any matching tags
                        if html_tags:
                            html_tag = html_tags[0]
                            attr_key = html_tag["attribute"]
                            attr_value = html_tag["value"]
                            wait_selector = f"[{attr_key}='{attr_value}']"
                            print(f"Found selector: {wait_selector}")
                        else:
                            print(f"No tags found matching pattern '{pattern}' in initial HTML")
                            print(f"Will search in dynamically rendered content...")
                    
                    html_content = await render_dynamic_page(url, wait_selector)
                    break # Success! Break the retry loop
                    
                except httpx.RequestError as e:
                    # Handle request errors (connection issues, timeouts, etc.)
                    if attempt == retries - 1:
                        print(f"All {retries} attempts failed for '{query}'. Giving up. Error: {e}")
                        return None # Return None on final failure
                except Exception as e:
                    print(f"An unexpected error occurred for '{query}': {e}")
                    return None
    
    # 3. HTML Parsing and Data Extraction
    if not html_content:
        return None

    # Use 'lxml' parser for speed
    soup = BeautifulSoup(html_content, 'lxml')
    
    # Return the entire soup object so we can search for all matching elements
    # The pattern will be used later in parse_ai_briefing()
    return soup

def parse_ai_briefing(content: Optional[BeautifulSoup]):
    '''
    Extracts AI briefing text from the provided content.
    
    Args:
        content: BeautifulSoup object or None
        
    Returns:
        list: List of AI briefing texts, or empty list if none found
    '''
    if content is None:
        return []
    
    filter = _attribute_regex_filter("ai-briefing")
    ai_briefing_tags = content.find_all(filter)
    ai_briefing_texts = []
    for tag in ai_briefing_tags:
        ai_briefing_texts.append(tag.text)
    return ai_briefing_texts

# Example Usage: Demonstrates how to run multiple searches concurrently
async def main():
    print("Starting Naver search scraping example...")
    search_queries = ["월급루팡"]
    
    # Create concurrent tasks for each search query
    tasks = [scrape_naver_search_page(query, "ai-briefing") for query in search_queries]
    
    # Run the tasks concurrently, limited by the REQUEST_SEMAPHORE
    results = await asyncio.gather(*tasks)

    for query, result in zip(search_queries, results):
        print(f"\n==========================================")
        print(f"Search Results for: '{query}'")
        print(f"==========================================")
        if result is None:
            print("No results found or error occurred")
        else:
            briefings = parse_ai_briefing(result)
            if briefings:
                print(f"{briefings}")
            else:
                print("No AI briefings found in the results")

if __name__ == '__main__':
    # This block allows the file to be run directly using `python naver_search_scraper.py`
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program interrupted by user.")