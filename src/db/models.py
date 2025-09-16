from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import datetime

@dataclass
class ScrapeData:
    """
    A data class to represent scraped data from a webpage
    """

    # Core data information, required for every entry
    source_url: str = ""
    source_name: str = "" # e.g., "Naver Dictionary", "Korena API"

    # List of entries to store for each page scraped
    entries: List[Dict] = field(default_factory=list)

    # Timestamps for tracking when the data was added or last updated
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)

@dataclass
class KoreanWord:
    """
    A data class to represent a single Korean word entry, designed for data
    collected from multiple web and API sources.
    """
    # Core word information, required for every entry
    word: str

    # Optional word data, added to class as they are aquired
    hanja: Optional[str]
    korean_definition: Optional[str]
    ko_example_sentence: Optional[str]
    english_definition: Optional[str]
    en_example_sentence: Optional[str]

    # Stores data from both API's and scraped webpages
    word_data: Optional[List[Any]] = field(default_factory=list)
    
    # Timestamps for tracking when the data was added or last updated
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    updated_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)