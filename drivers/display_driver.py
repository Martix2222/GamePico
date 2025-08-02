from machine import Pin,SPI,PWM
import framebuf
import time
import os
import gc
from drivers.sdcard_driver import SDCard


# Display pins
BL = 13
DC = 8
RST = 12
MOSI = 11
SCK = 10
CS = 9

# SD reader pins
SD_CS = 22
SD_MISO = 4
SD_CLK = 6
SD_MOSI = 7

# initialize buttons:
keyA = Pin(15,Pin.IN,Pin.PULL_UP)
keyB = Pin(17,Pin.IN,Pin.PULL_UP)
keyX = Pin(19,Pin.IN,Pin.PULL_UP)
keyY = Pin(21,Pin.IN,Pin.PULL_UP)

up = Pin(2,Pin.IN,Pin.PULL_UP)
down = Pin(18,Pin.IN,Pin.PULL_UP)
left = Pin(16,Pin.IN,Pin.PULL_UP)
right = Pin(20,Pin.IN,Pin.PULL_UP)
ctrl = Pin(3,Pin.IN,Pin.PULL_UP)

class Was_Pressed():
    def __init__(self):
        self.registeredPresses = {}
        self.lastPressTime = {}
        self.lastReleaseTime = {}

        # Values in ms
        self.multiClickEliminationDelay = 50
        self.holdRepetitionDelay = 500
        self.holdRepetitionFrequency = 200


        keyA.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=self.state_handler)
        keyB.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=self.state_handler)
        keyX.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=self.state_handler)
        keyY.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=self.state_handler)
        
        up.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=self.state_handler)
        down.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=self.state_handler)
        left.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=self.state_handler)
        right.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=self.state_handler)
        ctrl.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=self.state_handler)


    def state_handler(self, pin:Pin):
        if pin.value() == 0:
            self.press_handler(pin)
        else:
            self.release_handler(pin)


    def press_handler(self, pin:Pin):
        # Eliminate unintentional multi clicks caused by bad buttons
        if not pin in self.lastReleaseTime.keys():
            self.lastPressTime[pin] = time.time_ns()
            if pin in self.registeredPresses.keys():
                self.registeredPresses[pin] += 1
            else:
                self.registeredPresses[pin] = 1
        elif (time.time_ns() - self.lastReleaseTime[pin]) > (self.multiClickEliminationDelay*1000000):
            self.lastPressTime[pin] = time.time_ns()
            if pin in self.registeredPresses.keys():
                self.registeredPresses[pin] += 1
            else:
                self.registeredPresses[pin] = 1
        else:
            pass
    

    def release_handler(self, pin:Pin):
        self.lastReleaseTime[pin] = time.time_ns()
    

    def clear_queue(self):
        self.registeredPresses = {}


    def was_pressed(self, pin:Pin, subtract:bool = True, clearQue:bool = False):
        """
        Checks if a button was pressed.
        Arguments:
            pin (int): The pin number of the button to check.
            subtract (bool): If True, the count of presses in the queue will be decremented by 1 after checking. \n
                             If False, the count will not be changed.
            clearQue (bool): If True, the count of presses of the selected button pin in the queue will be set to 0 after checking. \n
        Returns:
            bool: True if the button was pressed at least once, False otherwise.
        """

        if pin in self.registeredPresses.keys():
            if self.registeredPresses[pin] > 0:
                if subtract:
                    self.registeredPresses[pin] -= 1
                if clearQue:
                    self.registeredPresses[pin] = 0
                return True
            else:
                return False
        else:
            return False
    
    def keyA(self, subtract:bool = True, clearQueue:bool = False):
        return self.was_pressed(keyA, subtract, clearQueue)
    def keyB(self, subtract:bool = True, clearQueue:bool = False):
        return self.was_pressed(keyB, subtract, clearQueue)
    def keyX(self, subtract:bool = True, clearQueue:bool = False):
        return self.was_pressed(keyX, subtract, clearQueue)
    def keyY(self, subtract:bool = True, clearQueue:bool = False):
        return self.was_pressed(keyY, subtract, clearQueue)

    def up(self, subtract:bool = True, clearQueue:bool = False):
        return self.was_pressed(up, subtract, clearQueue)
    def down(self, subtract:bool = True, clearQueue:bool = False):
        return self.was_pressed(down, subtract, clearQueue)
    def left(self, subtract:bool = True, clearQueue:bool = False):
        return self.was_pressed(left, subtract, clearQueue)
    def right(self, subtract:bool = True, clearQueue:bool = False):
        return self.was_pressed(right, subtract, clearQueue)
    def ctrl(self, subtract:bool = True, clearQueue:bool = False):
        return self.was_pressed(ctrl, subtract, clearQueue)


class LCD_1inch3(framebuf.FrameBuffer):
    def __init__(self):
        self.width = 240
        self.height = 240

        self.WasPressed = Was_Pressed()
        
        self.cs = Pin(CS,Pin.OUT)
        self.rst = Pin(RST,Pin.OUT)
        
        self.cs(1)
        # self.spi = SPI(1)
        # self.spi = SPI(1,1000_000)
        self.spi = SPI(1,125_000_000,polarity=0, phase=0,sck=Pin(SCK),mosi=Pin(MOSI),miso=None)
        self.dc = Pin(DC,Pin.OUT)
        self.dc(1)
        gc.collect()
        self.buffer = bytearray(self.height * self.width * 2)
        super().__init__(self.buffer, self.width, self.height, framebuf.RGB565)
        self.init_display()
        
        self.red   =   0x07E0
        self.green =   0x001f
        self.blue  =   0xf800
        self.white =   0xffff

        self.currentBrightness = 100.0
        self.brightness(self.currentBrightness)

        self.enableContinuousRecording = False

        # This is currently mostly for reference and sets the time between frames when recording.
        # This value should be set as the frame time when exporting the recording as a GIF.
        self.frameTime_ms = 50

        self.SDcs = Pin(SD_CS)
        self.SDcs(1)

        self.sdMountPoint = "/sd"
        self.mainScreenshotFolder = "/screenshots"
        self.currentRecordingFolder = "/0"
        self.stillRecording = False

    def init_save_location(self):
        try:
            SD = SDCard(SPI(0, 125_000_000, sck=Pin(SD_CLK),mosi=Pin(SD_MOSI),miso=Pin(SD_MISO)), self.SDcs, 125_000_000)
            os.mount(SD, self.sdMountPoint)
            SDavailable = True
        except OSError:
            SDavailable = False


        if SDavailable:
            if not self.mainScreenshotFolder[1:] in os.listdir(self.sdMountPoint):
                os.mkdir(self.sdMountPoint + self.mainScreenshotFolder)
            
            self.currentRecordingFolder = "/" + str(len(os.listdir(self.sdMountPoint + self.mainScreenshotFolder)))
            os.mkdir(self.sdMountPoint + self.mainScreenshotFolder + self.currentRecordingFolder)

        else:
            if not self.mainScreenshotFolder[1:] in os.listdir("/"):
                os.mkdir(self.mainScreenshotFolder)
            
            self.currentRecordingFolder = "/" + str(len(os.listdir(self.mainScreenshotFolder)))
            os.mkdir(self.mainScreenshotFolder + self.currentRecordingFolder)

        if SDavailable:
            os.umount(self.sdMountPoint)
            SD.deinit()
            self.SDcs(1)


    def write_cmd(self, cmd):
        self.cs(1)
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([cmd]))
        self.cs(1)

    def write_data(self, buf):
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(bytearray([buf]))
        self.cs(1)

    def init_display(self):
        """Initialize display"""  
        self.rst(1)
        self.rst(0)
        self.rst(1)
        
        self.write_cmd(0x36)
        self.write_data(0x70)

        self.write_cmd(0x3A) 
        self.write_data(0x05)

        self.write_cmd(0xB2)
        self.write_data(0x0C)
        self.write_data(0x0C)
        self.write_data(0x00)
        self.write_data(0x33)
        self.write_data(0x33)

        self.write_cmd(0xB7)
        self.write_data(0x35) 

        self.write_cmd(0xBB)
        self.write_data(0x19)

        self.write_cmd(0xC0)
        self.write_data(0x2C)

        self.write_cmd(0xC2)
        self.write_data(0x01)

        self.write_cmd(0xC3)
        self.write_data(0x12)   

        self.write_cmd(0xC4)
        self.write_data(0x20)

        self.write_cmd(0xC6)
        self.write_data(0x0F) 

        self.write_cmd(0xD0)
        self.write_data(0xA4)
        self.write_data(0xA1)

        self.write_cmd(0xE0)
        self.write_data(0xD0)
        self.write_data(0x04)
        self.write_data(0x0D)
        self.write_data(0x11)
        self.write_data(0x13)
        self.write_data(0x2B)
        self.write_data(0x3F)
        self.write_data(0x54)
        self.write_data(0x4C)
        self.write_data(0x18)
        self.write_data(0x0D)
        self.write_data(0x0B)
        self.write_data(0x1F)
        self.write_data(0x23)

        self.write_cmd(0xE1)
        self.write_data(0xD0)
        self.write_data(0x04)
        self.write_data(0x0C)
        self.write_data(0x11)
        self.write_data(0x13)
        self.write_data(0x2C)
        self.write_data(0x3F)
        self.write_data(0x44)
        self.write_data(0x51)
        self.write_data(0x2F)
        self.write_data(0x1F)
        self.write_data(0x1F)
        self.write_data(0x20)
        self.write_data(0x23)
        
        self.write_cmd(0x21)

        self.write_cmd(0x11)

        self.write_cmd(0x29)

    def show(self, capture:bool = False, forceMinimumDuplicates=0):
        """ 
        Arguments:
            record (bool): Set to true if you want to capture the current frame into a file on the SD card if it is available.
        """
        self.write_cmd(0x2A)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0xef)
        
        self.write_cmd(0x2B)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0xEF)
        
        self.write_cmd(0x2C)
        
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(self.buffer)
        self.cs(1)

        if (capture or self.enableContinuousRecording) and self.stillRecording:
            self.screenshot("frame.bin", max(forceMinimumDuplicates, (((time.time_ns() - self.lastCaptureTime)//1000000)//self.frameTime_ms)-1))
            self.lastCaptureTime = time.time_ns()
        elif (capture or self.enableContinuousRecording) and not self.stillRecording:
            self.init_save_location()
            self.screenshot("frame.bin")
            self.stillRecording = True
            self.lastCaptureTime = time.time_ns()
        else:
            self.stillRecording = False

    def screenshot(self, fileName, duplicateCount = 0):
        """ 
        Save the current display buffer to a .bin file.
        Arguments:
            filename (str): The name of the file to save the screenshot to.
        """
        gc.collect()

        try:
            SD = SDCard(SPI(0, 125_000_000, sck=Pin(SD_CLK),mosi=Pin(SD_MOSI),miso=Pin(SD_MISO)), self.SDcs, 125_000_000)
            os.mount(SD, self.sdMountPoint)
            SDavailable = True
        except OSError:
            SDavailable = False

        if SDavailable:        
            prefix = len(os.listdir(self.sdMountPoint + self.mainScreenshotFolder + self.currentRecordingFolder))
        else:
            prefix = len(os.listdir(self.mainScreenshotFolder + self.currentRecordingFolder))

        lastUpdatedFramePath = self.sdMountPoint*SDavailable + self.mainScreenshotFolder + self.currentRecordingFolder + "/" + "0"*(4-len(str(prefix))) + str(prefix) + fileName

        print(f"Saving: {lastUpdatedFramePath}")
        with open(lastUpdatedFramePath, 'xb') as f:
            f.write(self.buffer)
            f.close()

        for i in range(duplicateCount):
            prefix += 1
            copyFilePath = self.sdMountPoint*SDavailable + self.mainScreenshotFolder + self.currentRecordingFolder + "/" + "0"*(4-len(str(prefix))) + str(prefix) + fileName
            print(f"Copy: {copyFilePath}")
            with open(copyFilePath, 'xb') as f:
                f.write(self.buffer)
                f.close()

        
        if SDavailable:
            os.umount(self.sdMountPoint)
            SD.deinit()
            self.SDcs(1)

    
    def blit_image_file(self, filePath:str, x:int, y:int, width:int, height:int, memLimit:int = 1000):
        """ 
        This function was added in order to solve problems with insufficient free memory space while loading big images from files.\n
        It blits an image to the image buffer while it limits memory usage according to the *memLimit* argument.
        Only if it is set too low, it loads the image at least one line of pixels at a time.
        Arguments:
            filePath (str): binary image file encoded in the RGB565 format.
            x (int): x coordinate of the image
            y (int): y coordinate of the image
            width (int): width of the image
            height (int): height of the image
            memLimit (int): maximum amount of bytes of memory used to load the image
        """        
        fileSize = os.stat(filePath)
        fileSize = fileSize[6]

        if fileSize == ((width*height*2)+8):
            blockOffset = 8
        else:
            blockOffset = 0
        
        blockSize = max(width, (memLimit//(width*2))*width)
        blockCount = fileSize//(blockSize*2) + min(1, (fileSize-blockOffset)%(blockSize*2))
        # *2 is in the calculation, because each pixel occupies two bytes

        with open(filePath, "rb") as imageFile:
            if blockOffset > 0:
                imageFile.seek(blockOffset)
            
            for block in range(blockCount):
                if not ((block+1)*blockSize*2)>(fileSize-blockOffset):
                    imagePart = bytearray(imageFile.read(int(blockSize*2)))
                    self.blit(framebuf.FrameBuffer(imagePart, width, blockSize//width, framebuf.RGB565), x, y+(block*(blockSize//width)))
                else:
                    imagePartSize = (fileSize-blockOffset) - blockSize*2*block
                    imagePart = bytearray(imageFile.read(imagePartSize))
                    self.blit(framebuf.FrameBuffer(imagePart, width, imagePartSize//2//width, framebuf.RGB565), x, y+(block*(blockSize//width)))
              

            imageFile.close()

    @staticmethod
    def color(R:int,G:int,B:int):
        """ 
        Converts the 24-bit color format to the 16-bit color format supported by the display.
        """
        # Convert RGB888 to RGB565 by scaling
        r5 = (R * 31) // 255           # 5‑bit red
        g6 = (G * 63) // 255           # 6‑bit green
        b5 = (B * 31) // 255           # 5‑bit blue

        # Pack into 16 bits (2 bytes): |RRRRRGGG|GGGBBBBB|
        convertedColor = (r5 << 11) | (g6 << 5) | b5

        # Switch the two bytes around to circumvent color handling bug in framebuf library
        return ((convertedColor & 0x00ff) << 8) | ((convertedColor & 0xff00)>>8)
    
    def brightness(self, brightness:float = -1.0) -> float:
        """ 
        Gets or sets the brightness of the display.
        Arguments:
             brightness (float): The brightness (in %) that the display should be set to.
                Value of this argument must be between 0 (exclusive) and 100 (inclusive), otherwise it is automatically
                set to 100 if the value is too large and not changed if the value is too small.
        Returns:
            float: The current brightness of the display in %
        """
        if brightness == -1.0:
            return self.currentBrightness

        try:
            brightness = float(brightness)
        except ValueError:
            raise ValueError
        if brightness <= 0.0:
            brightness = self.currentBrightness
        if brightness > 100.0:
            brightness = 100.0

        self.currentBrightness = brightness

        pwm = PWM(Pin(BL))
        pwm.freq(1000)
        pwm.duty_u16(min(int(65535*brightness/100), 65535)) # max 65535
        return self.currentBrightness

