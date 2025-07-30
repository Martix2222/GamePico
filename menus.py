import time
import gc

from drivers.display_driver import LCD_1inch3 as displayClass
# The display driver must contain a colour() function to convert 24-bit
# color space to the color space supported by the display.

from render_tools import Toolset

from themes import Default_theme

class Menus(Toolset):
    def __init__(self, LCD:displayClass, theme:Default_theme):
        self.LCD = LCD
        self.color = LCD.color
        self.theme = theme

        super().__init__(LCD)
    
    def static_menu(self, title:str="Menu", options:list=["Key A", "Key B", "Key C", "Key D"], logoPath:str="", logoPos:list=[0,0], logoDim = [0,0], enableDebug = False):
        LCD = self.LCD
        theme = self.theme
        
        tmpSelection = 0
        selection = 0

        # Debug variables:
        startTime = time.time_ns()
        renderEndTime = time.time_ns()
        showEndTime = time.time_ns()

        buttonDimensionsA = self.calculate_button_dimensions(options[0], theme, ["", "A", "",""])
        buttonDimensionsB = self.calculate_button_dimensions(options[1], theme, ["", "B", "",""])
        buttonDimensionsX = self.calculate_button_dimensions(options[2], theme, ["", "X", "",""])
        buttonDimensionsY = self.calculate_button_dimensions(options[3], theme, ["", "Y", "",""])

        LCD.fill(theme.background_color)

        def reset_buttons():
            self.make_button(240 - buttonDimensionsA[0]//2, 30, options[0], theme, ["", "A", "",""])
            self.make_button(240 - buttonDimensionsB[0]//2, 90, options[1], theme, ["", "B", "",""])
            self.make_button(240 - buttonDimensionsX[0]//2, 150, options[2], theme, ["", "X", "",""])
            self.make_button(240 - buttonDimensionsY[0]//2, 210, options[3], theme, ["", "Y", "",""])


        while(True):
            time.sleep_ms(5)
            
            self.update_animated_background(0, theme.background_color, theme.secondary_background_color)

            # Draw the title
            titlePosition = [5, 100]
            titleTextDimensions = self.calculate_text_dimensions(title, 1, 2)
            self.LCD.fill_rect(titlePosition[0], titlePosition[1], titleTextDimensions[0]+theme.horizontal_reserve*4, titleTextDimensions[1]+theme.vertical_reserve*4//2, theme.button_border_color)
            self.LCD.fill_rect(titlePosition[0]+theme.horizontal_reserve, titlePosition[1]+theme.vertical_reserve//2, titleTextDimensions[0]+theme.horizontal_reserve*2, titleTextDimensions[1]+theme.vertical_reserve*2//2, theme.secondary_color)
            self.display_text(title, titlePosition[0]+theme.horizontal_reserve*2, titlePosition[1]+theme.vertical_reserve*2//2, theme.title_text_color,theme.secondary_color, 1, 2)
            
            if enableDebug:
                # Draw debug stats
                freeMemoryKB = gc.mem_free()/1000
                self.center_y_text(f"Free RAM: {freeMemoryKB}{" "*(7-len(str(freeMemoryKB)))}KB", 5, 5, 0x0000, 0xFFFF)
                self.center_y_text(f"Total time: {round((time.time_ns() - startTime)/1000000, 1)} ms ", 5, 15, 0x0000, 0xFFFF)
                self.center_y_text(f"Render time: {round((renderEndTime - startTime)/1000000, 1)} ms ", 5, 25, 0x0000, 0xFFFF)
                self.center_y_text(f"Show time: {round((showEndTime - renderEndTime)/1000000, 1)} ms ", 5, 35, 0x0000, 0xFFFF)
            else:
                # Show logo if specified
                if not logoPath == "":
                    try:
                        LCD.blit_image_file(logoPath, logoPos[0], logoPos[1], logoDim[0], logoDim[1])
                    except:
                        self.center_x_text(f"Error while loading logo: {logoPath}", 5, 25, self.color(255, 0, 0), 0xFFFF)

            
            startTime = time.time_ns()


            self.draw_battery_statistics(5, 170,theme.text_color,theme.primary_color,theme.secondary_color,theme.text_color)
            
            if LCD.WasPressed.keyA(False) or LCD.WasPressed.keyB(False) or LCD.WasPressed.keyX(False) or LCD.WasPressed.keyY(False):
                abxyPressed = True
            else:
                abxyPressed = False


            if (LCD.WasPressed.up(clearQueue=True) or LCD.WasPressed.left(clearQueue=True)) and not abxyPressed:
                tmpSelection -= 1
                if tmpSelection < 1:
                    tmpSelection = 4
                
            if (LCD.WasPressed.down(clearQueue=True) or LCD.WasPressed.right(clearQueue=True)) and not abxyPressed:
                tmpSelection += 1
                if tmpSelection > 4:
                    tmpSelection = 1

                
            if LCD.WasPressed.ctrl():
                selection = tmpSelection



            if(LCD.WasPressed.keyA() or selection==1):
                tmpSelection = 1
                selection = 1
                reset_buttons()
                self.make_button(240 - buttonDimensionsA[0]//2, 30, options[0], theme, ["", "A", "",""], 2)
            elif tmpSelection == 1:
                self.make_button(240 - buttonDimensionsA[0]//2, 30, options[0], theme, ["", "A", "",""], 1)
            else:
                self.make_button(240 - buttonDimensionsA[0]//2, 30, options[0], theme, ["", "A", "",""])
                

            if(LCD.WasPressed.keyB() or selection==2):
                tmpSelection = 2
                selection = 2
                reset_buttons()
                self.make_button(240 - buttonDimensionsB[0]//2, 90, options[1], theme, ["", "B", "",""], 2)
            elif tmpSelection == 2:
                self.make_button(240 - buttonDimensionsB[0]//2, 90, options[1], theme, ["", "B", "",""], 1)
            else:
                self.make_button(240 - buttonDimensionsB[0]//2, 90, options[1], theme, ["", "B", "",""])
                

            if(LCD.WasPressed.keyX() or selection==3):
                tmpSelection = 3
                selection = 3
                reset_buttons()
                self.make_button(240 - buttonDimensionsX[0]//2, 150, options[2], theme, ["", "X", "",""], 2)
            elif tmpSelection == 3:
                self.make_button(240 - buttonDimensionsX[0]//2, 150, options[2], theme, ["", "X", "",""], 1)
            else:
                self.make_button(240 - buttonDimensionsX[0]//2, 150, options[2], theme, ["", "X", "",""])


            if(LCD.WasPressed.keyY() or selection==4):
                tmpSelection = 4
                selection = 4
                reset_buttons()
                self.make_button(240 - buttonDimensionsY[0]//2, 210, options[3], theme, ["", "Y", "",""], 2)
            elif tmpSelection == 4:
                self.make_button(240 - buttonDimensionsY[0]//2, 210, options[3], theme, ["", "Y", "",""], 1)
            else:
                self.make_button(240 - buttonDimensionsY[0]//2, 210, options[3], theme, ["", "Y", "",""])

            renderEndTime = time.time_ns()

            LCD.show()
            showEndTime = time.time_ns()


            if selection != 0:
                if selection == 1:
                    self.scene_circle_transition(240 - buttonDimensionsA[0]//2, 30, theme.primary_color, theme.background_color, theme.intro_circle_thickness, theme.intro_circle_thickness//2)
                elif selection == 2:
                    self.scene_circle_transition(240 - buttonDimensionsB[0]//2, 90, theme.primary_color, theme.background_color, theme.intro_circle_thickness, theme.intro_circle_thickness//2)
                elif selection == 3:
                    self.scene_circle_transition(240 - buttonDimensionsX[0]//2, 150, theme.primary_color, theme.background_color, theme.intro_circle_thickness, theme.intro_circle_thickness//2)
                elif selection == 4:
                    self.scene_circle_transition(240 - buttonDimensionsY[0]//2, 210, theme.primary_color, theme.background_color, theme.intro_circle_thickness, theme.intro_circle_thickness//2)

                return selection
    

    def scrolling_menu(self, title:str="scrolling menu", options:list=["option1", "option2", "option3", "option4", "option5"], theme:Default_theme = Default_theme()):
        LCD = self.LCD
        
        tmpSelection = 0
        selection = 0

        
