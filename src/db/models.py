from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import datetime

@dataclass
class UserEntry:
    """
    A data class to represent manually-entered user data for a Korean word.
    """
    # Core data information
    source_name: str = "User Entry"
    
    # User-entered data
    page_data: Dict = field(default_factory=dict)
    
    # Timestamps for tracking when the data was added or last updated
    created_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    updated_at: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    
    def __post_init__(self):
        """
        Sets the 'updated_at' timestamp to match 'created_at' upon initialization.
        This ensures both timestamps are identical when a new entry is created.
        """
        self.updated_at = self.created_at

@dataclass
class KrdictAPIData:
    """
    A data class to represent data from a Korean Basic Dictionary API call
    """

    # Core data information, required for every entry
    source_url: str
    source_name: str # e.g., "Korean Basic Dictionary"
    param_part: str # e.g., "word", "ip", "dfn", "exam"
    param_trans_lang: Optional[str]

    # Data from the API call
    page_data: Dict = field(default_factory=dict)

    # Timestamps for tracking when the data was added or last updated
    created_at: datetime.datetime = field(default_factory=lambda: datetime.datetime.now(tz=datetime.UTC))
    updated_at: datetime.datetime = field(default_factory=lambda: datetime.datetime.now(tz=datetime.UTC))

    def __post_init__(self):
        """
        Sets the 'updated_at' timestamp to match 'created_at' upon initialization.
        This ensures both timestamps are identical when a new entry is created.
        """
        self.updated_at = self.created_at   

@dataclass
class NaverDictionaryPage:
    """
    A data class to represent scraped data from a Naver Dictionary Page
    """

    # Core data information, required for every entry
    source_url: str
    source_name: str # e.g., "Naver Dictionary"
    source_region: str
    source_page: str

    # List of entries on a given page
    page_data: List[Dict] = field(default_factory=list)

    # Timestamps for tracking when the data was added or last updated
    created_at: datetime.datetime = field(default_factory=lambda: datetime.datetime.now(tz=datetime.UTC))
    updated_at: datetime.datetime = field(default_factory=lambda: datetime.datetime.now(tz=datetime.UTC))

    def __post_init__(self):
        """
        Sets the 'updated_at' timestamp to match 'created_at' upon initialization.
        This ensures both timestamps are identical when a new entry is created.
        """
        self.updated_at = self.created_at

@dataclass
class KoreanWord:
    """
    A data class to represent a single Korean word entry, designed for data
    collected from multiple web and API sources.
    """
    # Core word information, required for every entry
    word: str

    # Optional word data, added to class as they are aquired
    hanja: Optional[str] = None
    ko_definition: Optional[str] = None
    ko_example_sentence: Optional[str] = None
    en_definition: Optional[str] = None
    en_example_sentence: Optional[str] = None

    # Stores data from both API's and scraped webpages
    word_data: List[Any] = field(default_factory=list)
    
    # Timestamps for tracking when the data was added or last updated
    created_at: datetime.datetime = field(default_factory=lambda: datetime.datetime.now(tz=datetime.UTC))
    updated_at: datetime.datetime = field(default_factory=lambda: datetime.datetime.now(tz=datetime.UTC))

    def __post_init__(self):
        """
        Sets the 'updated_at' timestamp to match 'created_at' upon initialization.
        This ensures both timestamps are identical when a new entry is created.
        """
        self.updated_at = self.created_at
