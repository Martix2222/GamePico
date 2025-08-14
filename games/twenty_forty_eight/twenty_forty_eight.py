import time
import random
from math import pow, log2
from collections import OrderedDict

from drivers.display_driver import LCD_1inch3 as displayClass
# The display driver must contain a color() function to convert 24-bit
# color space to the color space supported by the display.

from menus import Menus
from themes import Default_theme as themeClass
from games.twenty_forty_eight.theme import Theme2048

color = displayClass.color

""" ↑↓→← """


class TwentyFortyEight(Menus):
    def __init__(self, LCD: displayClass):

        self.theme = Theme2048()
        super().__init__(LCD, self.theme)

        self.grid_size = 4 # set the size of the grid, 4 will create a 4*4 grid, 5 would create a 5*5 grid

        self.grid = self.init_grid()
        
        self.draw_grid(20, 20)

    
    def init_grid(self):
        """ Creates a two dimensional list that represents the grid of the game. """
        theme = self.theme

        grid = []
        for y in range(self.grid_size):
            line = []
            for x in range(self.grid_size):
                line.append(0)
            grid.append(line)

        return grid

    
    def draw_grid(self, x, y):
        theme = self.theme

        self.rounded_rect(x, y, theme.spacer_size+(theme.spacer_size+theme.tile_size)*len(self.grid[0]),
                          theme.spacer_size+(theme.spacer_size+theme.tile_size)*len(self.grid),
                          theme.round_radius, theme.grid_color)

        for gridY in range(len(self.grid)):
            for gridX in range(len(self.grid[gridY])):
                self.draw_tile(x+theme.spacer_size+(theme.tile_size+theme.spacer_size)*gridX, 
                               y+theme.spacer_size+(theme.tile_size+theme.spacer_size)*gridY,
                               self.grid[gridY][gridX])
                
    
    def calculate_grid_dimensions(self):
        """
        Calculates the total dimensions of the entire grid.
        Returns:
            list[int]: The list of the dimensions in the form of [width, height]
        """
        theme = self.theme
        return [theme.spacer_size+(theme.spacer_size+theme.tile_size)*len(self.grid[0]),
                theme.spacer_size+(theme.spacer_size+theme.tile_size)*len(self.grid)]

    
    def draw_tile(self, x, y, value):
        LCD = self.LCD
        theme = self.theme
        
        if value == 0:
            # Draw an empty tile:
            self.rounded_rect(x, y, theme.tile_size, theme.tile_size, theme.round_radius, theme.empty_tile_color)
            return


        if len(theme.tile_colors) > int(log2(value)):
            tileColor = theme.tile_colors[int(log2(value))]
        else:
            tileColor = theme.tile_colors[0]
        
        # I intentionally kept the tileColor in the tuple form for this part of the code:
        if LCD.calculate_luminance(*tileColor) > theme.dark_text_luminance_threshold:
            textColor = theme.dark_text_color
        else:
            textColor = theme.dark_text_color

        # Convert the RGB888 tileColor code tuple to RGB565 value
        tileColor = color(*tileColor)

        self.rounded_rect(x, y, theme.tile_size, theme.tile_size, theme.round_radius, tileColor)

        # Draw the number value:
        if self.calculate_text_dimensions(str(value), theme.number_font, theme.number_font_size)[0] <= theme.tile_size:
            # Draw the text as expected
            self.center_text(str(value), x+theme.tile_size//2, y+theme.tile_size//2, textColor, font=theme.number_font, size=theme.number_font_size)
        else:
            # Default to the smallest font to try to fit the number into the tile
            self.center_text(str(value), x+theme.tile_size//2, y+theme.tile_size//2, textColor, font=1, size=1)

        

            
        
        