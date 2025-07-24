import time
import random
import render_tools

from drivers.display_driver import LCD_1inch3 as displayClass
# The display driver must contain a colour() function to convert 24-bit
# color space to the color space supported by the display.

color = displayClass.color


class Snek():
    def __init__(self, LCD:displayClass):
        self.LCD = LCD
        self.Tools = render_tools.Toolset(LCD)

        self.score = 0
        self.blockSize = 12
        self.headSize = 2
        self.eyeSize = 5
        self.eyeEdgeDistance = 2


    def game_loop(self, updateInterval_ns:int=250000000, backgroundColor=color(255,255,255), snakeColor=color(240,0,0), stripeColor=color(0,0,0)):
        self.LCD.fill(backgroundColor)
        self.score = 0

        heading = "south"
        traveledInHeading = 0
        
        snake = [[120 - 120%self.blockSize,0]]

        appleCoords = [120, 120]
        
        appleSize = self.blockSize
        lastUpdate = time.time_ns()

        while(True):
            time.sleep_ms(max(int((updateInterval_ns - (lastUpdate - time.time_ns()))/1_000_000), 1))
            lastUpdate = time.time_ns()

            if(self.LCD.WasPressed.up(clearQueue=True) and not heading == "south" and not heading == "north"):
                heading = 'north'
                traveledInHeading = 0
            elif(self.LCD.WasPressed.down(clearQueue=True) and not heading == "north" and not heading == "south"):
                heading = 'south'
                traveledInHeading = 0
            elif(self.LCD.WasPressed.left(clearQueue=True) and not heading == "east" and not heading == "west"):
                heading = 'west'
                traveledInHeading = 0
            elif(self.LCD.WasPressed.right(clearQueue=True) and not heading == "west" and not heading == "east"):
                heading = 'east'
                traveledInHeading = 0

            
            if len(snake) < self.score+5:
                if heading == "north":
                    snake.insert(0, [snake[0][0], snake[0][1] - self.blockSize])
                elif heading == "south":
                    snake.insert(0, [snake[0][0], snake[0][1] + self.blockSize])
                elif heading == "west":
                    snake.insert(0, [snake[0][0] - self.blockSize, snake[0][1]])
                elif heading == "east":
                    snake.insert(0, [snake[0][0] + self.blockSize, snake[0][1]])         
            else:
                if heading == "north":
                        snake.insert(0, [snake[0][0], snake[0][1] - self.blockSize])
                elif heading == "south":
                        snake.insert(0, [snake[0][0], snake[0][1] + self.blockSize])
                elif heading == "west":
                        snake.insert(0, [snake[0][0] - self.blockSize, snake[0][1]])
                elif heading == "east":
                        snake.insert(0, [snake[0][0] + self.blockSize, snake[0][1]])
                lastBlock = snake.pop()
                self.LCD.fill_rect(lastBlock[0], lastBlock[1], self.blockSize, self.blockSize, backgroundColor)
            
            
            self.LCD.fill_rect(snake[1][0]-self.headSize, snake[1][1]-self.headSize, self.blockSize + self.headSize*2, self.blockSize + self.headSize*2, backgroundColor)
            self.LCD.fill_rect(snake[0][0]-self.headSize, snake[0][1]-self.headSize, self.blockSize + self.headSize*2, self.blockSize + self.headSize*2, snakeColor)

            if heading == "south":
                self.LCD.fill_rect(snake[0][0]-self.headSize+self.eyeEdgeDistance, snake[0][1]+self.headSize+self.blockSize-self.eyeSize-self.eyeEdgeDistance, self.eyeSize, self.eyeSize, 0x0000)
                self.LCD.fill_rect(snake[0][0]+self.headSize+self.blockSize-self.eyeSize-self.eyeEdgeDistance, snake[0][1]+self.headSize+self.blockSize-self.eyeSize-self.eyeEdgeDistance, self.eyeSize, self.eyeSize, 0x0000)
            elif heading == "north":
                self.LCD.fill_rect(snake[0][0]-self.headSize+self.eyeEdgeDistance, snake[0][1]-self.headSize+self.eyeEdgeDistance, self.eyeSize, self.eyeSize, 0x0000)
                self.LCD.fill_rect(snake[0][0]+self.headSize+self.blockSize-self.eyeSize-self.eyeEdgeDistance, snake[0][1]-self.headSize+self.eyeEdgeDistance, self.eyeSize, self.eyeSize, 0x0000)
            elif heading == "west":
                self.LCD.fill_rect(snake[0][0]-self.headSize+self.eyeEdgeDistance, snake[0][1]-self.headSize+self.eyeEdgeDistance, self.eyeSize, self.eyeSize, 0x0000)
                self.LCD.fill_rect(snake[0][0]-self.headSize+self.eyeEdgeDistance, snake[0][1]+self.headSize+self.blockSize-self.eyeSize-self.eyeEdgeDistance, self.eyeSize, self.eyeSize, 0x0000)
            elif heading == "east":
                self.LCD.fill_rect(snake[0][0]+self.headSize+self.blockSize-self.eyeSize-self.eyeEdgeDistance, snake[0][1]-self.headSize+self.eyeEdgeDistance, self.eyeSize, self.eyeSize, 0x0000)
                self.LCD.fill_rect(snake[0][0]+self.headSize+self.blockSize-self.eyeSize-self.eyeEdgeDistance, snake[0][1]+self.headSize+self.blockSize-self.eyeSize-self.eyeEdgeDistance, self.eyeSize, self.eyeSize, 0x0000)

            if len(snake) > 1:
                self.LCD.fill_rect(snake[1][0], snake[1][1], self.blockSize, self.blockSize, snakeColor)
                self.LCD.line(snake[1][0], snake[1][1], snake[1][0]+self.blockSize-1, snake[1][1]+self.blockSize-1, stripeColor)
                self.LCD.line(snake[1][0]+self.blockSize-1, snake[1][1], snake[1][0], snake[1][1]+self.blockSize-1, stripeColor)

            if len(snake) > 2:
                self.LCD.fill_rect(snake[2][0], snake[2][1], self.blockSize, self.blockSize, snakeColor)
                self.LCD.line(snake[2][0], snake[2][1], snake[2][0]+self.blockSize-1, snake[2][1]+self.blockSize-1, stripeColor)
                self.LCD.line(snake[2][0]+self.blockSize-1, snake[2][1], snake[2][0], snake[2][1]+self.blockSize-1, stripeColor)

            if len(snake) > 3:
                self.LCD.fill_rect(snake[3][0], snake[3][1], self.blockSize, self.blockSize, snakeColor)
                self.LCD.line(snake[3][0], snake[3][1], snake[3][0]+self.blockSize-1, snake[3][1]+self.blockSize-1, stripeColor)
                self.LCD.line(snake[3][0]+self.blockSize-1, snake[3][1], snake[3][0], snake[3][1]+self.blockSize-1, stripeColor)


            self.LCD.ellipse(appleCoords[0] + int((self.blockSize - self.blockSize%2)/2), appleCoords[1] + int((self.blockSize - self.blockSize%2)/2), int((appleSize - appleSize%2)/2), int((appleSize - appleSize%2)/2), color(50, 250, 0), True)

            if appleCoords == snake[0]:
                self.score += 1
                while appleCoords in snake:
                    appleCoords = [random.randint(1, int((240 - 240%self.blockSize)/self.blockSize))*self.blockSize - self.blockSize, random.randint(1, int((240 - 240%self.blockSize)/self.blockSize))*self.blockSize - self.blockSize]
                self.Tools.center_x_text("score: " + str(self.score), 120, 1, 0x0000, backgroundColor, 1, 2)
            self.Tools.center_x_text("score: " + str(self.score), 120, 1, 0x0000, -1, 1, 2)

            if 240 <= snake[0][0] or snake[0][0] < 0 or 240 <= snake[0][1] or snake[0][1] < 0 or snake[0] in snake[1:]:
                self.game_over_screen()
                return 1

            self.LCD.show()
            traveledInHeading += 1


    def game_over_screen(self, title="GAME OVER!", titleColor=color(255,0,0), scoreColor=color(255,170,0),
                        introCircleColor=color(255,0,0), backgroundColor=color(255,255,255), introCircleThickness=10):
        for i in range(1, 170 + introCircleThickness, int(introCircleThickness/2)):
            self.LCD.ellipse(120, 120, i, i, introCircleColor, True)
            if i > 10:
                self.LCD.ellipse(120, 120, i - introCircleThickness, i - introCircleThickness, backgroundColor, True)
            if i > 100:
                self.Tools.center_text(title, 120, 115, titleColor, font=1, size=3)
            self.LCD.show()
        
        self.LCD.fill(backgroundColor)
        self.Tools.center_text(title, 120, 115, titleColor, font=1, size=3)
        self.Tools.center_text("You scored " + str(self.score) + " points!", 120, 140, scoreColor, font=1, size=2)

        self.LCD.show()

        time.sleep(5)
        return