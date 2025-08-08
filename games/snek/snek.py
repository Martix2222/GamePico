import time
import random

from drivers.display_driver import LCD_1inch3 as displayClass
# The display driver must contain a color() function to convert 24-bit
# color space to the color space supported by the display.

from render_tools import Toolset
from themes import Default_theme as themeClass

color = displayClass.color

richGameOverTitle = """
   ___    _    __  __  ___ 
  / __|  /_\\  |  \\/  || __|
 | (_ | / _ \\ | |\\/| || _| 
  \\___|/_/ \\_\\|_|  |_||___|
   ___ __   __ ___  ___  _ 
  / _ \\\\ \\ / /| __|| _ \\| |
 | (_) |\\ V / | _| |   /|_|
  \\___/  \\_/  |___||_|_\\(_)
                           
"""


class Snek(Toolset):
    def __init__(self, LCD:displayClass, theme:themeClass):
        self.LCD = LCD
        super().__init__(LCD, theme)

        self.score = 0
        self.blockSize = 12
        self.additionalHeadSize = 2
        self.eyeSize = 5
        self.eyeEdgeDistance = 2
        self.minSnakeLen = 2

    
    def move_snake(self):
        theme = self.theme
        LCD = self.LCD

        # Add a new block to the beginning of the snake list to move it forward
        if self.heading == "north":
            self.snake.insert(0, [self.snake[0][0], self.snake[0][1] - self.blockSize])
        elif self.heading == "south":
            self.snake.insert(0, [self.snake[0][0], self.snake[0][1] + self.blockSize])
        elif self.heading == "west":
            self.snake.insert(0, [self.snake[0][0] - self.blockSize, self.snake[0][1]])
        elif self.heading == "east":
            self.snake.insert(0, [self.snake[0][0] + self.blockSize, self.snake[0][1]])

        # Remove the last block of the snake to finish the moving animation
        if len(self.snake) > self.score+self.minSnakeLen:
            lastBlock = self.snake.pop()
            # LCD.fill_rect(lastBlock[0], lastBlock[1], self.blockSize, self.blockSize, theme.background_color)
    

    def draw_snake_head(self, snakeColor:int, eyeColor:int):
        # theme = self.theme
        LCD = self.LCD

        # LCD.fill_rect(self.snake[1][0]-self.additionalHeadSize, self.snake[1][1]-self.additionalHeadSize, self.blockSize + self.additionalHeadSize*2, self.blockSize + self.additionalHeadSize*2, theme.background_color)
        LCD.fill_rect(self.snake[0][0]-self.additionalHeadSize, self.snake[0][1]-self.additionalHeadSize, self.blockSize + self.additionalHeadSize*2, self.blockSize + self.additionalHeadSize*2, snakeColor)

        if self.heading == "south":
            LCD.fill_rect(self.snake[0][0]-self.additionalHeadSize+self.eyeEdgeDistance, self.snake[0][1]+self.additionalHeadSize+self.blockSize-self.eyeSize-self.eyeEdgeDistance, self.eyeSize, self.eyeSize, eyeColor)
            LCD.fill_rect(self.snake[0][0]+self.additionalHeadSize+self.blockSize-self.eyeSize-self.eyeEdgeDistance, self.snake[0][1]+self.additionalHeadSize+self.blockSize-self.eyeSize-self.eyeEdgeDistance, self.eyeSize, self.eyeSize, eyeColor)
        elif self.heading == "north":
            LCD.fill_rect(self.snake[0][0]-self.additionalHeadSize+self.eyeEdgeDistance, self.snake[0][1]-self.additionalHeadSize+self.eyeEdgeDistance, self.eyeSize, self.eyeSize, eyeColor)
            LCD.fill_rect(self.snake[0][0]+self.additionalHeadSize+self.blockSize-self.eyeSize-self.eyeEdgeDistance, self.snake[0][1]-self.additionalHeadSize+self.eyeEdgeDistance, self.eyeSize, self.eyeSize, eyeColor)
        elif self.heading == "west":
            LCD.fill_rect(self.snake[0][0]-self.additionalHeadSize+self.eyeEdgeDistance, self.snake[0][1]-self.additionalHeadSize+self.eyeEdgeDistance, self.eyeSize, self.eyeSize, eyeColor)
            LCD.fill_rect(self.snake[0][0]-self.additionalHeadSize+self.eyeEdgeDistance, self.snake[0][1]+self.additionalHeadSize+self.blockSize-self.eyeSize-self.eyeEdgeDistance, self.eyeSize, self.eyeSize, eyeColor)
        elif self.heading == "east":
            LCD.fill_rect(self.snake[0][0]+self.additionalHeadSize+self.blockSize-self.eyeSize-self.eyeEdgeDistance, self.snake[0][1]-self.additionalHeadSize+self.eyeEdgeDistance, self.eyeSize, self.eyeSize, eyeColor)
            LCD.fill_rect(self.snake[0][0]+self.additionalHeadSize+self.blockSize-self.eyeSize-self.eyeEdgeDistance, self.snake[0][1]+self.additionalHeadSize+self.blockSize-self.eyeSize-self.eyeEdgeDistance, self.eyeSize, self.eyeSize, eyeColor)


    def draw_update_apple(self, appleColor:int):
        """ 
        Checks whether the snake collected the apple and if so it updates the apples' position. It also draws the apple on the display.
        Arguments:
            appleColor (int): The color of the apple.
        """
        LCD = self.LCD
        appleSize = self.blockSize

        if self.appleCoords == self.snake[0]:
            self.score += 1
            while self.appleCoords in self.snake:
                self.appleCoords = [random.randint(1, int((240 - 240%self.blockSize)/self.blockSize))*self.blockSize - self.blockSize, random.randint(1, int((240 - 240%self.blockSize)/self.blockSize))*self.blockSize - self.blockSize]
                # self.center_x_text("score: " + str(self.score), 120, 1, 0x0000, theme.background_color, 1, 2)
        else:
            LCD.ellipse(self.appleCoords[0] + int((self.blockSize - self.blockSize%2)/2), self.appleCoords[1] + int((self.blockSize - self.blockSize%2)/2), int((appleSize - appleSize%2)/2), int((appleSize - appleSize%2)/2), appleColor, True)



    def game_loop(self, updateInterval_ms:int=250, snakeColor:int=color(240,0,0), stripeColor:int=color(0,0,0), eyeColor:int=color(0,0,0), appleColor:int=color(50, 250, 0)):
        theme = self.theme
        LCD = self.LCD
        self.score = 0


        self.heading = "south"
        
        self.snake = [[120 - 120%self.blockSize,0]]

        self.appleCoords = [120, 120]
        
        lastUpdate = time.time_ns()

        while(True):
            # Limit the update rate (and thus set the difficulty [TODO]):
            time.sleep_ms(max(int(updateInterval_ms - ((time.time_ns()-lastUpdate))/1000000), 1))
            lastUpdate = time.time_ns()

            LCD.fill(theme.background_color)

            # Check for button presses and update the current heading accordingly
            if(LCD.WasPressed.up(clearQueue=True) and not (self.heading == "south" or self.heading == "north")):
                self.heading = 'north'

            elif(LCD.WasPressed.down(clearQueue=True) and not (self.heading == "north" or self.heading == "south")):
                self.heading = 'south'

            elif(LCD.WasPressed.left(clearQueue=True) and not (self.heading == "east" or self.heading == "west")):
                self.heading = 'west'

            elif(LCD.WasPressed.right(clearQueue=True) and not (self.heading == "west" or self.heading == "east")):
                self.heading = 'east'

            self.move_snake()
            
            # Draw the entire snake (back to front, such that the head is always on top)
            for i in range(len(self.snake)-1, -1, -1):
                if i == 0:
                    self.draw_snake_head(snakeColor, eyeColor)
                else:
                    LCD.fill_rect(self.snake[i][0], self.snake[i][1], self.blockSize, self.blockSize, snakeColor)
                    LCD.line(self.snake[i][0], self.snake[i][1], self.snake[i][0]+self.blockSize-1, self.snake[i][1]+self.blockSize-1, stripeColor)
                    LCD.line(self.snake[i][0]+self.blockSize-1, self.snake[i][1], self.snake[i][0], self.snake[i][1]+self.blockSize-1, stripeColor)
            

            self.draw_update_apple(appleColor)

            # Draw the score
            self.center_x_text("score: " + str(self.score), 120, 1, 0x0000, -1, 1, 2)

            if LCD.width <= self.snake[0][0] or self.snake[0][0] < 0 or LCD.height <= self.snake[0][1] or self.snake[0][1] < 0 or self.snake[0] in self.snake[3:]:
                self.game_over_screen()
                return 1

            # Update the screen and if recording is enabled duplicate the screenshots such that
            # when the recording is exported the frame timing should be more or less right.
            LCD.show(forceMinimumDuplicates=updateInterval_ms//LCD.frameTime_ms-1)


    def game_over_screen(self, title=richGameOverTitle, titleColor=color(255,0,0), scoreColor=color(255,170,0),
                        introCircleColor=color(255,0,0), backgroundColor=color(255,255,255), introCircleThickness=10):
        for i in range(1, 170 + introCircleThickness, int(introCircleThickness/2)):
            self.LCD.ellipse(120, 120, i, i, introCircleColor, True)
            if i > 10:
                self.LCD.ellipse(120, 120, i - introCircleThickness, i - introCircleThickness, backgroundColor, True)
            if i > 110:
                self.center_text(title, 115, 120, titleColor)
            self.LCD.show()
        
        self.LCD.fill(backgroundColor)
        # The font looks off center a little, so I put 115 instead of 120 as the x coordinate
        self.center_text(title, 115, 90, titleColor)
        self.center_text("You scored " + str(self.score) + " points!", 120, 140, scoreColor, font=1, size=2)

        self.LCD.show()
        time.sleep(5)
        self.LCD.show()
        return