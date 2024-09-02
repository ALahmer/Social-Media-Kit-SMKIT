from typing import Dict


class PlotColorManager:

    COLORS = [
        "#FF6F61",  # Coral Red
        "#6B5B95",  # Royal Purple
        "#88B04B",  # Lime Green
        "#F7CAC9",  # Pale Pink
        "#92A8D1",  # Soft Blue
        "#955251",  # Mauve
        "#B565A7",  # Orchid
        "#009B77",  # Emerald Green
        "#DD4124",  # Fiery Red
        "#45B8AC",  # Turquoise
        "#EFC050",  # Sunset Yellow
        "#5B5EA6",  # Indigo
        "#9B2335",  # Cranberry
        "#BC243C",  # Ruby Red
        "#C3447A",  # Rose Pink
        "#98B4D4",  # Light Steel Blue
        "#C97D60",  # Terra Cotta
        "#FFD662",  # Goldenrod
        "#00A591",  # Teal
        "#4B9CD3",  # Sky Blue
        "#E08119",  # Persimmon
        "#7F4145",  # Maroon
        "#CE5B78",  # Mulberry
        "#00758F",  # Cerulean
        "#D4B9DA",  # Lilac
        "#DEC1A3",  # Peach
        "#6CACE4",  # Azure
        "#D1B6C3",  # Blush
        "#F7786B",  # Coral
        "#E15D44",  # Burnt Orange
        "#7D8B8F",  # Slate
        "#9B6376",  # Antique Rose
        "#2A4B7C",  # Denim Blue
        "#DC4C46",  # Tomato Red
        "#E94B3C",  # Flame Red
        "#DFCFBE",  # Sand
        "#9B1B30",  # Claret
        "#55B4B0",  # Aqua Blue
        "#B55A30",  # Chestnut
        "#9A8B4F",  # Olive
        "#E08119",  # Pumpkin
        "#0B5369",  # Deep Teal
        "#BCB4A4",  # Taupe
        "#D69C2F",  # Mustard
        "#4A772F",  # Forest Green
        "#D94F70",  # Raspberry
        "#CF1020",  # Vivid Red
        "#9E1030",  # Carmine
        "#EFC050",  # Saffron
        "#DD4124",  # Tangerine
        "#6B5B95",  # Purple Iris
        "#4A7C59",  # Moss Green
        "#D2C29D",  # Tan
        "#91A8D0",  # Periwinkle
        "#F6A6B6",  # Pastel Pink
        "#D2386C",  # Fuchsia Rose
        "#78C0A8",  # Mint
        "#F4A7B9",  # Bubblegum Pink
        "#D2691E",  # Cinnamon
        "#5B5EA6",  # Royal Blue
        "#E08119",  # Amber
        "#B3B3B3",  # Platinum
        "#E2725B",  # Clay Red
        "#4B5335",  # Khaki
        "#6A5ACD",  # Slate Blue
        "#8E6B23",  # Bronze
        "#BD3F32",  # Brick Red
        "#FFA07A",  # Salmon
        "#4682B4",  # Steel Blue
        "#DDA0DD",  # Pale Violet Red
        "#8FBC8F",  # Dark Sea Green
        "#66CDAA",  # Medium Aquamarine
        "#B22222",  # Fire Brick
        "#FFD700",  # Gold
        "#708090",  # Slate Gray
        "#778899",  # Light Slate Gray
        "#B0E0E6",  # Powder Blue
        "#AFEEEE",  # Pale Turquoise
        "#7FFF00",  # Chartreuse
        "#40E0D0",  # Turquoise
        "#FF6347",  # Tomato
        "#FF4500",  # Orange Red
        "#2E8B57",  # Sea Green
        "#8A2BE2",  # Blue Violet
        "#A52A2A",  # Brown
        "#9932CC",  # Dark Orchid
        "#DC143C",  # Crimson
        "#FF8C00",  # Dark Orange
        "#FFDAB9",  # Peach Puff
        "#DB7093",  # Pale Violet Red
        "#4B0082",  # Indigo
        "#FF1493",  # Deep Pink
        "#E9967A",  # Dark Salmon
        "#FF69B4",  # Hot Pink
        "#CD5C5C",  # Indian Red
        "#FFA500",  # Orange
        "#7B68EE",  # Medium Slate Blue
        "#BA55D3",  # Medium Orchid
        "#9370DB",  # Medium Purple
        "#DA70D6",  # Orchid
        "#C71585",  # Medium Violet Red
        "#FF00FF",  # Magenta
    ]

    # Class variable to keep track of the assigned colors for topics
    topic_color_map: Dict[str, str] = {}
    _next_color_index: int = 0

    @classmethod
    def get_color_for_topic(cls, topic: str) -> str:
        """
        Get or assign a color for the given topic.

        Args:
            topic (str): The topic for which the color is needed.

        Returns:
            str: The color assigned to the topic.
        """
        # If the topic already has a color, return it
        if topic in cls.topic_color_map:
            return cls.topic_color_map[topic]

        # Otherwise, assign the next available color
        color = cls.COLORS[cls._next_color_index]
        cls.topic_color_map[topic] = color

        # Increment and loop the color index if we exceed the color list length
        cls._next_color_index = (cls._next_color_index + 1) % len(cls.COLORS)
        return color
