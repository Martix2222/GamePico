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


class TwentyFortyEight(Menus):
    def __init__(self, LCD: displayClass):

        self.theme = Theme2048()
        super().__init__(LCD, self.theme)

        self.grid_size = 4 # set the size of the grid, 4 will create a 4*4 grid, 5 would create a 5*5 grid

        self.grid = self.init_grid()
        self.current_grid_offsets = self.reset_grid_offsets()
        self.target_grid_offsets = self.reset_grid_offsets()

        self.score = 0

        self.reached2048 = False

    
    def start(self):
        self.game_loop()


    def game_loop(self):
        LCD = self.LCD
        theme = self.theme

        self.add_new_tile()
        noInput = False

        while True:
            noInput = True
            while noInput:
                time.sleep_ms(50)
                if LCD.WasPressed.up(clearQueue=True):
                    self.advance_game("up")
                    noInput = False
                if LCD.WasPressed.left(clearQueue=True):
                    self.advance_game("left")
                    noInput = False
                if LCD.WasPressed.down(clearQueue=True):
                    self.advance_game("down")
                    noInput = False
                if LCD.WasPressed.right(clearQueue=True):
                    self.advance_game("right")
                    noInput = False
                self.show_frame()

            # End the game if there are no more moves that can be made
            if not self.is_still_playable():
                time.sleep(1)
                self.game_over_screen(theme.rich_game_over_title, theme.game_over_title_color, [120, 80], "You scored\n" + str(self.score) + " points!", theme.game_over_secondary_color)
                break
                
            # Show a special screen if the player reaches 2048
            if not self.reached2048 and self.detect_2048():
                self.reached2048 = True

                secondaryText ="You reached 2048\nwith the score of\n" + str(self.score) + " points!"
                tertiaryText = "You can continue playing\nuntil you fill up the grid!"

                self.game_over_screen(theme.rich_you_win_title, theme.game_over_title_color, [120, 60], secondaryText, theme.game_over_secondary_color, tertiaryText)
                time.sleep(3)
                noInput = False

            self.LCD.WasPressed.clear_queue()
    

    def show_frame(self):
        LCD = self.LCD
        theme = self.theme
        
        LCD.fill(theme.background_color)

        self.draw_grid((LCD.width-self.calculate_grid_dimensions()[0])//2,
        LCD.height-self.calculate_grid_dimensions()[1]-10)

        self.draw_score()
        LCD.show()

    
    def add_new_tile(self) -> bool:
        if random.randrange(10) == 0:
            value = 4
        else:
            value = 2

        emptyTileCount =  self.empty_tile_count()
        
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


    def empty_tile_count(self) -> int:
        emptyTileCount = 0
        for gridY in range(self.grid_size):
            for gridX in range(self.grid_size):
                if self.grid[gridY][gridX] == 0:
                    emptyTileCount += 1
        
        return emptyTileCount


    def advance_game(self, direction:str):
        """ 
        Advances game by the next move if it is possible.
        Arguments:
            direction (str): The acceptable values are "up", "down", "left" or "right".
        """
        self.animate_advancement(direction)
        noChange = self.move_tiles(direction)
        noChange = min(noChange, self.add_tiles_together(direction))
        noChange = min(noChange, self.move_tiles(direction))
        # The no change bool indicates whether the gid was changed in any way after the operations.
        # If not then noChange is True and the game does not advance until the player makes a move that changes the grid
        if not noChange:
            self.add_new_tile()


    def animate_advancement(self, direction:str):
        theme = self.theme
        
        self.calculate_target_offsets(direction)

        if direction == "up" or direction == "down":
            vertical = True
        else:
            vertical = False

        # Perform the animation
        while self.target_grid_offsets != self.current_grid_offsets:
            for gridY in range(self.grid_size):
                for gridX in range(self.grid_size):
                    if self.current_grid_offsets[gridY][gridX][int(vertical)] == self.target_grid_offsets[gridY][gridX][int(vertical)]:
                        continue
                    elif abs(self.current_grid_offsets[gridY][gridX][int(vertical)] - self.target_grid_offsets[gridY][gridX][int(vertical)]) < theme.animation_denominator:
                        change = 1
                    else:
                        change = abs(self.current_grid_offsets[gridY][gridX][int(vertical)] - self.target_grid_offsets[gridY][gridX][int(vertical)])//theme.animation_denominator + 1
                     
                    if direction == "up" or direction == "left":
                        self.current_grid_offsets[gridY][gridX][int(vertical)] -= change
                    else:
                        self.current_grid_offsets[gridY][gridX][int(vertical)] += change
            
            self.show_frame()

        self.current_grid_offsets = self.reset_grid_offsets()
        self.target_grid_offsets = self.reset_grid_offsets()


    def calculate_target_offsets(self, direction:str):
        """ Calculates target offsets that should be achieved during the animation. """
        theme = self.theme

        if direction == "right":
            start, stop, step = self.grid_size-1, -1, -1
            vertical = False
            xLookahead, yLookahead = -1, 0
        elif direction == "left":
            start, stop, step = 0, self.grid_size, 1
            vertical = False
            xLookahead, yLookahead = 1, 0
        elif direction == "up":
            start, stop, step = 0, self.grid_size, 1
            vertical = True
            xLookahead, yLookahead = 0, -1
        elif direction == "down":
            start, stop, step = self.grid_size-1, -1, -1
            vertical = True
            xLookahead, yLookahead = 0, 1
        else: ValueError("direction (str): The acceptable values are \"up\", \"down\", \"left\" or \"right\".")

        
        for A in range(self.grid_size):
            currentOffset = 0
            lastNumber = 0
            for B in range(start, stop, step):
                # If vertical is false, then the grid will be evaluated line by line, else it will be evaluated column by column    
                if not vertical:
                    gridY, gridX = A, B
                else:
                    gridY, gridX = B, A
                
                change = 0
                
                if self.grid[gridY][gridX] == 0:
                    change += theme.grid_spacing_size + theme.tile_size
                elif self.grid[gridY][gridX] == lastNumber:
                    change += theme.grid_spacing_size + theme.tile_size
                

                if direction == "up" or direction == "left":
                    currentOffset -= change
                else:
                    currentOffset += change

                if self.grid[gridY][gridX] != 0:
                    if lastNumber != self.grid[gridY][gridX]:
                        lastNumber = self.grid[gridY][gridX]
                    else:
                        lastNumber = 0
                    self.target_grid_offsets[gridY][gridX][int(vertical)] = currentOffset


    def add_tiles_together(self, direction:str) -> bool:
        """ 
        Based on the *direction* argument checks in each row and column whether there are two tiles
        next to each other that should be added together in that given direction.
        Arguments:
            direction (str): The acceptable values are "up", "down", "left" or "right".
        """
        noChange = True

        if direction == "right":
            start, stop, step = self.grid_size-1, 0, -1
            vertical = False
            xLookahead, yLookahead = -1, 0
        elif direction == "left":
            start, stop, step = 0, self.grid_size-1, 1
            vertical = False
            xLookahead, yLookahead = 1, 0
        elif direction == "up":
            start, stop, step = 1, self.grid_size, 1
            vertical = True
            xLookahead, yLookahead = 0, -1
        elif direction == "down":
            start, stop, step = self.grid_size-2, -1, -1
            vertical = True
            xLookahead, yLookahead = 0, 1
        else: ValueError("direction (str): The acceptable values are \"up\", \"down\", \"left\" or \"right\".")

        
        for A in range(self.grid_size):
                skipNext = False
                for B in range(start, stop, step):
                    if skipNext:
                        skipNext = False
                        continue

                    # If vertical is false, then the grid will be evaluated line by line, else it will be evaluated column by column    
                    if not vertical:
                        gridY, gridX = A, B
                    else:
                        gridY, gridX = B, A
                    
                    if self.grid[gridY][gridX] == self.grid[gridY+yLookahead][gridX+xLookahead] and self.grid[gridY][gridX] > 0:
                        self.grid[gridY+yLookahead][gridX] += self.grid[gridY][gridX+xLookahead]
                        self.grid[gridY][gridX+xLookahead] = 0

                        self.score += self.grid[gridY+yLookahead][gridX]
                        skipNext = True
                        noChange = False
        
        return noChange


    def move_tiles(self, direction:str) -> bool:
        """ 
        Moves all tiles in all rows or columns in the given direction until they can't move further.
        Arguments:
            direction (str): The acceptable values are "up", "down", "left" or "right".
        """
        noChange = True

        if direction == "right":
            start, stop, step = self.grid_size-1, -1, -1
            vertical = False
            xMultiplier, yMultiplier = 1, 0
        elif direction == "left":
            start, stop, step = 0, self.grid_size, 1
            vertical = False
            xMultiplier, yMultiplier = -1, 0
        elif direction == "up":
            start, stop, step = 0, self.grid_size, 1
            vertical = True
            xMultiplier, yMultiplier = 0, -1
        elif direction == "down":
            start, stop, step = self.grid_size-1, -1, -1
            vertical = True
            xMultiplier, yMultiplier = 0, 1
        else: ValueError("direction (str): The acceptable values are \"up\", \"down\", \"left\" or \"right\".")

        for A in range(self.grid_size):
            freeTilesPassed = 0
            for B in range(start, stop, step):
                # If vertical is false, then the grid will be evaluated line by line, else it will be evaluated column by column    
                if not vertical:
                    gridY, gridX = A, B
                else:
                    gridY, gridX = B, A
                
                if self.grid[gridY][gridX] > 0 and freeTilesPassed > 0:
                    self.grid[gridY+freeTilesPassed*yMultiplier][gridX+freeTilesPassed*xMultiplier] = self.grid[gridY][gridX]
                    self.grid[gridY][gridX] = 0
                    noChange = False
                elif self.grid[gridY][gridX] == 0:
                    freeTilesPassed += 1

        return noChange


    def init_grid(self):
        """ Creates a two dimensional list that represents the grid of the game. """
        grid = []
        for y in range(self.grid_size):
            line = []
            for x in range(self.grid_size):
                line.append(0)
            grid.append(line)

        return grid
    

    def reset_grid_offsets(self):
        """ Creates a two dimensional list that on each coordinate represents the x and y offset of each tile from the grid."""
        grid_offsets = []
        for y in range(self.grid_size):
            line = []
            for x in range(self.grid_size):
                line.append([0, 0])
            grid_offsets.append(line)

        return grid_offsets

    
    def draw_grid(self, x, y):
        theme = self.theme

        self.rounded_rect(x, y, theme.grid_spacing_size+(theme.grid_spacing_size+theme.tile_size)*len(self.grid[0]),
                          theme.grid_spacing_size+(theme.grid_spacing_size+theme.tile_size)*self.grid_size,
                          theme.round_radius, theme.grid_color)
        
        # Draw an empty grid as background
        for gridY in range(self.grid_size):
            for gridX in range(self.grid_size):
                self.draw_tile(x+theme.grid_spacing_size+(theme.tile_size+theme.grid_spacing_size)*gridX, 
                               y+theme.grid_spacing_size+(theme.tile_size+theme.grid_spacing_size)*gridY,
                               0)

        for gridY in range(self.grid_size):
            for gridX in range(self.grid_size):
                if self.grid[gridY][gridX] != 0:
                    self.draw_tile(x+theme.grid_spacing_size+(theme.tile_size+theme.grid_spacing_size)*gridX+self.current_grid_offsets[gridY][gridX][0], 
                                   y+theme.grid_spacing_size+(theme.tile_size+theme.grid_spacing_size)*gridY+self.current_grid_offsets[gridY][gridX][1],
                                   self.grid[gridY][gridX])
                
    
    def calculate_grid_dimensions(self) -> list[int]:
        """
        Calculates the total dimensions of the entire grid.
        Returns:
            list[int]: The list of the dimensions in the form of [width, height]
        """
        theme = self.theme
        return [theme.grid_spacing_size+(theme.grid_spacing_size+theme.tile_size)*len(self.grid[0]),
                theme.grid_spacing_size+(theme.grid_spacing_size+theme.tile_size)*self.grid_size]
    

    def list_deep_copy(self, object):
        """ Returns a deep copy of a list. """
        if isinstance(object, list):
            return [self.list_deep_copy(item) for item in object]

        return object


    def is_still_playable(self) -> bool:
        if self.empty_tile_count() != 0:
            return True

        originalGrid = self.list_deep_copy(self.grid)
        playable = False
        for direction in ["up", "down", "left", "right"]:
            # Test whether a move is possible
            if not self.add_tiles_together(direction):
                playable = True

                # Return the grid to it's original position, because calling
                # the self.add_tiles_together function has changed it.
                self.grid = self.list_deep_copy(originalGrid)

                return playable            

        return playable


    def detect_2048(self) -> bool:
        """ Returns True, if there  is any 2048 value in the grid. """
        for gridY in range(self.grid_size):
            if 2048 in self.grid[gridY]:
                return True
        return False


    def draw_score(self):
        x = 120
        y = 8

        theme = self.theme

        text = f"Score = {self.score}"
        textDimensions = self.calculate_text_dimensions(text, 0)
        self.rounded_rect(x-textDimensions[0]//2-theme.horizontal_reserve, y-textDimensions[1]-theme.vertical_reserve, 
                          textDimensions[0]+theme.horizontal_reserve*2, textDimensions[1]+theme.vertical_reserve*2, 
                          theme.vertical_reserve, theme.secondary_color)
        
        self.center_text(text, x, y, theme.secondary_text_color, theme.secondary_color)

    
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



if __name__ == "__main__":
    twentyFortyEight = TwentyFortyEight(displayClass())
    twentyFortyEight.start()