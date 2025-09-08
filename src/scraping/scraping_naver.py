import requests
from bs4 import BeautifulSoup
from urllib.parse import quote

def scrape_naver_dict(korean_word: str):
    """
    Scrapes the Naver dictionary for a given Korean word and returns
    its Hanja, English definition, and an example sentence.

    Args:
        korean_word (str): The Korean word to search for.

    Returns:
        dict: A dictionary containing the scraped data.
              Returns None if the word is not found or an error occurs.
    """
    # The base URL for Naver's dictionary search. The query parameter needs to be URL-encoded.
    url = f"https://ko.dict.naver.com/#/search?query={quote(korean_word)}"

    # Set a User-Agent header to mimic a web browser. This can help prevent
    # being blocked by the website.
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        # Send an HTTP GET request to the URL
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)

        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, 'html.parser')

        # Initialize variables to store the scraped data
        hanja = ""
        english_definition = ""
        example_sentence = ""

        # --- Scrape Hanja ---
        # Hanja is typically found in an <sup> tag with a specific class.
        hanja_tag = soup.find('a', class_='link_hanja')
        if hanja_tag:
            hanja = hanja_tag.get_text(strip=True)

        # --- Scrape English Definition ---
        # English definitions are often within the first <li> of a list, with a specific class.
        # This selector targets the first list item containing an English translation.
        # Adjusting the selector for more robust searching.
        definition_tag = soup.select_one('.lst_mean .mean_li .c_l:nth-of-type(1)')
        if definition_tag:
            english_definition = definition_tag.get_text(strip=True).replace('1. ', '')
            
        # If the direct selector fails, try a broader approach.
        if not english_definition:
            definition_tag_alt = soup.find('p', class_='mean_view')
            if definition_tag_alt:
                english_definition = definition_tag_alt.get_text(strip=True).replace('1. ', '')

        # --- Scrape Example Sentence ---
        # Example sentences are usually in a specific div with the class 'box_ex'
        # or inside a ul with the class 'lst_word_exp'.
        example_tag = soup.select_one('.lst_word_exp .box_ex .sent:nth-of-type(1)')
        if example_tag:
            # Clean up the text, removing any sub-tags like English translation
            # We use `string` to get the text of the first part, before any other tags.
            example_sentence = example_tag.get_text(strip=True)
            # Find the English part and remove it to get a clean Korean sentence
            english_part = example_tag.find('span', class_='e_sent')
            if english_part:
                example_sentence = example_sentence.replace(english_part.get_text(strip=True), '').strip()


        # Return the collected data in a dictionary
        return {
            "korean_word": korean_word,
            "hanja": hanja if hanja else "Not available",
            "english_definition": english_definition if english_definition else "Not available",
            "example_sentence": example_sentence if example_sentence else "Not available"
        }

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

if __name__ == '__main__':
    # Test with a few words
    words_to_scrape = ["사랑", "감사", "학교", "컴퓨터"]

    for word in words_to_scrape:
        print(f"Scraping data for '{word}'...")
        data = scrape_naver_dict(word)
        if data:
            print("-" * 20)
            print(f"Korean Word: {data['korean_word']}")
            print(f"Hanja: {data['hanja']}")
            print(f"English Definition: {data['english_definition']}")
            print(f"Example Sentence: {data['example_sentence']}")
            print("-" * 20)
        else:
            print(f"Could not retrieve data for '{word}'.")
        print("\n")