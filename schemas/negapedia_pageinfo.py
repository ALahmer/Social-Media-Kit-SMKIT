from typing import TypedDict, List, Optional, Dict
from .imageinfo import ImageInfo


class NegapediaPageInfo(TypedDict):
    title: Optional[str]
    description: Optional[str]
    message: Optional[str]
    historical_conflict: List[ImageInfo]  # Images representing historical conflict
    historical_polemic: List[ImageInfo]  # Images representing historical polemic
    recent_conflict_levels: List[Dict[str, str]]  # List of dictionaries containing recent conflict levels
    recent_polemic_levels: List[Dict[str, str]]  # List of dictionaries containing recent polemic levels
    words_that_matter: List[str]  # List of important words extracted
    conflict_awards: List[str]  # List of awards related to conflict
    polemic_awards: List[str]  # List of awards related to polemic
    social_jumps: List[Dict[str, str]]  # List of social jumps with titles and links
