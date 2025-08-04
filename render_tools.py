import time
import math
import random

from drivers.display_driver import LCD_1inch3 as displayClass
# The display driver must contain a color() function to convert 24-bit
# color space to the color space supported by the display.

from FONTS import FONTS
from themes import Default_theme as themeClass


class Toolset():
    def __init__(self, LCD:displayClass):
        self.LCD = LCD

        self.FONTS = FONTS(LCD)

        try: 
            import drivers.UPS_driver as UPS_driver
            # Create an ADS1115 ADC (16-bit) instance.
            self.UPS = UPS_driver.INA219(addr=0x43)
            self.UPSavailable = True
        except:
            self.UPSavailable = False


    def calculate_text_dimensions(self, string:str, font:int, size:int=0) -> list[int]:
        """ 
        Calculates the dimensions of rendered text based on it's length, font and size.  
        """
        if font == 0:
            return [8*len(string), 8]
        elif font == 1:
            return FONTS.calculate_text_dimensions(string, size)
        else:
            raise ValueError


    def display_text(self, string:str, x:int, y:int, color:int, backgroundColor:int=-1, font:int=0, size:int=0):
        if font != 1:
            if backgroundColor > -1:
                self.LCD.fill_rect(x, y,len(string)*8, 8,backgroundColor)
            self.LCD.text(string, x, y, color)
        else:
            xSize, ySize = self.calculate_text_dimensions(string, font, size)

            if backgroundColor > -1:
                self.LCD.fill_rect(x, y, xSize, ySize, backgroundColor)
            self.FONTS.text(string, x, y, size, color)


    def center_text(self, string:str, x:int, y:int, color:int, backgroundColor:int=-1, font:int=0, size:int=0):
        """
        Centers the *string* on the given *x* and *y* coordinates
        *color* sets the color of the text
        *backgroundColor* sets the background color, if no value is given, the background will be transparent
        """
        width, height = self.calculate_text_dimensions(string, font, size)
        self.display_text(string, x - width//2, y - height//2, color, backgroundColor, font, size)
        

    def center_y_text(self, string:str, x:int, y:int, color:int, backgroundColor:int=-1, font:int=0, size:int=0):
        """
        Centers the *string* on the given *y* coordinate, but not the *x* coordinate
        *color* sets the color of the text
        *backgroundColor* sets the background color, if no value is given, the background will be transparent
        """
        width, height = self.calculate_text_dimensions(string, font, size)
        self.display_text(string, x, y - height//2, color, backgroundColor, font, size)


    def center_x_text(self, string:str, x:int, y:int, color:int, backgroundColor:int=-1, font:int=0, size:int=0):
        """
        Centers the *string* on the given *x* coordinate, but not the *y* coordinate
        *color* sets the color of the text
        *backgroundColor* sets the background color, if no value is given, the background will be transparent
        """
        width, height = self.calculate_text_dimensions(string, font, size)
        self.display_text(string, x - width//2, y, color, backgroundColor, font, size)


    def scene_roll_transition(self, direction:str, color:int, speed:int, pause:float):
        if direction == "down":
            for s in range(0, 240, speed):
                self.LCD.scroll(0,speed)
                self.LCD.fill_rect(0, 0, 240, speed, color)
                self.LCD.show()
                time.sleep(pause)
        elif direction == "up":
            for s in range(0, 240, speed):
                self.LCD.scroll(0,-speed)
                self.LCD.fill_rect(0, 240, 240, speed, color)
                self.LCD.show()
                time.sleep(pause)
        elif direction == "left":
            for s in range(0, 240, speed):
                self.LCD.scroll(-speed,0)
                self.LCD.fill_rect(0, 0, speed, 240, color)
                self.LCD.show()
                time.sleep(pause)
        elif direction == "right":
            for s in range(0, 240, speed):
                self.LCD.scroll(speed,0)
                self.LCD.fill_rect(240, 0, speed, 240, color)
                self.LCD.show()
                time.sleep(pause)
        
        return


    def scene_circle_transition(self, x:int, y:int, circleColor:int, resultColor:int, circleThickness:int=20, step=4):
        for i in range(1,170 + circleThickness + int(math.sqrt((120-x)*(120-x)+(120-y)*(120-y)) + 3), step):
            self.LCD.ellipse(x, y, i, i, circleColor, True)
            if i>circleThickness: self.LCD.ellipse(x, y, i-circleThickness, i-circleThickness, resultColor, True)
            self.LCD.show()
        return


    def draw_battery_statistics(self, x:int, y:int, titleColor:int, borderColor:int, backgroundColor:int, textColor:int):
        width = 130
        height = 60
        borderThickness = 2
        textShift = 3

        if self.UPSavailable:
            bus_voltage = self.UPS.getBusVoltage_V()             # voltage on V- (load side)
            current = self.UPS.getCurrent_mA()                   # current in mA
            P = (bus_voltage - 3.3)/0.9*100
            if(P<0):P=0
            elif(P>100):P=100
        else:
            bus_voltage = 0
            current = 0
            P = 0

        self.LCD.fill_rect(x,y,width,height, borderColor)
        if P>10:
            self.LCD.fill_rect(x + borderThickness, y + 8 + borderThickness*2,
                        width-borderThickness*2, height - 8 - borderThickness*3, backgroundColor)
        else:
            self.LCD.fill_rect(x + borderThickness, y + 8 + borderThickness*2,
                        width-borderThickness*2, height - 8 - borderThickness*3, self.LCD.color(255,0,0))
        
        self.center_x_text("Battery status:", int(x + width/2), y + borderThickness, titleColor)

        self.center_y_text("Voltage: {:1.2f} V".format(bus_voltage), x + borderThickness + textShift, y + borderThickness*2 + 8 + 10, textColor)
        self.center_y_text("Current:{:4.0f} mA".format(current), x + borderThickness + textShift, y + borderThickness*2 + 8 + 20, textColor)
        self.center_y_text("Percent: {:3.1f} %".format(P), x + borderThickness + textShift, y + borderThickness*2 + 8 + 30, textColor)
        self.LCD.fill_rect(x + borderThickness + textShift, y + borderThickness*2 + 8 + 38,
                    width - textShift*2 - borderThickness*2, 4, 0x000)
        self.LCD.fill_rect(x + borderThickness + textShift + 2, y + borderThickness*2 + 8 + 39,
                    int(int(P)/(100/(width - textShift*2 - borderThickness*2-4))), 2, self.LCD.color(0,255,0))


    def update_animated_background(self, backgroundMode:int, backgroundColor:int, secondaryBackgroundColor:int):
        """
        Used to create and update an animated background in a specific style. \n
        Currently supported *backgroundMode* values:\n
        0: crates a mosaic out of fixed-grid squares with the *backgroundColor* and *secondaryBackgroundColor* \n
        1: draws random lines on the screen with the *backgroundColor* and *secondaryBackgroundColor* \n
        2: similar to mode 0, but with circles that are not fixed to a grid \n
        3: Non-functional
        """    

        if not 0 <= backgroundMode <= 2:
            backgroundMode = 0

        redBackgroundComponent = 255
        greenBackgroundComponent = 0
        blueBackgroundComponent = 0
        
        if backgroundMode == 0:
            self.LCD.fill_rect(random.randint(0,24)*10, random.randint(0,24)*10, 10, 10, secondaryBackgroundColor)
            self.LCD.fill_rect(random.randint(0,24)*10, random.randint(0,24)*10, 10, 10, backgroundColor)
        elif backgroundMode == 1:
            self.LCD.line(random.randint(0,240), random.randint(0,240), random.randint(0,240), random.randint(0,240), secondaryBackgroundColor)
            self.LCD.line(random.randint(0,240), random.randint(0,240), random.randint(0,240), random.randint(0,240), backgroundColor)
        elif backgroundMode == 2:
            self.LCD.ellipse(random.randint(0,240), random.randint(0,240), 5, 5, secondaryBackgroundColor, True)
            self.LCD.ellipse(random.randint(0,240), random.randint(0,240), 5, 5, backgroundColor, True)
        elif backgroundMode == 3:
            if redBackgroundComponent == 255 and blueBackgroundComponent > 0:
                self.LCD.ellipse(random.randint(0,240), random.randint(0,240), 5, 5, self.LCD.color(redBackgroundComponent, greenBackgroundComponent, blueBackgroundComponent), True)
                blueBackgroundComponent -= 1
            if redBackgroundComponent == 255 and blueBackgroundComponent == 0 and greenBackgroundComponent < 255:
                self.LCD.ellipse(random.randint(0,240), random.randint(0,240), 5, 5, self.LCD.color(redBackgroundComponent, greenBackgroundComponent, blueBackgroundComponent), True)
                greenBackgroundComponent += 1
            elif greenBackgroundComponent == 255 and redBackgroundComponent > 0:
                self.LCD.ellipse(random.randint(0,240), random.randint(0,240), 5, 5, self.LCD.color(redBackgroundComponent, greenBackgroundComponent, blueBackgroundComponent), True)
                redBackgroundComponent -= 1
            elif greenBackgroundComponent == 255 and redBackgroundComponent == 0 and blueBackgroundComponent < 255:
                self.LCD.ellipse(random.randint(0,240), random.randint(0,240), 5, 5, self.LCD.color(redBackgroundComponent, greenBackgroundComponent, blueBackgroundComponent), True)
                blueBackgroundComponent += 1
            elif blueBackgroundComponent == 255 and greenBackgroundComponent > 0:
                self.LCD.ellipse(random.randint(0,240), random.randint(0,240), 5, 5, self.LCD.color(redBackgroundComponent, greenBackgroundComponent, blueBackgroundComponent), True)
                greenBackgroundComponent -= 1
            elif blueBackgroundComponent == 255 and greenBackgroundComponent == 0 and redBackgroundComponent < 255:
                self.LCD.ellipse(random.randint(0,240), random.randint(0,240), 5, 5, self.LCD.color(redBackgroundComponent, greenBackgroundComponent, blueBackgroundComponent), True)
                redBackgroundComponent += 1


class Button(Toolset):
    def __init__(self, LCD: displayClass, x:int, y:int, text:str, textFont:int, fontSize:int, theme:themeClass,
                 borderText:list[str]=["top", "right", "bottom", "left"], state:int = 0, center:list[bool] = [False, False]):
        """
        Creates a button object centered around the *x* and *y* coordinates according to the *center* argument.
        Arguments:
            text (str): sets the main text of the button
            theme (themeClass): theme that determines the look of the button
            borderText (list): List with four items determining the text displayed on each edge of the button
            state (int): The state of the button:\n 0 = default; 1 = selected; 2 = pressed
            center (list): whether to center the button around x and y coordinates:
                [False, False] = "don\'t center"; [True, True] = "center around both"; 
                [True, False] = "center on x"; [False, True] = "center on y"
        """

        self.LCD = LCD
        super().__init__(LCD)
        self.position = [x, y]
        self.text = text
        self.font = textFont
        self.fontSize = fontSize
        self.theme = theme
        self.borderText = borderText
        self.state = state
        self.center = center

        self.calculate_spacing()
        [self.width, self.height] = self.calculate_dimensions()


    def calculate_spacing(self):
        """ Calculates the spacing around the border of the button to accompany for border text. """
        self.topBorderReserve = 0
        self.rightBorderReserve = 0
        self.bottomBorderReserve = 0
        self.leftBorderReserve = 0
    
        if len(self.borderText) != 4:
            raise ValueError("self.borderText must be a list with 4 elements [top, right, bottom, left], each element being a string that can be empty")
        else:
            if len(self.borderText[0]) > 0:
                self.topBorderReserve = self.calculate_text_dimensions(self.borderText[0], 0)[1] + self.theme.button_border_thickness
            if len(self.borderText[1]) > 0:
                self.rightBorderReserve = self.calculate_text_dimensions(self.borderText[1], 0)[0] + self.theme.button_border_thickness
            if len(self.borderText[2]) > 0:
                self.bottomBorderReserve = self.calculate_text_dimensions(self.borderText[2], 0)[1]  + self.theme.button_border_thickness
            if len(self.borderText[3]) > 0:
                self.leftBorderReserve = self.calculate_text_dimensions(self.borderText[3], 0)[0] + self.theme.button_border_thickness


    def calculate_dimensions(self) -> list:
        """ Calculates the width and height of the button with the current properties and returns the result. """
        return [(self.calculate_text_dimensions(self.text, self.font, self.fontSize)[0] + self.theme.button_border_thickness*2 + self.theme.horizontal_reserve*2 + self.leftBorderReserve + self.rightBorderReserve), 
                (self.calculate_text_dimensions(self.text, self.font, self.fontSize)[1] + self.theme.button_border_thickness*2 + self.theme.vertical_reserve*2 + self.topBorderReserve + self.bottomBorderReserve)]


    def update(self):
        """
        Updates spacing and calculated dimensions of the button.\n
        This must be called every time when the self.borderText variable is changed.
        """
        self.calculate_spacing()
        [self.width, self.height] = self.calculate_dimensions()


    def draw(self):
        """ Draws the button according to its current properties. """
        theme = self.theme
        LCD = self.LCD

        x = self.position[0]
        y = self.position[1]

        if self.center[0]:
            x -= self.width//2
        if self.center[1]:
            y -= self.height//2

        borderThickness = theme.button_border_thickness

        borderColor = theme.button_border_color
        textColor = theme.text_color
        buttonColor = theme.button_color
        borderTextColor = theme.button_border_text_color

        if self.state == 1:
            borderColor = theme.button_selected_border_color
            textColor = theme.button_selected_text_color
            buttonColor = theme.button_color
            borderTextColor = theme.button_border_text_color
        elif self.state == 2:
            borderColor = theme.button_selected_border_color
            textColor = theme.button_pressed_text_color
            buttonColor = theme.button_pressed_color
            borderTextColor = theme.button_border_text_color

        LCD.fill_rect(x, y, self.width, self.height, borderColor)
        LCD.fill_rect(x + self.leftBorderReserve + borderThickness, 
                      y + self.topBorderReserve + borderThickness, 
                      self.calculate_text_dimensions(self.text, self.font, self.fontSize)[0] + theme.horizontal_reserve*2,
                      self.calculate_text_dimensions(self.text, self.font, self.fontSize)[1] + theme.vertical_reserve*2, 
                      buttonColor)
        
        self.center_text(self.text,
                         x + (self.calculate_text_dimensions(self.text, self.font, self.fontSize)[0]//2 + borderThickness + self.theme.horizontal_reserve + self.leftBorderReserve),
                         y + (self.calculate_text_dimensions(self.text, self.font, self.fontSize)[1]//2 + borderThickness + self.theme.vertical_reserve + self.topBorderReserve),
                         textColor, buttonColor, self.font, self.fontSize)
        
        self.center_x_text(self.borderText[0], x + self.width//2, y - borderThickness, borderTextColor)
        self.center_y_text(self.borderText[1], x + self.width - self.rightBorderReserve, y + self.height//2, borderTextColor)
        self.center_x_text(self.borderText[2], x + self.width//2, y + self.height - self.bottomBorderReserve, borderTextColor)
        self.center_y_text(self.borderText[3], x + borderThickness, y + self.height//2, borderTextColor)

        