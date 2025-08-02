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

class Main(Toolset):
    def __init__(self) -> None:
        # Initialize the display
        self.LCD = display_driver.LCD_1inch3()
        super().__init__(self.LCD)

        self.color = display_driver.LCD_1inch3.color

        self.theme = themes.Default_theme()

        self.Menus = Menus(self.LCD, self.theme)

    
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
            choice = -1
            while choice != 3:
                self.LCD.WasPressed.clear_queue()
                choice = self.Menus.static_menu("Main Menu", ["Play", "Settings", "Exit", "Controls"], "logo 100x51.bin", [20, 30], [100, 51])
                self.LCD.WasPressed.clear_queue()
                if choice == 1:
                    # Play
                    snek = Snek(self.LCD)
                    snek.game_loop()
                    pass
                elif choice == 2:
                    # Settings
                    # TODO - add brightness settings
                    choice = -1
                    while choice != 1:
                        options = ["Brightness", "Main menu"]
                        center = [175, 120]
                        choice = self.Menus.scrolling_menu("Settings", options, self.theme, center, True)
                        if choice == 0:
                            # TODO brightness
                            pass
                        elif choice == 1:
                            # Return to main menu
                            self.scene_circle_transition(center[0], center[1], self.theme.primary_color, self.theme.background_color, self.theme.intro_circle_thickness, self.theme.intro_circle_thickness//2)

                    choice = -1
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
    

