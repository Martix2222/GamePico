# This script converts a binary file containing 16-bit color values (RGB565) that is generated when taking a screenshot
# into a binary file with 24-bit RGB values. This binary file is then converted into a bmp image using the microbmp library.

from microbmp import MicroBMP

inputFile = "menu_screenshot.bin"
outputFile = "screenshot.bmp"


def color(value565):
    """ 
    Converts the 16-bit color format to the 24-bit RGB format.
    """
    r5 = (value565 >> 11) & 0x1F
    g6 = (value565 >> 5) & 0x3F
    b5 = value565 & 0x1F

    # Convert to 8-bit (0–255) by scaling:
    r8 = (r5 * 255) // 31
    g8 = (g6 * 255) // 63
    b8 = (b5 * 255) // 31

    return (r8, g8, b8)


outputImage = MicroBMP(240, 240, 24)

with open(inputFile, 'rb') as tmp:
    for i in range(0, len(tmp.read()), 2):
        tmp.seek(i) 
        value = tmp.read(2)
        color888 = color(int.from_bytes(value, 'big'))
        outputImage[int((i/2)%240), int((i/2)//240)] = color888
    tmp.close()

outputImage.save(outputFile)          