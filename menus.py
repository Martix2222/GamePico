import time
import gc

from drivers.display_driver import LCD_1inch3 as displayClass
# The display driver must contain a colour() function to convert 24-bit
# color space to the color space supported by the display.

from themes import Default_theme

class Menus():
    def __init__(self, LCD:displayClass):
        self.LCD = LCD
        self.color = LCD.color

        self.Tools = LCD.Tools
    
    def static_menu(self, title:str="Menu", options:list=["Key A", "Key B", "Key C", "Key D"], logoPath:str="", logoPos:list=[0,0], logoDim = [0,0], theme:Default_theme = Default_theme()):     
        Tools = self.Tools
        LCD = self.LCD
        
        tmpSelection = 0
        selection = 0

        # Debug variables:
        enableDebug = False
        startTime = time.time_ns()
        renderEndTime = time.time_ns()
        showEndTime = time.time_ns()

        LCD.fill(theme.background_color)

        def reset_buttons(self):
            Tools.make_button(240 - theme.button_border_thickness*2 - len(options[0])*4 - theme.horizontal_reserve - 8, 30, options[0], theme.text_color, theme.button_color, theme.horizontal_reserve, theme.vertical_reserve, theme.button_border_color, theme.button_border_thickness, ["", "A", "",""])
            Tools.make_button(240 - theme.button_border_thickness*2 - len(options[1])*4 - theme.horizontal_reserve - 8, 90, options[1], theme.text_color, theme.button_color, theme.horizontal_reserve, theme.vertical_reserve, theme.button_border_color, theme.button_border_thickness, ["", "B", "",""])
            Tools.make_button(240 - theme.button_border_thickness*2 - len(options[2])*4 - theme.horizontal_reserve - 8, 150, options[2], theme.text_color, theme.button_color, theme.horizontal_reserve, theme.vertical_reserve, theme.button_border_color, theme.button_border_thickness, ["", "X", "",""])
            Tools.make_button(240 - theme.button_border_thickness*2 - len(options[3])*4 - theme.horizontal_reserve - 8, 210, options[3], theme.text_color, theme.button_color, theme.horizontal_reserve, theme.vertical_reserve, theme.button_border_color, theme.button_border_thickness, ["", "Y", "",""])


        while(True):
            time.sleep_ms(5)
            
            Tools.update_animated_background(0, theme.background_color, theme.secondary_background_color)

            # Draw the title
            LCD.fill_rect(15,105,20 + len(title)*8,30, theme.button_border_color)
            LCD.fill_rect(20,110,10 + len(title)*8,20,theme.secondary_color)
            Tools.center_text(title, 25 + len(title)*4, 120, 0xFFFF,theme.secondary_color)
            
            if enableDebug:
                # Draw debug stats
                freeMemoryKB = gc.mem_free()/1000
                Tools.center_y_text(f"Free RAM: {freeMemoryKB}{" "*(7-len(str(freeMemoryKB)))}KB", 5, 5, 0x0000, 0xFFFF)
                Tools.center_y_text(f"Total time: {round((time.time_ns() - startTime)/1000000, 1)} ms ", 5, 15, 0x0000, 0xFFFF)
                Tools.center_y_text(f"Render time: {round((renderEndTime - startTime)/1000000, 1)} ms ", 5, 25, 0x0000, 0xFFFF)
                Tools.center_y_text(f"Show time: {round((showEndTime - renderEndTime)/1000000, 1)} ms ", 5, 35, 0x0000, 0xFFFF)
            else:
                # Show logo if specified
                if not logoPath == "":
                    try:
                        LCD.blit_image_file(logoPath, logoPos[0], logoPos[1], logoDim[0], logoDim[1])
                    except:
                        Tools.center_x_text(f"Error while loading logo: {logoPath}", 5, 25, self.color(255, 0, 0), 0xFFFF)

            
            startTime = time.time_ns()


            Tools.draw_battery_statistics(5, 170,theme.text_color,theme.primary_color,theme.secondary_color,theme.text_color)
            
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
                reset_buttons(self)
                Tools.make_button(240 - theme.button_border_thickness*2 - len(options[0])*4 - theme.horizontal_reserve - 8, 30, options[0], theme.button_pressed_text_color, theme.button_pressed_color, theme.horizontal_reserve, theme.vertical_reserve, theme.button_selected_border_color, theme.button_border_thickness, ["", "A", "",""])
            elif tmpSelection == 1:
                Tools.make_button(240 - theme.button_border_thickness*2 - len(options[0])*4 - theme.horizontal_reserve - 8, 30, options[0], theme.button_selected_text_color, theme.button_color, theme.horizontal_reserve, theme.vertical_reserve, theme.button_selected_border_color, theme.button_border_thickness, ["", "A", "",""])
            else:
                Tools.make_button(240 - theme.button_border_thickness*2 - len(options[0])*4 - theme.horizontal_reserve - 8, 30, options[0], theme.text_color, theme.button_color, theme.horizontal_reserve, theme.vertical_reserve, theme.button_border_color, theme.button_border_thickness, ["", "A", "",""])
                

            if(LCD.WasPressed.keyB() or selection==2):
                tmpSelection = 2
                selection = 2
                reset_buttons(self)
                Tools.make_button(240 - theme.button_border_thickness*2 - len(options[1])*4 - theme.horizontal_reserve - 8, 90, options[1], theme.button_pressed_text_color, theme.button_pressed_color, theme.horizontal_reserve, theme.vertical_reserve, theme.button_selected_border_color, theme.button_border_thickness, ["", "B", "",""])
            elif tmpSelection == 2:
                Tools.make_button(240 - theme.button_border_thickness*2 - len(options[1])*4 - theme.horizontal_reserve - 8, 90, options[1], theme.button_selected_text_color, theme.button_color, theme.horizontal_reserve, theme.vertical_reserve, theme.button_selected_border_color, theme.button_border_thickness, ["", "B", "",""])
            else:
                Tools.make_button(240 - theme.button_border_thickness*2 - len(options[1])*4 - theme.horizontal_reserve - 8, 90, options[1], theme.text_color, theme.button_color, theme.horizontal_reserve, theme.vertical_reserve, theme.button_border_color, theme.button_border_thickness, ["", "B", "",""])
                

            if(LCD.WasPressed.keyX() or selection==3):
                tmpSelection = 3
                selection = 3
                reset_buttons(self)
                Tools.make_button(240 - theme.button_border_thickness*2 - len(options[2])*4 - theme.horizontal_reserve - 8, 150, options[2], theme.button_pressed_text_color, theme.button_pressed_color, theme.horizontal_reserve, theme.vertical_reserve, theme.button_selected_border_color, theme.button_border_thickness, ["", "X", "",""])
            elif tmpSelection == 3:
                Tools.make_button(240 - theme.button_border_thickness*2 - len(options[2])*4 - theme.horizontal_reserve - 8, 150, options[2], theme.button_selected_text_color, theme.button_color, theme.horizontal_reserve, theme.vertical_reserve, theme.button_selected_border_color, theme.button_border_thickness, ["", "X", "",""])
            else:
                Tools.make_button(240 - theme.button_border_thickness*2 - len(options[2])*4 - theme.horizontal_reserve - 8, 150, options[2], theme.text_color, theme.button_color, theme.horizontal_reserve, theme.vertical_reserve, theme.button_border_color, theme.button_border_thickness, ["", "X", "",""])


            if(LCD.WasPressed.keyY() or selection==4):
                tmpSelection = 4
                selection = 4
                reset_buttons(self)
                Tools.make_button(240 - theme.button_border_thickness*2 - len(options[3])*4 - theme.horizontal_reserve - 8, 210, options[3], theme.button_pressed_text_color, theme.button_pressed_color, theme.horizontal_reserve, theme.vertical_reserve, theme.button_selected_border_color, theme.button_border_thickness, ["", "Y", "",""])
            elif tmpSelection == 4:
                Tools.make_button(240 - theme.button_border_thickness*2 - len(options[3])*4 - theme.horizontal_reserve - 8, 210, options[3], theme.button_selected_text_color, theme.button_color, theme.horizontal_reserve, theme.vertical_reserve, theme.button_selected_border_color, theme.button_border_thickness, ["", "Y", "",""])
            else:
                Tools.make_button(240 - theme.button_border_thickness*2 - len(options[3])*4 - theme.horizontal_reserve - 8, 210, options[3], theme.text_color, theme.button_color, theme.horizontal_reserve, theme.vertical_reserve, theme.button_border_color, theme.button_border_thickness, ["", "Y", "",""])

            renderEndTime = time.time_ns()

            LCD.show()
            showEndTime = time.time_ns()


            if selection != 0:
                if selection == 1:
                    Tools.scene_circle_transition(240 - theme.button_border_thickness*2 - len(options[0])*4 - theme.horizontal_reserve - 8, 30, theme.primary_color, theme.background_color, theme.intro_circle_thickness, int(theme.intro_circle_thickness/2))
                elif selection == 2:
                    Tools.scene_circle_transition(240 - theme.button_border_thickness*2 - len(options[1])*4 - theme.horizontal_reserve - 8, 90, theme.primary_color, theme.background_color, theme.intro_circle_thickness, int(theme.intro_circle_thickness/2))
                elif selection == 3:
                    Tools.scene_circle_transition(240 - theme.button_border_thickness*2 - len(options[2])*4 - theme.horizontal_reserve - 8, 150, theme.primary_color, theme.background_color, theme.intro_circle_thickness, int(theme.intro_circle_thickness/2))
                elif selection == 4:
                    Tools.scene_circle_transition(240 - theme.button_border_thickness*2 - len(options[3])*4 - theme.horizontal_reserve - 8, 210, theme.primary_color, theme.background_color, theme.intro_circle_thickness, int(theme.intro_circle_thickness/2))

                return selection
        return
