# from machine import I2C,Pin,SPI,PWM,freq
import time
import gc

import renderTools

import display_driver
# The display driver must contain a colour() function to convert 24-bit
# color space to the color space supported by the display.¨

# Initialize the display
LCD = display_driver.LCD_1inch3()


class main_menu():
    def __init__(self) -> None:

        # Initialize the default colors
        self.primary_color = LCD.colour(255, 0, 0)
        self.secondary_color = LCD.colour(90, 90, 90)
        self.background_color = LCD.colour(255, 255, 255)
        self.text_color = LCD.colour(0, 0, 0)



    def mainloop(self):
        pass
        



if __name__=='__main__':
    MainMenu = main_menu()
    MainMenu.mainloop()