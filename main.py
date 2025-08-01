from machine import freq
import time
import gc

from games.snek import Snek

import drivers.display_driver as display_driver
# The display driver must contain a color() function to convert 24-bit
# color space to the color space supported by the display.

from render_tools import Toolset

import themes

from menus import Menus

# Overclock
freq(250_000_000)

class Main(Menus):
    def __init__(self) -> None:
        # Initialize the display
        self.LCD = display_driver.LCD_1inch3()

        self.color = display_driver.LCD_1inch3.color

        self.theme = themes.Default_theme()
        super().__init__(self.LCD, self.theme)

    
    def start(self, showSplash = True, recordSession = False):
        self.LCD.brightness(100)
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
                choice = self.static_menu("Main Menu", ["Play", "Settings", "Exit", "Controls"], "logo 100x51.bin", [20, 30], [100, 51])
                self.LCD.WasPressed.clear_queue()
                if choice == 1:
                    # Play
                    snek = Snek(self.LCD)
                    snek.game_loop()
                    pass
                elif choice == 2:
                    # Settings
                    choice = 0
                    while True:
                        options = ["Brightness", "Main menu"]
                        center = [175, 120]
                        self.LCD.WasPressed.clear_queue()
                        choice = self.scrolling_menu("Settings", options, choice, center, [True])

                        if choice == 0:
                            choice += self.brightness_menu_button(center)
                            if choice < 0:
                                choice = 0
                            elif choice > len(options)-1:
                                choice = len(options)-1
                        
                        elif choice == 1:
                            # Return to main menu
                            break

                    choice = 0
                elif choice == 3:
                    # Exit
                    break
                elif choice == 4:
                    # Controls
                    # TODO
                    pass


if __name__=='__main__':
    gc.collect()

    MainMenu = Main()
    MainMenu.start()
    
    MainMenu.LCD.fill(0xffff)
    MainMenu.LCD.show()
    

