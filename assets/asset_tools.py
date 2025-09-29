from drivers.display_driver import LCD_1inch3 as displayClass
# The display driver must contain a color() function to convert 24-bit
# color space to the color space supported by the display.

from render_tools import Toolset

from themes import Default_theme as themeClass


class Asset():
    def __init__(self, LCD: displayClass, theme: themeClass, assetPath:str, singleStateDimensions:tuple[int, int], position:tuple[int, int]):
        """
        This creates an object that is tied to a graphical asset that has multiple states, that can for example create an animation when sequenced together.
        This can for example be used for assets exported from Aseprite, where there are multiple states in one image. 
        This function loads them and then sets the *Asset.stateCount* variable accordingly.
        It calculates *Asset.stateCount* by dividing the image with the states into separate parts based on the initial *singleStateDimensions* argument.
        Arguments:
            LCD (displayClass): The object of the display driver with a frame buffer to which the asset is drawn.
            theme (themeClass): The global theme used especially for the transparent color parameter.
            assetPath (str): The path to a .binFrame image that contains all the states of the asset in a left-to-right sequence.
            singleStateDimensions (tuple[int, int]): The dimensions in a *(width, height)* format of a single state and variation of the asset.
                This also dictates the final size of the asset that is drawn on the screen.
            position (tuple[int, int]): The position where the asset will be drawn by calling the *Asset.draw()* function.
                (This is also subsequently saved and can be changed by accessing the *Asset.position* variable.)

        """
        self.LCD = LCD
        self.position = position

        self.transparentColor = theme.transparent_color

        self.filePath:str = assetPath

        self.dimensions:tuple[int, int] = singleStateDimensions

        self.header = self.LCD.read_binFrame_header(assetPath)

        self.calculate_states()
        self.state:int = 0
        self.variation:int = 0


    def calculate_states(self):
        # Calculate the number of states along the horizontal axis
        self.stateCount = self.header["width"]//self.dimensions[0]

        # Calculate the number of variations along the vertical axis
        self.variationCount = self.header["width"]//self.dimensions[0]


    def draw_asset(self, memLimit:int=1000):
        """ Draws the asset to the image buffer. """
        if self.state >= self.stateCount:
            raise ValueError("The state parameter must not exceed the number of states of the asset")
        if self.state >= self.stateCount:
            raise ValueError("The variation parameter must not exceed the number of variations of the asset")

        x = self.dimensions[0]*self.state
        y = self.dimensions[0]*self.variation
        
        self.LCD.blit_image_from_file(self.filePath, self.position, self.dimensions, (x, y), memLimit, self.transparentColor)


            
