from machine import Pin,SPI,PWM
import framebuf
import time
import os
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
keyX = Pin(19 ,Pin.IN,Pin.PULL_UP)
keyY = Pin(21 ,Pin.IN,Pin.PULL_UP)

up = Pin(2,Pin.IN,Pin.PULL_UP)
down = Pin(18,Pin.IN,Pin.PULL_UP)
left = Pin(16,Pin.IN,Pin.PULL_UP)
right = Pin(20,Pin.IN,Pin.PULL_UP)
ctrl = Pin(3,Pin.IN,Pin.PULL_UP)

class Was_Pressed():
    def __init__(self):
        self.registeredPresses = {}
        # self.lastPressTime = {}
        self.holdRepetitionDelay = 0.5  # seconds
        self.holdRepetitionFrequency = 0.2  # seconds


        # Initialize key press handling
        keyA.irq(trigger=Pin.IRQ_FALLING, handler=self.press_handler)
        keyB.irq(trigger=Pin.IRQ_FALLING, handler=self.press_handler)
        keyX.irq(trigger=Pin.IRQ_FALLING, handler=self.press_handler)
        keyY.irq(trigger=Pin.IRQ_FALLING, handler=self.press_handler)
        
        up.irq(trigger=Pin.IRQ_FALLING, handler=self.press_handler)
        down.irq(trigger=Pin.IRQ_FALLING, handler=self.press_handler)
        left.irq(trigger=Pin.IRQ_FALLING, handler=self.press_handler)
        right.irq(trigger=Pin.IRQ_FALLING, handler=self.press_handler)
        ctrl.irq(trigger=Pin.IRQ_FALLING, handler=self.press_handler)


    def press_handler(self, pin:Pin):
        if pin in self.registeredPresses.keys():
            self.registeredPresses[pin] += 1
        else:
            self.registeredPresses[pin] = 1


    def was_pressed(self, pin:Pin, subtract:bool = True, clearQue:bool = False):
        """
        Checks if a button was pressed.
        Arguments:
            pin (int): The pin number of the button to check.
            subtract (bool): If True, the count of presses in the queue will be decremented by 1 after checking. \n
                             If False, the count will not be changed.
            clearQue (bool): If True, the count of presses in the queue will be set to 0 after checking. \n
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
        
        self.cs = Pin(CS,Pin.OUT)
        self.rst = Pin(RST,Pin.OUT)
        
        self.cs(1)
        # self.spi = SPI(1)
        # self.spi = SPI(1,1000_000)
        self.spi = SPI(1,150_000_000,polarity=0, phase=0,sck=Pin(SCK),mosi=Pin(MOSI),miso=None)
        self.dc = Pin(DC,Pin.OUT)
        self.dc(1)
        self.buffer = bytearray(self.height * self.width * 2)
        super().__init__(self.buffer, self.width, self.height, framebuf.RGB565)
        self.init_display()
        
        self.red   =   0x07E0
        self.green =   0x001f
        self.blue  =   0xf800
        self.white =   0xffff

        self.SDcs = Pin(SD_CS)
        self.SDcs(1)

        self.sdMountPoint = "/sd"
        self.mainScreenshotFolder = "/screenshots"
        self.currentRecordingFolder = "/1"
        self.stillRecording = False

    def init_save_location(self):
        try:
            SD = SDCard(SPI(0, 150_000_000, sck=Pin(SD_CLK),mosi=Pin(SD_MOSI),miso=Pin(SD_MISO)), self.SDcs, 150_000_000)
            os.mount(SD, self.sdMountPoint)
            SDavailable = True
        except OSError:
            SDavailable = False


        if SDavailable:
            if not self.mainScreenshotFolder[1:] in os.listdir(self.sdMountPoint):
                os.mkdir(self.sdMountPoint + self.mainScreenshotFolder + self.currentRecordingFolder)
            self.currentRecordingFolder = "/" + str(len(os.listdir(self.sdMountPoint + self.mainScreenshotFolder)))
        else:
            if not self.mainScreenshotFolder[1:] in os.listdir("/"):
                os.mkdir(self.mainScreenshotFolder)
            self.currentRecordingFolder = "/" + str(len(os.listdir(self.mainScreenshotFolder)))


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

    def show(self, record:bool = False):
        """ 
        Arguments:
            record (bool): Set to true if you want to capture the current frame into a file on the SD card if it is available.
        """

        if record and self.stillRecording:
            self.screenshot("frame.bin")
        elif record and not self.stillRecording:
            self.init_save_location()
            self.screenshot("frame.bin")
        else:
            self.stillRecording = False

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

    def screenshot(self, filename):
        """ 
        Save the current display buffer to a .bin file.
        Arguments:
            filename (str): The name of the file to save the screenshot to.
        """

        try:
            SD = SDCard(SPI(0, 150_000_000, sck=Pin(SD_CLK),mosi=Pin(SD_MOSI),miso=Pin(SD_MISO)), self.SDcs, 150_000_000)
            os.mount(SD, self.sdMountPoint)
            SDavailable = True
        except OSError:
            SDavailable = False

        if SDavailable:        
            prefix = str(len(os.listdir(self.sdMountPoint + self.mainScreenshotFolder + self.currentRecordingFolder)))
        else:
            prefix = str(len(os.listdir(self.mainScreenshotFolder)))


        with open(self.mainScreenshotFolder + "0"*(4-len(prefix)) + prefix + filename, 'wb') as f:
            f.write(self.buffer)
            f.close()


        os.umount(self.sdMountPoint)
        SD.deinit()
        self.SDcs(1)

    @staticmethod
    def color(R:int,G:int,B:int): # Convert RGB888 to RGB565
        """ 
        Converts the 24-bit color format to the 16-bit color format supported by the display.
        """
        return (((G&0b00011100)<<3) + ((B&0b11111000)>>3)<<8) + (R&0b11111000) + ((G&0b11100000)>>5)
    
    @staticmethod
    def set_brightness(brightness:float):
        """ 
        Set the brightness of the display.
        Arguments:
             brightness (float): The brightness (in %) that the display should be set to.
                Value of this argument should be between 0 and 100, otherwise it is automatically
                set to 100 if the value is too large and to 1 if the value is too small.
        """
        try:
            brightness = float(brightness)
        except ValueError:
            return(ValueError)
        if brightness < 0.0:
            brightness = 1.0
        if brightness > 100.0:
            brightness = 100.0



        pwm = PWM(Pin(BL))
        pwm.freq(1000)
        pwm.duty_u16(min(int(65535*brightness/100), 65535)) # max 65535

