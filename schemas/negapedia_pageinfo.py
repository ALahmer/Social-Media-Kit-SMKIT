from typing import TypedDict, List, Optional, Dict
from .imageinfo import ImageInfo


class NegapediaPageInfo(TypedDict):
    title: Optional[str]
    description: Optional[str]
    message: Optional[str]
    compact_message: Optional[str]
    historical_conflict: List[ImageInfo]  # Images representing historical conflict
    historical_polemic: List[ImageInfo]  # Images representing historical polemic
    historical_conflict_comparison: Optional[List[ImageInfo]]  # Images representing historical conflict levels comparison
    historical_polemic_comparison: Optional[List[ImageInfo]]  # Images representing historical polemic levels comparison
    recent_conflict_levels: Optional[str]  # String containing recent conflict levels
    recent_polemic_levels: Optional[str]  # String containing recent polemic levels
    mean_conflict_level: Optional[str]  # String containing mean conflict level
    mean_polemic_level: Optional[str]  # String containing mean polemic level
    words_that_matter: List[str]  # List of important words extracted
    conflict_awards: Dict[str, List[str]]  # Dictionary with categories as keys and lists of awards as values
    polemic_awards: Dict[str, List[str]]  # Dictionary with categories as keys and lists of awards as values
    social_jumps: List[Dict[str, str]]  # List of social jumps with titles and links
