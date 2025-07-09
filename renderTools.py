import time
import math
import random

from display_driver import LCD_1inch3 as displayClass
# The display driver must contain a colour() function to convert 24-bit
# color space to the color space supported by the display.

from FONTS import FONTS


class toolset():
    def __init__(self, LCD:displayClass):
        self.LCD = LCD

        self.FONTS = FONTS(LCD)

        try: 
            import UPS_driver as UPS_driver
            # Create an ADS1115 ADC (16-bit) instance.
            self.UPS = UPS_driver.INA219(addr=0x43)
            self.UPSavailable = True
        except:
            self.UPSavailable = False


    def calculate_displayed_text_width(self, string, font, size):
        """ 
        Calculates the width of rendered text based on it's length, font and size.  
        """
        if font != 1:
            return 8*len(string)
        else:
            return (6*size - int(size/2))*len(string)-int((size+1)/2)


    def calculate_displayed_text_height(self, font, size):
        """ 
        Calculates the height of rendered text based on it's font and size.  
        """
        if font != 1:
            return 8
        else:
            return ((6*size - int(size/2))+size+1)


    def display_text(self, string:str, x:int, y:int, color:int, backgroundColor:int=-1, font:int=0, size:int=0):
        if font != 1:
            if backgroundColor > -1:
                self.LCD.fill_rect(x, y,len(string)*8, 8,backgroundColor)
            self.LCD.text(string, x, y, color)
        else:
            characterWidth = 6*size - int(size/2)
            ySize = (characterWidth+size+1)
            xSize = (characterWidth*len(string)-int((size+1)/2))

            if backgroundColor > -1:
                self.LCD.fill_rect(x, y, xSize, ySize, backgroundColor)
            self.FONTS.text(string, x, y, size, color)


    def center_text(self, string:str, x:int, y:int, color:int, backgroundColor:int=-1, font:int=0, size:int=0):
        """
        Centers the *string* on the given *x* and *y* coordinates
        *color* sets the color of the text
        *backgroundColor* sets the background color, if no value is given, the background will be transparent
        """
        if font != 1:
            if backgroundColor > -1:
                self.LCD.fill_rect(x - len(string) * 4, y-4,len(string)*8, 8,backgroundColor)
            self.LCD.text(string, x - len(string) * 4, y-4, color)
        else:
            characterWidth = 6*size - int(size/2)
            ySize = (characterWidth+size+1)
            xSize = (characterWidth*len(string)-int((size+1)/2))

            if backgroundColor > -1:
                self.LCD.fill_rect(x - int(xSize/2), y - int(ySize/2), xSize, ySize,backgroundColor)
            self.FONTS.text(string, x - int(xSize/2), y  -int(ySize/2), size, color)
        

    def center_y_text(self, string:str, x:int, y:int, color:int, backgroundColor:int=-1, font:int=0, size:int=0):
        """
        Centers the *string* on the given *y* coordinate, but not the *x* coordinate
        *color* sets the color of the text
        *backgroundColor* sets the background color, if no value is given, the background will be transparent
        """
        if font != 1:
            if backgroundColor != -1:
                self.LCD.fill_rect(x, y-4, len(string)*8, 8,backgroundColor)
            self.LCD.text(string, x , y-4, color)
        else:
            characterWidth = 6*size - int(size/2)
            ySize = (characterWidth+size+1)

            if backgroundColor > -1:
                xSize = (characterWidth*len(string)-int((size+1)/2))
                self.LCD.fill_rect(x, y - int(ySize/2), xSize, ySize,backgroundColor)
            self.FONTS.text(string, x, y - int(ySize/2), size, color)


    def center_x_text(self, string:str, x:int, y:int, color:int, backgroundColor:int=-1, font:int=0, size:int=0):
        """
        Centers the *string* on the given *x* coordinate, but not the *y* coordinate
        *color* sets the color of the text
        *backgroundColor* sets the background color, if no value is given, the background will be transparent
        """
        if font != 1:
            if backgroundColor != -1:
                self.LCD.fill_rect(x - len(string) * 4, y, len(string)*8, 8,backgroundColor)
            self.LCD.text(string, x - len(string) * 4, y, color)
        else:
            characterWidth = 6*size - int(size/2)
            xSize = (characterWidth*len(string)-int((size+1)/2))

            if backgroundColor > -1:
                ySize = (characterWidth+size+1)
                self.LCD.fill_rect(x - int(xSize/2), y, xSize, ySize,backgroundColor)
            self.FONTS.text(string, x - int(xSize/2), y, size, color)


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
        for i in range(1,170 + circleThickness + int(math.sqrt((120-x)*(120-x)+(120-y)*(120-y))), step):
            self.LCD.ellipse(x, y, i, i, circleColor, True)
            if i>circleThickness: self.LCD.ellipse(x, y, i-circleThickness, i-circleThickness, resultColor, True)
            self.LCD.show()
        return


    def make_button(self, x:int, y:int, text:str, textColor:int, buttonColor:int, horizontalReserve:int, verticalReserve:int, borderColor:int, borderThickness:int, borderText:list=["", "", "",""], borderTextColor:int=0xFFFF):
        """
        Creates a button with it's center at the given *x* and *y* coordinates\n
        *text* sets the main text of the button\n
        *textColor* sets the color of the main text\n
        *buttonColor* sets the color of the button\n
        *verticalReserve* sets the vertical space between the  main text and the border on both sides\n
        *horizontalReserve* sets the horizontal space between the  main text and the border on both sides\n
        *borderColor* sets the color of the border\n
        *borderThickness* sets the thickness of the border\n
        *borderText* is a list that sets the text inside each of the border sides "[top, right, bottom, left]"\n
        *borderTextColor* sets the color of the border text
        """
        topBorderReserve = 0
        rightBorderReserve = 0
        bottomBorderReserve = 0
        leftBorderReserve = 0

        if len(borderText) != 4:
            raise ValueError("borderText must be a list with 4 elements [top, right, bottom, left], each element being a string that can be empty")
        elif len(borderText[0]) > 0:
            topBorderReserve = 8 + borderThickness
        elif len(borderText[1]) > 0:
            rightBorderReserve = len(borderText[1])*8 + borderThickness
        elif len(borderText[2]) > 0:
            bottomBorderReserve = 8  + borderThickness
        elif len(borderText[3]) > 0:
            leftBorderReserve = len(borderText[3])*8 + borderThickness
        
        self.LCD.fill_rect(x - len(text)*4 - horizontalReserve - borderThickness - leftBorderReserve, y - 4 - verticalReserve - borderThickness - topBorderReserve,
                    len(text)*8 + horizontalReserve*2 + borderThickness*2 + rightBorderReserve + leftBorderReserve, 8 + verticalReserve*2 + borderThickness*2 + bottomBorderReserve + topBorderReserve, borderColor)

        self.LCD.fill_rect(x - len(text)*4 - horizontalReserve, y - 4 - verticalReserve, len(text)*8 + horizontalReserve*2, 8 + verticalReserve*2, buttonColor)
        self.center_text(text, x, y, textColor)

        self.center_text(borderText[0], x, y - 8 - verticalReserve - borderThickness, borderTextColor)
        self.center_y_text(borderText[1], x + len(text)*4 + horizontalReserve + borderThickness, y, borderTextColor)
        self.center_text(borderText[2], x, y + 8 + verticalReserve + borderThickness, borderTextColor)
        self.center_y_text(borderText[3], x - len(text)*4 - horizontalReserve - borderThickness, y, borderTextColor)
        
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
        Current supported *backgroundMode* values:\n
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
                