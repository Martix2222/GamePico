from machine import freq
import time
import gc

import render_tools

from games.snek import Snek

import drivers.display_driver as display_driver
# The display driver must contain a color() function to convert 24-bit
# color space to the color space supported by the display.

import themes

from menus import Menus

# Overclock
freq(250_000_000)

class Main():
    def __init__(self) -> None:
        # Initialize the display
        self.LCD = display_driver.LCD_1inch3()
        self.color = display_driver.LCD_1inch3.color

        self.theme = themes.Default_theme()

        self.Tools = self.LCD.Tools

        self.Menus = Menus(self.LCD)

    
    def start(self, showSplash = True, recordSession = False):
        self.LCD.set_brightness(100)
        self.LCD.enableContinuousRecording = recordSession
        if showSplash:
            self.LCD.fill(0xffff)

            self.LCD.blit_image_file("logo 240x123.bin", 0, 58, 240, 123, 1000)
            
            self.LCD.show()
            time.sleep(2)
            self.LCD.show()

        self.main_loop()


    def main_loop(self):
            choice = 0
            while True:
                self.LCD.WasPressed.clear_queue()
                choice = self.Menus.static_menu("Main Menu", ["Play", "Settings", "Exit", "Controls"], "logo 100x51.bin", [20, 30], [100, 51], self.theme)
                if choice == 1:
                    # Play option
                    snek = Snek(self.LCD)
                    snek.game_loop()
                    pass
                elif choice == 2:
                    # Settings option
                    pass
                elif choice == 3:
                    # Exit option - break out of the loop
                    break
                elif choice == 4:
                    # Controls option
                    pass


if __name__=='__main__':
    gc.collect()

    MainMenu = Main()
    MainMenu.start()
    
    MainMenu.LCD.fill(0xffff)
    MainMenu.LCD.show()
    

