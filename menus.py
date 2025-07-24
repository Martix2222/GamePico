import time
import gc

from drivers.display_driver import LCD_1inch3 as displayClass
# The display driver must contain a colour() function to convert 24-bit
# color space to the color space supported by the display.

from themes import Default_theme

class Menus():
    def __init__(self, LCD:displayClass):
        self.LCD = LCD

        self.Tools = LCD.Tools
    
    def static_menu(self, title:str="Menu", options:list=["Key A", "Key B", "Key C", "Key D"], theme:Default_theme = Default_theme()):     
        tmpSelection = 0
        selection = 0

        # Debug variables:
        enableDebug = False
        startTime = time.time_ns()
        renderEndTime = time.time_ns()
        showEndTime = time.time_ns()

        self.LCD.fill(theme.background_color)

        def reset_buttons(self):
            self.Tools.make_button(240 - theme.button_border_thickness*2 - len(options[0])*4 - theme.horizontal_reserve - 8, 30, options[0], theme.text_color, theme.button_color, theme.horizontal_reserve, theme.vertical_reserve, theme.button_border_color, theme.button_border_thickness, ["", "A", "",""])
            self.Tools.make_button(240 - theme.button_border_thickness*2 - len(options[1])*4 - theme.horizontal_reserve - 8, 90, options[1], theme.text_color, theme.button_color, theme.horizontal_reserve, theme.vertical_reserve, theme.button_border_color, theme.button_border_thickness, ["", "B", "",""])
            self.Tools.make_button(240 - theme.button_border_thickness*2 - len(options[2])*4 - theme.horizontal_reserve - 8, 150, options[2], theme.text_color, theme.button_color, theme.horizontal_reserve, theme.vertical_reserve, theme.button_border_color, theme.button_border_thickness, ["", "X", "",""])
            self.Tools.make_button(240 - theme.button_border_thickness*2 - len(options[3])*4 - theme.horizontal_reserve - 8, 210, options[3], theme.text_color, theme.button_color, theme.horizontal_reserve, theme.vertical_reserve, theme.button_border_color, theme.button_border_thickness, ["", "Y", "",""])


        while(True):
            time.sleep_ms(5)
            
            self.Tools.update_animated_background(0, theme.background_color, theme.secondary_background_color)

            # Draw the title
            self.LCD.fill_rect(15,105,20 + len(title)*8,30, theme.button_border_color)
            self.LCD.fill_rect(20,110,10 + len(title)*8,20,theme.secondary_color)
            self.Tools.center_text(title, 25 + len(title)*4, 120, 0xFFFF,theme.secondary_color)
            
            if enableDebug:
                # Draw debug stats
                freeMemoryKB = gc.mem_free()/1000
                self.Tools.center_y_text(f"Free RAM: {freeMemoryKB}{" "*(7-len(str(freeMemoryKB)))}KB", 5, 5, 0x0000, 0xFFFF)
                self.Tools.center_y_text(f"Total time: {round((time.time_ns() - startTime)/1000000, 1)} ms ", 5, 15, 0x0000, 0xFFFF)
                self.Tools.center_y_text(f"Render time: {round((renderEndTime - startTime)/1000000, 1)} ms ", 5, 25, 0x0000, 0xFFFF)
                self.Tools.center_y_text(f"Show time: {round((showEndTime - renderEndTime)/1000000, 1)} ms ", 5, 35, 0x0000, 0xFFFF)
            
            startTime = time.time_ns()


            self.Tools.draw_battery_statistics(5, 170,theme.text_color,theme.primary_color,theme.secondary_color,theme.text_color)
            
            if self.LCD.WasPressed.keyA(False) or self.LCD.WasPressed.keyB(False) or self.LCD.WasPressed.keyX(False) or self.LCD.WasPressed.keyY(False):
                abxyPressed = True
            else:
                abxyPressed = False


            if (self.LCD.WasPressed.up(clearQueue=True) or self.LCD.WasPressed.left(clearQueue=True)) and not abxyPressed:
                tmpSelection -= 1
                if tmpSelection < 1:
                    tmpSelection = 4
                
            if (self.LCD.WasPressed.down(clearQueue=True) or self.LCD.WasPressed.right(clearQueue=True)) and not abxyPressed:
                tmpSelection += 1
                if tmpSelection > 4:
                    tmpSelection = 1

                
            if self.LCD.WasPressed.ctrl():
                selection = tmpSelection



            if(self.LCD.WasPressed.keyA() or selection==1):
                tmpSelection = 1
                selection = 1
                reset_buttons(self)
                self.Tools.make_button(240 - theme.button_border_thickness*2 - len(options[0])*4 - theme.horizontal_reserve - 8, 30, options[0], theme.button_pressed_text_color, theme.button_pressed_color, theme.horizontal_reserve, theme.vertical_reserve, theme.button_selected_border_color, theme.button_border_thickness, ["", "A", "",""])
            elif tmpSelection == 1:
                self.Tools.make_button(240 - theme.button_border_thickness*2 - len(options[0])*4 - theme.horizontal_reserve - 8, 30, options[0], theme.button_selected_text_color, theme.button_color, theme.horizontal_reserve, theme.vertical_reserve, theme.button_selected_border_color, theme.button_border_thickness, ["", "A", "",""])
            else:
                self.Tools.make_button(240 - theme.button_border_thickness*2 - len(options[0])*4 - theme.horizontal_reserve - 8, 30, options[0], theme.text_color, theme.button_color, theme.horizontal_reserve, theme.vertical_reserve, theme.button_border_color, theme.button_border_thickness, ["", "A", "",""])
                

            if(self.LCD.WasPressed.keyB() or selection==2):
                tmpSelection = 2
                selection = 2
                reset_buttons(self)
                self.Tools.make_button(240 - theme.button_border_thickness*2 - len(options[1])*4 - theme.horizontal_reserve - 8, 90, options[1], theme.button_pressed_text_color, theme.button_pressed_color, theme.horizontal_reserve, theme.vertical_reserve, theme.button_selected_border_color, theme.button_border_thickness, ["", "B", "",""])
            elif tmpSelection == 2:
                self.Tools.make_button(240 - theme.button_border_thickness*2 - len(options[1])*4 - theme.horizontal_reserve - 8, 90, options[1], theme.button_selected_text_color, theme.button_color, theme.horizontal_reserve, theme.vertical_reserve, theme.button_selected_border_color, theme.button_border_thickness, ["", "B", "",""])
            else:
                self.Tools.make_button(240 - theme.button_border_thickness*2 - len(options[1])*4 - theme.horizontal_reserve - 8, 90, options[1], theme.text_color, theme.button_color, theme.horizontal_reserve, theme.vertical_reserve, theme.button_border_color, theme.button_border_thickness, ["", "B", "",""])
                

            if(self.LCD.WasPressed.keyX() or selection==3):
                tmpSelection = 3
                selection = 3
                reset_buttons(self)
                self.Tools.make_button(240 - theme.button_border_thickness*2 - len(options[2])*4 - theme.horizontal_reserve - 8, 150, options[2], theme.button_pressed_text_color, theme.button_pressed_color, theme.horizontal_reserve, theme.vertical_reserve, theme.button_selected_border_color, theme.button_border_thickness, ["", "X", "",""])
            elif tmpSelection == 3:
                self.Tools.make_button(240 - theme.button_border_thickness*2 - len(options[2])*4 - theme.horizontal_reserve - 8, 150, options[2], theme.button_selected_text_color, theme.button_color, theme.horizontal_reserve, theme.vertical_reserve, theme.button_selected_border_color, theme.button_border_thickness, ["", "X", "",""])
            else:
                self.Tools.make_button(240 - theme.button_border_thickness*2 - len(options[2])*4 - theme.horizontal_reserve - 8, 150, options[2], theme.text_color, theme.button_color, theme.horizontal_reserve, theme.vertical_reserve, theme.button_border_color, theme.button_border_thickness, ["", "X", "",""])


            if(self.LCD.WasPressed.keyY() or selection==4):
                tmpSelection = 4
                selection = 4
                reset_buttons(self)
                self.Tools.make_button(240 - theme.button_border_thickness*2 - len(options[3])*4 - theme.horizontal_reserve - 8, 210, options[3], theme.button_pressed_text_color, theme.button_pressed_color, theme.horizontal_reserve, theme.vertical_reserve, theme.button_selected_border_color, theme.button_border_thickness, ["", "Y", "",""])
            elif tmpSelection == 4:
                self.Tools.make_button(240 - theme.button_border_thickness*2 - len(options[3])*4 - theme.horizontal_reserve - 8, 210, options[3], theme.button_selected_text_color, theme.button_color, theme.horizontal_reserve, theme.vertical_reserve, theme.button_selected_border_color, theme.button_border_thickness, ["", "Y", "",""])
            else:
                self.Tools.make_button(240 - theme.button_border_thickness*2 - len(options[3])*4 - theme.horizontal_reserve - 8, 210, options[3], theme.text_color, theme.button_color, theme.horizontal_reserve, theme.vertical_reserve, theme.button_border_color, theme.button_border_thickness, ["", "Y", "",""])

            renderEndTime = time.time_ns()

            self.LCD.show()
            showEndTime = time.time_ns()


            if selection != 0:
                if selection == 1:
                    self.Tools.scene_circle_transition(240 - theme.button_border_thickness*2 - len(options[0])*4 - theme.horizontal_reserve - 8, 30, theme.primary_color, theme.background_color, theme.intro_circle_thickness, int(theme.intro_circle_thickness/2))
                elif selection == 2:
                    self.Tools.scene_circle_transition(240 - theme.button_border_thickness*2 - len(options[1])*4 - theme.horizontal_reserve - 8, 90, theme.primary_color, theme.background_color, theme.intro_circle_thickness, int(theme.intro_circle_thickness/2))
                elif selection == 3:
                    self.Tools.scene_circle_transition(240 - theme.button_border_thickness*2 - len(options[2])*4 - theme.horizontal_reserve - 8, 150, theme.primary_color, theme.background_color, theme.intro_circle_thickness, int(theme.intro_circle_thickness/2))
                elif selection == 4:
                    self.Tools.scene_circle_transition(240 - theme.button_border_thickness*2 - len(options[3])*4 - theme.horizontal_reserve - 8, 210, theme.primary_color, theme.background_color, theme.intro_circle_thickness, int(theme.intro_circle_thickness/2))

                return selection
        return
