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
        
    
    def start(self):
        self.game_loop()


    def game_loop(self):
        LCD = self.LCD
        theme = self.theme

        self.add_new_tile()
        nothing = False

        while True:
            while nothing:
                time.sleep_ms(50)
                if LCD.WasPressed.up(clearQueue=True):
                    self.advance_game("up")
                    nothing = False
                if LCD.WasPressed.left(clearQueue=True):
                    self.advance_game("left")
                    nothing = False
                if LCD.WasPressed.down(clearQueue=True):
                    self.advance_game("down")
                    nothing = False
                if LCD.WasPressed.right(clearQueue=True):
                    self.advance_game("right")
                    nothing = False
            nothing = True

            self.draw_grid((LCD.width-self.calculate_grid_dimensions()[0])//2,
                       LCD.height-self.calculate_grid_dimensions()[1]-10)
            

            LCD.show(True)
            self.LCD.WasPressed.clear_queue()

    
    def add_new_tile(self) -> bool:
        if random.randrange(10) == 0:
            value = 4
        else:
            value = 2

        emptyTileCount = 0
        for gridY in range(self.grid_size):
            for gridX in range(self.grid_size):
                if self.grid[gridY][gridX] == 0:
                    emptyTileCount += 1
        
        if emptyTileCount == 0:
            return False
        
        tileToCreate = random.randrange(emptyTileCount)

        occupiedTiles = 0
        foundFreeTile = False
        for gridY in range(self.grid_size):
            for gridX in range(self.grid_size):
                if self.grid[gridY][gridX] > 0:
                    occupiedTiles += 1
                if (gridY*self.grid_size + gridX) == tileToCreate+occupiedTiles:
                    self.grid[gridY][gridX] = value
                    foundFreeTile = True
                    break
            if foundFreeTile:
                    break
            

        return True


    def advance_game(self, direction:str):
        """ 
        Advances game by the next move if it is possible.
        Arguments:
            direction (str): The acceptable values are "up", "down", "left" or "right".
        """
        noChange = self.move_tiles(direction)
        noChange = min(noChange, self.add_tiles_together(direction))
        noChange = min(noChange, self.move_tiles(direction))
        # The no change bool indicates whether the gid was changed in any way after the operations.
        # If not then noChange is True and the game does not advance until the player makes a move that changes the grid
        if not noChange:
            self.add_new_tile()


    def add_tiles_together(self, direction:str) -> bool:
        """ 
        Based on the *direction* argument checks in each row and column whether there are two tiles
        next to each other that should be added together in that given direction.
        Arguments:
            direction (str): The acceptable values are "up", "down", "left" or "right".
        """
        noChange = True
        # TODO: Optimize and shorten this:
        if direction == "right":
            for gridY in range(self.grid_size):
                skipNext = False
                for gridX in range(self.grid_size-1):
                    if skipNext:
                        skipNext = False
                        continue
                    
                    if self.grid[gridY][gridX] == self.grid[gridY][gridX+1] and self.grid[gridY][gridX] > 0:
                        self.grid[gridY][gridX+1] += self.grid[gridY][gridX]
                        self.grid[gridY][gridX] = 0
                        skipNext = True
                        noChange = False
        if direction == "left":
            for gridY in range(self.grid_size):
                skipNext = False
                for gridX in range(self.grid_size-1, 0, -1):
                    if skipNext:
                        skipNext = False
                        continue
                    
                    if self.grid[gridY][gridX] == self.grid[gridY][gridX-1] and self.grid[gridY][gridX] > 0:
                        self.grid[gridY][gridX-1] += self.grid[gridY][gridX]
                        self.grid[gridY][gridX] = 0
                        skipNext = True
                        noChange = False
        if direction == "up":
            for gridX in range(self.grid_size):
                skipNext = False
                for gridY in range(1, self.grid_size):
                    if skipNext:
                        skipNext = False
                        continue
                    
                    if self.grid[gridY][gridX] == self.grid[gridY-1][gridX] and self.grid[gridY][gridX] > 0:
                        self.grid[gridY-1][gridX] += self.grid[gridY][gridX]
                        self.grid[gridY][gridX] = 0
                        skipNext = True
                        noChange = False
        if direction == "down":
            for gridX in range(self.grid_size):
                skipNext = False
                for gridY in range(self.grid_size-2, -1, -1):
                    if skipNext:
                        skipNext = False
                        continue

                    if self.grid[gridY][gridX] == self.grid[gridY+1][gridX] and self.grid[gridY][gridX] > 0:
                        self.grid[gridY+1][gridX] += self.grid[gridY][gridX]
                        self.grid[gridY][gridX] = 0
                        skipNext = True
                        noChange = False
        else: ValueError("direction (str): The acceptable values are \"up\", \"down\", \"left\" or \"right\".")

        return noChange


    def move_tiles(self, direction:str) -> bool:
        """ 
        Moves all tiles in all rows or columns in the given direction until they can't move further.
        Arguments:
            direction (str): The acceptable values are "up", "down", "left" or "right".
        """
        noChange = True
        # TODO: Optimize and shorten this:
        if direction == "right":
            for gridY in range(self.grid_size):
                freeTilesPassed = 0
                for gridX in range(self.grid_size-1, -1, -1):
                    if self.grid[gridY][gridX] > 0 and freeTilesPassed > 0:
                        self.grid[gridY][gridX+freeTilesPassed] = self.grid[gridY][gridX]
                        self.grid[gridY][gridX] = 0
                        noChange = False
                    elif self.grid[gridY][gridX] == 0:
                        freeTilesPassed += 1
        elif direction == "left":
            for gridY in range(self.grid_size):
                freeTilesPassed = 0
                for gridX in range(self.grid_size):
                    if self.grid[gridY][gridX] > 0 and freeTilesPassed > 0:
                        self.grid[gridY][gridX-freeTilesPassed] = self.grid[gridY][gridX]
                        self.grid[gridY][gridX] = 0
                        noChange = False
                    elif self.grid[gridY][gridX] == 0:
                        freeTilesPassed += 1
        elif direction == "up":
            for gridX in range(self.grid_size):
                freeTilesPassed = 0
                for gridY in range(self.grid_size):
                    if self.grid[gridY][gridX] > 0 and freeTilesPassed > 0:
                        self.grid[gridY-freeTilesPassed][gridX] = self.grid[gridY][gridX]
                        self.grid[gridY][gridX] = 0
                        noChange = False
                    elif self.grid[gridY][gridX] == 0:
                        freeTilesPassed += 1
        elif direction == "down":
            for gridX in range(self.grid_size):
                freeTilesPassed = 0
                for gridY in range(self.grid_size-1, -1, -1):
                    if self.grid[gridY][gridX] > 0 and freeTilesPassed > 0:
                        self.grid[gridY+freeTilesPassed][gridX] = self.grid[gridY][gridX]
                        self.grid[gridY][gridX] = 0
                        noChange = False
                    elif self.grid[gridY][gridX] == 0:
                        freeTilesPassed += 1
        else: ValueError("direction (str): The acceptable values are \"up\", \"down\", \"left\" or \"right\".")

        return noChange

    
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
                          theme.spacer_size+(theme.spacer_size+theme.tile_size)*self.grid_size,
                          theme.round_radius, theme.grid_color)

        for gridY in range(self.grid_size):
            for gridX in range(self.grid_size):
                self.draw_tile(x+theme.spacer_size+(theme.tile_size+theme.spacer_size)*gridX, 
                               y+theme.spacer_size+(theme.tile_size+theme.spacer_size)*gridY,
                               self.grid[gridY][gridX])
                
    
    def calculate_grid_dimensions(self) -> list[int]:
        """
        Calculates the total dimensions of the entire grid.
        Returns:
            list[int]: The list of the dimensions in the form of [width, height]
        """
        theme = self.theme
        return [theme.spacer_size+(theme.spacer_size+theme.tile_size)*len(self.grid[0]),
                theme.spacer_size+(theme.spacer_size+theme.tile_size)*self.grid_size]

    
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

