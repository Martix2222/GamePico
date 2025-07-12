from machine import Pin, freq
import time
import gc
import framebuf

# Overclock
freq(300_000_000)

import renderTools

import display_driver as display_driver
# The display driver must contain a color() function to convert 24-bit
# color space to the color space supported by the display.

# Initialize the display
LCD = display_driver.LCD_1inch3()

import themes
theme = themes.Default_theme(LCD)

# initialize buttons:
keyA = Pin(15,Pin.IN,Pin.PULL_UP)
keyB = Pin(17,Pin.IN,Pin.PULL_UP)
keyX = Pin(19 ,Pin.IN,Pin.PULL_UP)
keyY = Pin(21 ,Pin.IN,Pin.PULL_UP)

up = Pin(2,Pin.IN,Pin.PULL_UP)
down = Pin(18,Pin.IN,Pin.PULL_UP)
left = Pin(16,Pin.IN,Pin.PULL_UP)
right = Pin(20,Pin.IN,Pin.PULL_UP)
ctrl = Pin(3,Pin.IN,Pin.PULL_UP)

class main_menu():
    def __init__(self) -> None:
        self.Tools = renderTools.toolset(LCD)


    def static_menu(self, title="Menu", options=["Key A", "Key B", "Key C", "Key D"], backgroundColor=theme.background_color, secondaryBackgroundColor=theme.secondary_background_color,
              buttonColor=theme.button_color, buttonPressedColor = theme.button_pressed_color, buttonSelectedBorderColor = theme.button_selected_border_color, buttonBorderColor=theme.button_border_color, buttonBorderThickness=theme.button_border_thickness,
              buttonTextColor=theme.text_color, buttonPressedTextColor = theme.button_pressed_text_color, buttonSelectedTextColor=theme.button_selected_border_color, verticalReserve=theme.vertical_reserve, horizontalReserve=theme.horizontal_reserve, 
              introCircleColor=theme.primary_color, introBackgroundColor=theme.background_color, introCircleThickness=theme.intro_circle_thickness):
    
        tmpSelection = 0
        selection = 0
        justPressed = False
        buttonLock = False
        buttonRepetition_ns = 200000000
        repeatPressWaitTime = time.time_ns() + buttonRepetition_ns

        # Debug variables:
        enableDebug = False
        startTime = time.time_ns()
        renderEndTime = time.time_ns()
        showEndTime = time.time_ns()

        LCD.fill(backgroundColor)

        def reset_buttons(self):
            self.Tools.make_button(240 - buttonBorderThickness*2 - len(options[0])*4 - horizontalReserve - 8, 30, options[0], buttonTextColor, buttonColor, horizontalReserve, verticalReserve, buttonBorderColor, buttonBorderThickness, ["", "A", "",""])
            self.Tools.make_button(240 - buttonBorderThickness*2 - len(options[1])*4 - horizontalReserve - 8, 90, options[1], buttonTextColor, buttonColor, horizontalReserve, verticalReserve, buttonBorderColor, buttonBorderThickness, ["", "B", "",""])
            self.Tools.make_button(240 - buttonBorderThickness*2 - len(options[2])*4 - horizontalReserve - 8, 150, options[2], buttonTextColor, buttonColor, horizontalReserve, verticalReserve, buttonBorderColor, buttonBorderThickness, ["", "X", "",""])
            self.Tools.make_button(240 - buttonBorderThickness*2 - len(options[3])*4 - horizontalReserve - 8, 210, options[3], buttonTextColor, buttonColor, horizontalReserve, verticalReserve, buttonBorderColor, buttonBorderThickness, ["", "Y", "",""])


        while(1):
            self.Tools.update_animated_background(0, backgroundColor, secondaryBackgroundColor)

            # Draw the title
            LCD.fill_rect(15,105,20 + len(title)*8,30, buttonBorderColor)
            LCD.fill_rect(20,110,10 + len(title)*8,20, theme.secondary_color)
            self.Tools.center_text(title, 25 + len(title)*4, 120, 0xFFFF, theme.secondary_color)
            
            if enableDebug:
                # Draw debug stats
                freeMemoryKB = gc.mem_free()/1000
                self.Tools.center_y_text(f"Free RAM: {freeMemoryKB}{" "*(7-len(str(freeMemoryKB)))}KB", 5, 5, 0x0000, 0xFFFF)
                self.Tools.center_y_text(f"Total time: {round((time.time_ns() - startTime)/1000000, 1)} ms ", 5, 15, 0x0000, 0xFFFF)
                self.Tools.center_y_text(f"Render time: {round((renderEndTime - startTime)/1000000, 1)} ms ", 5, 25, 0x0000, 0xFFFF)
                self.Tools.center_y_text(f"Show time: {round((showEndTime - renderEndTime)/1000000, 1)} ms ", 5, 35, 0x0000, 0xFFFF)
            
            startTime = time.time_ns()


            self.Tools.draw_battery_statistics(5, 170, theme.text_color, theme.primary_color, theme.secondary_color, theme.text_color)
            

            if (justPressed == True and (up.value() == 0 or down.value() == 0 or left.value() == 0 or right.value() == 0) and repeatPressWaitTime < time.time_ns()):
                repeatPressWaitTime = time.time_ns() + buttonRepetition_ns
                buttonLock = True
                justPressed = False
            elif ((up.value() == 0 or down.value() == 0 or left.value() == 0 or right.value() == 0) and repeatPressWaitTime >= time.time_ns()):
                buttonLock = True
            else:
                buttonLock = False


            if(up.value() == 0 and not (keyA.value() == 0 or keyB.value() == 0 or keyX.value() == 0 or keyY.value() == 0) and not buttonLock):
                justPressed = True
                tmpSelection -= 1
                if tmpSelection < 1:
                    tmpSelection = 4
                
            if(down.value() == 0 and not (keyA.value() == 0 or keyB.value() == 0 or keyX.value() == 0 or keyY.value() == 0) and not buttonLock):
                justPressed = True
                tmpSelection += 1
                if tmpSelection > 4:
                    tmpSelection = 1
                
            if(left.value() == 0 and not (keyA.value() == 0 or keyB.value() == 0 or keyX.value() == 0 or keyY.value() == 0) and not buttonLock):
                justPressed = True
                tmpSelection -= 1
                if tmpSelection < 1:
                    tmpSelection = 4
            
            if(right.value() == 0 and not (keyA.value() == 0 or keyB.value() == 0 or keyX.value() == 0 or keyY.value() == 0) and not buttonLock):
                justPressed = True
                tmpSelection += 1
                if tmpSelection > 4:
                    tmpSelection = 1
                
            if(ctrl.value() == 0):
                selection = tmpSelection



            if(keyA.value() == 0 or selection==1):
                tmpSelection = 1
                selection = 1
                reset_buttons(self)
                self.Tools.make_button(240 - buttonBorderThickness*2 - len(options[0])*4 - horizontalReserve - 8, 30, options[0], buttonPressedTextColor, buttonPressedColor, horizontalReserve, verticalReserve, buttonSelectedBorderColor, buttonBorderThickness, ["", "A", "",""])
            elif tmpSelection == 1:
                self.Tools.make_button(240 - buttonBorderThickness*2 - len(options[0])*4 - horizontalReserve - 8, 30, options[0], buttonSelectedTextColor, buttonColor, horizontalReserve, verticalReserve, buttonSelectedBorderColor, buttonBorderThickness, ["", "A", "",""])
            else:
                self.Tools.make_button(240 - buttonBorderThickness*2 - len(options[0])*4 - horizontalReserve - 8, 30, options[0], buttonTextColor, buttonColor, horizontalReserve, verticalReserve, buttonBorderColor, buttonBorderThickness, ["", "A", "",""])
                

            if(keyB.value() == 0 or selection==2):
                tmpSelection = 2
                selection = 2
                reset_buttons(self)
                self.Tools.make_button(240 - buttonBorderThickness*2 - len(options[1])*4 - horizontalReserve - 8, 90, options[1], buttonPressedTextColor, buttonPressedColor, horizontalReserve, verticalReserve, buttonSelectedBorderColor, buttonBorderThickness, ["", "B", "",""])
            elif tmpSelection == 2:
                self.Tools.make_button(240 - buttonBorderThickness*2 - len(options[1])*4 - horizontalReserve - 8, 90, options[1], buttonSelectedTextColor, buttonColor, horizontalReserve, verticalReserve, buttonSelectedBorderColor, buttonBorderThickness, ["", "B", "",""])
            else:
                self.Tools.make_button(240 - buttonBorderThickness*2 - len(options[1])*4 - horizontalReserve - 8, 90, options[1], buttonTextColor, buttonColor, horizontalReserve, verticalReserve, buttonBorderColor, buttonBorderThickness, ["", "B", "",""])
                

            if(keyX.value() == 0 or selection==3):
                tmpSelection = 3
                selection = 3
                reset_buttons(self)
                self.Tools.make_button(240 - buttonBorderThickness*2 - len(options[2])*4 - horizontalReserve - 8, 150, options[2], buttonPressedTextColor, buttonPressedColor, horizontalReserve, verticalReserve, buttonSelectedBorderColor, buttonBorderThickness, ["", "X", "",""])
            elif tmpSelection == 3:
                self.Tools.make_button(240 - buttonBorderThickness*2 - len(options[2])*4 - horizontalReserve - 8, 150, options[2], buttonSelectedTextColor, buttonColor, horizontalReserve, verticalReserve, buttonSelectedBorderColor, buttonBorderThickness, ["", "X", "",""])
            else:
                self.Tools.make_button(240 - buttonBorderThickness*2 - len(options[2])*4 - horizontalReserve - 8, 150, options[2], buttonTextColor, buttonColor, horizontalReserve, verticalReserve, buttonBorderColor, buttonBorderThickness, ["", "X", "",""])


            if(keyY.value() == 0 or selection==4):
                tmpSelection = 4
                selection = 4
                reset_buttons(self)
                self.Tools.make_button(240 - buttonBorderThickness*2 - len(options[3])*4 - horizontalReserve - 8, 210, options[3], buttonPressedTextColor, buttonPressedColor, horizontalReserve, verticalReserve, buttonSelectedBorderColor, buttonBorderThickness, ["", "Y", "",""])
            elif tmpSelection == 4:
                self.Tools.make_button(240 - buttonBorderThickness*2 - len(options[3])*4 - horizontalReserve - 8, 210, options[3], buttonSelectedTextColor, buttonColor, horizontalReserve, verticalReserve, buttonSelectedBorderColor, buttonBorderThickness, ["", "Y", "",""])
            else:
                self.Tools.make_button(240 - buttonBorderThickness*2 - len(options[3])*4 - horizontalReserve - 8, 210, options[3], buttonTextColor, buttonColor, horizontalReserve, verticalReserve, buttonBorderColor, buttonBorderThickness, ["", "Y", "",""])

            renderEndTime = time.time_ns()

            LCD.show()
            showEndTime = time.time_ns()


            if selection != 0:
                if selection == 1:
                    self.Tools.scene_circle_transition(240 - buttonBorderThickness*2 - len(options[0])*4 - horizontalReserve - 8, 30, introCircleColor, introBackgroundColor, introCircleThickness, int(introCircleThickness/2))
                elif selection == 2:
                    self.Tools.scene_circle_transition(240 - buttonBorderThickness*2 - len(options[1])*4 - horizontalReserve - 8, 90, introCircleColor, introBackgroundColor, introCircleThickness, int(introCircleThickness/2))
                elif selection == 3:
                    self.Tools.scene_circle_transition(240 - buttonBorderThickness*2 - len(options[2])*4 - horizontalReserve - 8, 150, introCircleColor, introBackgroundColor, introCircleThickness, int(introCircleThickness/2))
                elif selection == 4:
                    self.Tools.scene_circle_transition(240 - buttonBorderThickness*2 - len(options[3])*4 - horizontalReserve - 8, 210, introCircleColor, introBackgroundColor, introCircleThickness, int(introCircleThickness/2))

                return selection
        return

    def mainloop(self):
            choice = 0
            while choice != 3:
                choice = self.static_menu("Main Menu", ["Play", "Settings", "Exit", "Controls"])
                if choice == 1:
                    pass
                elif choice == 2:
                    pass
                else:
                    pass
        



if __name__=='__main__':
    gc.collect()
    with open("logo 120x61.bin", "rb") as f:
        image = bytearray(f.read()[7:])

    LCD.fill(0xffff)
    LCD.blit(framebuf.FrameBuffer(image, 120, 61, framebuf.RGB565), 60, 90)
    LCD.show()

    time.sleep(2)

    MainMenu = main_menu()
    MainMenu.mainloop()