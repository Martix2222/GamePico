from drivers.display_driver import LCD_1inch3 as displayClass
# The display driver must contain a color() function to convert 24-bit
# color space to the color space supported by the display.

from themes import Default_theme

color = displayClass.color

class Theme2048(Default_theme):
    def __init__(self) -> None:
        """
        The specific color theme for the 2048 game.
        """
        super().__init__()
        self.tile_size = 40
        self.spacer_size = 5
        self.round_radius = 5

        self.grid_color = color(165, 147, 128)
        self.empty_tile_color = color(189, 176, 160)

        # Tile RGB888 color tuples according to the number inside the tile:
        # Assume that the number inside the tile is n, then the color of the tile will be:
        # self.tile_colors[log2(n)], and if the n is greater than pow(2, len(self.tile_colors)-1) then the color of the tile will be:
        # self.tile_colors[0]
        self.tile_colors = [(0, 0, 0), (238, 228, 218), (237, 224, 200), (242, 177, 121),
                            (245, 149, 99), (246, 124, 96), (246, 94, 59),
                            (237, 207, 115), (237, 204, 98), (237, 200, 80),
                            (237, 197, 63), (237, 194, 45)]
        
        self.dark_text_color = color(119, 110, 101)
        self.light_text_color = 0xFFFF

        # If the luminance of the color of the tile is lower than this value
        # the text will have light_text_color otherwise it will have dark_text_color
        self.dark_text_luminance_threshold = 220

        self.number_font = 0
        self.number_font_size = 1 # only works with certain fonts

        self.animation_speed = 2

        self.rich_you_win_title = """ __   __ ___   _   _    
 \\ \\ / // _ \\ | | | |   
  \\ V /| (_) || |_| |   
   |_|  \\___/  \\___/    
__      __ ___  _  _  _ 
\\ \\    / /|_ _|| \\| || |
 \\ \\/\\/ /  | | | .` ||_|
  \\_/\\_/  |___||_|\\_|(_)"""
        