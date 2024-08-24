from typing import TypedDict, Optional


class ImageInfo(TypedDict):
    image: Optional[str]
    image_width: Optional[int]
    image_height: Optional[int]
    image_alt: Optional[str]
    location: Optional[str]
