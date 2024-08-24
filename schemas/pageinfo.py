from typing import TypedDict, List, Optional
from .imageinfo import ImageInfo


class PageInfo(TypedDict):
    title: Optional[str]
    description: Optional[str]
    message: Optional[str]
    images: List[ImageInfo]
    audio: Optional[str]
    video: Optional[str]
    urls: List[Optional[str]]
    updated_time: Optional[str]
    article_published_time: Optional[str]
    article_modified_time: Optional[str]
    article_tag: Optional[str]
    keywords: Optional[str]
