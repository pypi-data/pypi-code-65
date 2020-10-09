colors = {
    "black": (0, 0, 0),
    "light_brown": (250, 133, 50),
    "brown": (207, 98, 21),
    "dark_brown": (130, 61, 12),
    "light_red": (255, 69, 69),
    "red": (255, 0, 0),
    "dark_red": (179, 0, 0),
    "light_orange": (255, 188, 79),
    "orange": (252, 157, 3),
    "dark_orange": (186, 115, 0),
    "light_yellow": (249, 255, 69),
    "yellow": (244, 252, 3),
    "dark_yellow": (153, 158, 0),
    "light_green": (144, 252, 3),
    "green": (0, 255, 0),
    "dark_green": (0, 120, 0),
    "light_blue": (0, 255, 242),
    "blue": (0, 0, 255),
    "dark_blue": (0, 0, 102),
    "purple": (145, 9, 186),
    "pink": (255, 46, 175),
    "beige": (255, 208, 128),
    "golden": (240, 237, 81),
    "emerald": (14, 173, 43),
    "coral": (224, 49, 67),
    "copper": (224, 68, 7),
    "khaki": (49, 158, 19),
    "light_gray": (222, 222, 222),
    "gray": (143, 143, 143),
    "dark_gray": (43, 43, 43),
    "white": (255, 255, 255)
}


def get_colors_names():
    global colors
    return tuple(colors.keys())
