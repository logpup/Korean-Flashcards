import pandas as pd
import krdict
import os

# Set your API key from an environment variable for security
# It is highly recommended to do this instead of hardcoding it.
krdict.set_key(os.getenv("KRDICT_API_KEY"))

# Create a sample DataFrame (replace with your actual DataFrame)
df = pd.DataFrame({'korean_word': ['사과', '학교', '사랑']})

# A function to look up a word
def lookup_word(word):
    try:
        response = krdict.search(query=word)
        if response and response['data']['total'] > 0:
            # Get the first result
            first_entry = response['data']['results'][0]
            
            # Extract the desired information
            hanja = first_entry.get('original_language', [{}])[0].get('original_language')
            definitions = first_entry.get('definitions', [])
            english_definition = definitions[0].get('definition')
            example_sentence = definitions[0].get('example_sentences', [{}])[0].get('sentence')
            
            return pd.Series([hanja, english_definition, example_sentence])
        else:
            return pd.Series([None, None, None])
    except Exception as e:
        print(f"Error looking up {word}: {e}")
        return pd.Series([None, None, None])

# Apply the function to the DataFrame
df[['hanja', 'english_definition', 'example_sentence']] = df['korean_word'].apply(lookup_word)

print(df)