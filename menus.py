import time
import gc

from drivers.display_driver import LCD_1inch3 as displayClass
# The display driver must contain a color() function to convert 24-bit
# color space to the color space supported by the display.

from render_tools import Toolset
from render_tools import Button

from themes import Default_theme

class Menus(Toolset):
    def __init__(self, LCD:displayClass, theme:Default_theme):
        self.LCD = LCD
        self.color = LCD.color
        self.theme = theme

        super().__init__(LCD)
    
    def static_menu(self, title:str="Menu", options:list=["Key A", "Key B", "Key C", "Key D"], logoPath:str="", logoPos:list=[0,0], logoDim = [0,0], enableDebug = False):
        """ A menu with four options, each tied to one of the A, B, X or Y buttons of the display. """
        LCD = self.LCD
        theme = self.theme
        
        tmpSelection = 0
        selection = 0

        # Debug variables:
        startTime = time.time_ns()
        renderEndTime = time.time_ns()
        showEndTime = time.time_ns()

        buttonA = Button(LCD, 240, 30, options[0], 0, 0, theme, ["", "A", "",""], 0, [False, True])
        buttonA.position[0] -= buttonA.width

        buttonB = Button(LCD, 240, 90, options[1], 0, 0, theme, ["", "B", "",""], 0, [False, True])
        buttonB.position[0] -= buttonB.width

        buttonX = Button(LCD, 240, 150, options[2], 0, 0, theme, ["", "X", "",""], 0, [False, True])
        buttonX.position[0] -= buttonX.width

        buttonY = Button(LCD, 240, 210, options[3], 0, 0, theme, ["", "Y", "",""], 0, [False, True])
        buttonY.position[0] -= buttonY.width

        LCD.fill(theme.background_color)

        def reset_buttons():
            buttonA.state, buttonB.state, buttonX.state, buttonY.state = 0,0,0,0


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
                buttonA.state = 2
                buttonA.draw()
            elif tmpSelection == 1:
                buttonA.state = 1
                buttonA.draw()
            else:
                buttonA.state = 0
                buttonA.draw()
                

            if(LCD.WasPressed.keyB() or selection==2):
                tmpSelection = 2
                selection = 2
                reset_buttons()
                buttonB.state = 2
                buttonB.draw()
            elif tmpSelection == 2:
                buttonB.state = 1
                buttonB.draw()
            else:
                buttonB.state = 0
                buttonB.draw()
                

            if(LCD.WasPressed.keyX() or selection==3):
                tmpSelection = 3
                selection = 3
                reset_buttons()
                buttonX.state = 2
                buttonX.draw()
            elif tmpSelection == 3:
                buttonX.state = 1
                buttonX.draw()
            else:
                buttonX.state = 0
                buttonX.draw()


            if(LCD.WasPressed.keyY() or selection==4):
                tmpSelection = 4
                selection = 4
                reset_buttons()
                buttonY.state = 2
                buttonY.draw()
            elif tmpSelection == 4:
                buttonY.state = 1
                buttonY.draw()
            else:
                buttonY.state = 0
                buttonY.draw()

            renderEndTime = time.time_ns()

            LCD.show()
            showEndTime = time.time_ns()


            if selection != 0:
                if selection == 1:
                    self.scene_circle_transition(240 - buttonA.width//2, 30, theme.primary_color, theme.background_color, theme.intro_circle_thickness, theme.intro_circle_thickness//2)
                elif selection == 2:
                    self.scene_circle_transition(240 - buttonB.width//2, 90, theme.primary_color, theme.background_color, theme.intro_circle_thickness, theme.intro_circle_thickness//2)
                elif selection == 3:
                    self.scene_circle_transition(240 - buttonX.width//2, 150, theme.primary_color, theme.background_color, theme.intro_circle_thickness, theme.intro_circle_thickness//2)
                elif selection == 4:
                    self.scene_circle_transition(240 - buttonY.width//2, 210, theme.primary_color, theme.background_color, theme.intro_circle_thickness, theme.intro_circle_thickness//2)

                return selection
    

    def scrolling_menu(self, title:str="scrolling menu", options:list[str]=["option1", "option2", "option3", "option4", "option5"],
                       theme:Default_theme = Default_theme(), center:list[int] = [175, 120], skipExitTransition:bool = False) -> int:
        """
        A menu with unlimited amount of options which can be scrolled through using the joystick on the display.\n 
        The returned value is the index of the selected option out of the *options* argument.
        """
        
        LCD = self.LCD
        x, y = center

        # Initialize variables
        tmpSelection = 0
        selection = 0

        font = 0
        fontSize = 0

        buttons = []

        update = True
        
        targetScrollOffset = 0
        currentScrollOffset = 0

        selection = -1 

        # Initialize all buttons
        for i in range(len(options)):
            if i == 0:
                buttons.append(Button(LCD, x, y, options[i], font, fontSize, theme, ["", "", "", ""], 0, [True, False]))
                buttons[i].position[1] -= buttons[i].height // 2
                y -= buttons[i].height // 2
            else:
                buttons.append(Button(LCD, x, y, options[i], font, fontSize, theme, ["", "", "", ""], 0, [True, False]))
                
            y += buttons[i].height + theme.button_spacing


        while True:
            if selection == -1:
                if LCD.WasPressed.up(clearQueue=True) and tmpSelection > 0:
                    update = True
                    tmpSelection -= 1
                    targetScrollOffset += buttons[tmpSelection+1].position[1] - buttons[tmpSelection].position[1]

                if LCD.WasPressed.keyA() and 1 < tmpSelection:
                    update = True
                    tmpSelection -= 2
                    selection = tmpSelection
                    targetScrollOffset += buttons[tmpSelection+2].position[1] - buttons[tmpSelection].position[1]

                if LCD.WasPressed.keyB() and 0 < tmpSelection:
                    update = True
                    tmpSelection -= 1
                    selection = tmpSelection
                    targetScrollOffset += buttons[tmpSelection+1].position[1] - buttons[tmpSelection].position[1]
                

                if LCD.WasPressed.down(clearQueue=True) and tmpSelection < len(buttons)-1:
                    update = True
                    tmpSelection += 1
                    targetScrollOffset -= buttons[tmpSelection].position[1] - buttons[tmpSelection-1].position[1]
                
                if LCD.WasPressed.keyX() and tmpSelection < len(buttons)-1:
                    update = True
                    tmpSelection += 1
                    selection = tmpSelection
                    targetScrollOffset -= buttons[tmpSelection].position[1] - buttons[tmpSelection-1].position[1]

                if LCD.WasPressed.keyY() and tmpSelection < len(buttons)-2:
                    update = True
                    tmpSelection += 2
                    selection = tmpSelection
                    targetScrollOffset -= buttons[tmpSelection].position[1] - buttons[tmpSelection-2].position[1]

                if LCD.WasPressed.ctrl():
                    update = True
                    selection = tmpSelection


            if currentScrollOffset != targetScrollOffset:
                change = 0
                if abs(currentScrollOffset - targetScrollOffset) < 5:
                    change = 1
                else:
                    change = abs(currentScrollOffset - targetScrollOffset)//5 + 1

                if currentScrollOffset > targetScrollOffset:
                    change = change * -1
                
                for button in buttons:
                    button.position[1] += change

                currentScrollOffset += change
            else:
                time.sleep_ms(100) # Limit the update rate when nothing is happening
                if selection > -1:
                    if not skipExitTransition:
                        self.scene_circle_transition(x, 120, theme.primary_color, theme.background_color, theme.intro_circle_thickness, theme.intro_circle_thickness//2)
                    return selection

            # If a button was pressed, this updates the buttons' state and side text
            if update:
                update = False
                for i in range(len(buttons)):
                    if selection == -1:
                        buttons[i].state = 0
                        buttons[i].borderText = ["", "", "", ""]
                        
                        if i == tmpSelection:
                            buttons[i].state = 1
                            buttons[i].borderText = ["", "", "", ""]
                        elif i == tmpSelection-2:
                            buttons[i].borderText = ["", "A", "", ""]
                        elif i == tmpSelection-1:
                            buttons[i].borderText = ["", "B", "", ""]
                        elif i == tmpSelection+1:
                            buttons[i].borderText = ["", "X", "", ""]
                        elif i == tmpSelection+2:
                            buttons[i].borderText = ["", "Y", "", ""]
                    else:
                        if i == selection:
                            buttons[i].state = 2
                        else:
                            buttons[i].state = 0
                    
                    buttons[i].update()
            
            
            LCD.fill(theme.background_color)

            for button in buttons:
                # Skip buttons outside of the display
                if (button.position[1]+button.height) > 0 and button.position[1] < self.LCD.height: 
                    button.draw()

            # Draw the title
            titleTextDimensions = self.calculate_text_dimensions(title, 1, 2)
            titlePosition = [5, (120 - (titleTextDimensions[1]+theme.vertical_reserve*4//2)//2)]
            self.LCD.fill_rect(titlePosition[0], titlePosition[1], titleTextDimensions[0]+theme.horizontal_reserve*4, titleTextDimensions[1]+theme.vertical_reserve*4//2, theme.button_border_color)
            self.LCD.fill_rect(titlePosition[0]+theme.horizontal_reserve, titlePosition[1]+theme.vertical_reserve//2, titleTextDimensions[0]+theme.horizontal_reserve*2, titleTextDimensions[1]+theme.vertical_reserve*2//2, theme.secondary_color)
            self.display_text(title, titlePosition[0]+theme.horizontal_reserve*2, titlePosition[1]+theme.vertical_reserve*2//2, theme.title_text_color,theme.secondary_color, 1, 2)
            
            LCD.show()

