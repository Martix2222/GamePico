from drivers.display_driver import LCD_1inch3
# The display driver must contain a color() function to convert 24-bit
# color space to the color space supported by the display.

color = LCD_1inch3.color

class Default_theme():
    def __init__(self):
        self.primary_color = color(255, 0, 0)
        self.secondary_color = color(90, 90, 90)
        self.background_color = color(255, 255, 255)
        self.secondary_background_color = color(200, 200, 200)
        self.title_text_color = color(255, 255, 255)
        self.text_color = color(0, 0, 0)
        self.vertical_reserve=10
        self.horizontal_reserve=6
        self.intro_circle_thickness=20

        # Buttons
        self.button_color = color(240, 50, 40)
        self.button_pressed_color = color(0, 255, 0)
        self.button_border_color = color(0, 0, 0)
        self.button_border_text_color = color(200, 200, 200)
        self.button_selected_border_color = color(127, 127, 127)
        self.button_selected_text_color = color(127, 127, 127)
        self.button_pressed_text_color = color(255, 255, 255)
        self.button_border_thickness = 4
        self.button_spacing = 10