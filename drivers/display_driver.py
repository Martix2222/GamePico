from machine import Pin,SPI,PWM
import framebuf
import time
import os
import gc
from drivers.sdcard_driver import SDCard
import deflate
import sys


# Display pins
BL = const(13)
DC = const(8)
RST = const(12)
MOSI = const(11)
SCK = const(10)
CS = const(9)

# SD reader pins
SD_CS = const(5)
SD_MISO = const(4)
SD_CLK = const(6)
SD_MOSI = const(7)

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

        self.SDcs = Pin(SD_CS, Pin.OUT)
        
        self.cs(1)
        self.spi = SPI(1)
        self.spi = SPI(1,1000_000)
        self.spi = SPI(1,62_500_000,polarity=0, phase=0,sck=Pin(SCK),mosi=Pin(MOSI),miso=None)
        self.dc = Pin(DC,Pin.OUT)
        self.dc(1)

        gc.collect()
        self.buffer = bytearray(self.height * self.width * 2)
        super().__init__(self.buffer, self.width, self.height, framebuf.RGB565)
        self.init_display()

        self.currentBrightness = 100.0
        self.brightness(self.currentBrightness)

        self.enableRecording = False
        
        self.enableRecordingCompression = True
        self.compressionWbits = 5

        self.globalFrameRateLimit = 20
        self.lastFrameDuration = 1000 // self.globalFrameRateLimit

        self.lastFrameTime = time.ticks_us()

        self.sdMountPoint = "/sd"
        self.screenshotFolder = "/screenshots"
        self.recordingFolder = "/recordings"
        self.stillRecording = False

        self.SDavailable = self.check_SD_availability()

        self.enableUSBstreaming = False


    def init_SD(self):
        """ Returns an initialized SDCard object. """
        return SDCard(SPI(0, 1_000_000, sck=Pin(SD_CLK), mosi=Pin(SD_MOSI), miso=Pin(SD_MISO)), self.SDcs, 12_500_000)


    def mount_SD(self, mount:bool):
        """ 
        Arguments:
            mount (bool): If set to True, the SD card is mounted at the sdMountPoint location, else, the SD card is unmounted.
        """
        if mount:
            self.SDcs(0)
            self.SD = self.init_SD()
            os.mount(self.SD, self.sdMountPoint)
        else:
            os.umount(self.sdMountPoint)
            self.SD.deinit()
            self.SDcs(1)


    def check_SD_availability(self):
        try:
            # Check whether an SD card is available by temporarily mounting it.
            self.mount_SD(True)
            self.mount_SD(False)
            return True
        except OSError:
            return False


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

    def show(self, screenshot:bool = False, minimumFrameTime_ms:int = -1):
        """ 
        Arguments:
            screenshot (bool): Set to true if you want to save the current frame as a screenshot into a file on the SD card if it is available.
        """
        if minimumFrameTime_ms == -1:
            minimumFrameTime_ms = 1000 // self.globalFrameRateLimit
        if self.lastFrameTime == -1:
            self.lastFrameTime = time.ticks_us()

        startTime = time.ticks_us()

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

        if self.enableUSBstreaming:
            packetCount = 16

            packetNumber = 0

            command = sys.stdin.readline().strip()
            if command == "ready":
                sys.stdin.buffer.write(bytearray(2))
                while packetNumber < packetCount:
                    command = sys.stdin.readline().strip()
                    if command == "ready":
                        pass
                    elif command == "continue":
                        sys.stdout.buffer.write(self.buffer[packetNumber*self.width*self.height*2//packetCount:packetNumber*self.width*self.height*2//packetCount+self.width*self.height*2//packetCount])
                        packetNumber += 1
                    elif command == "retry":
                        sys.stdout.buffer.write(self.buffer[packetNumber*self.width*self.height*2//packetCount:packetNumber*self.width*self.height*2//packetCount+self.width*self.height*2//packetCount])
                    
            while not sys.stdin.readline().strip() == "end":
                time.sleep_ms(1)

        time.sleep_ms(1)

        if screenshot:
            self.screenshot("screenshot")
        if self.enableRecording:
            self.record("recording", max(self.lastFrameDuration, time.ticks_diff(time.ticks_ms(), self.lastFrameTime)))
        elif self.stillRecording:
            self.record("recording", max(self.lastFrameDuration, time.ticks_diff(time.ticks_ms(), self.lastFrameTime)))
        self.lastFrameDuration = minimumFrameTime_ms

        time.sleep_us(max(0, minimumFrameTime_ms*1000-time.ticks_diff(time.ticks_us(), self.lastFrameTime)))
        self.lastFrameTime = time.ticks_us()


    @staticmethod
    def create_binFrame_header(width:int, height:int, id:int, frameTime:int, gzip:bool, gzipWbits:int=0):
        # The currently implemented binFrame version is V1
        version:int = 1

        header = bytearray(32)
        header[0:2] = version.to_bytes(2, "big")
        header[2:10] = width.to_bytes(4, "big") + height.to_bytes(4, "big")
        header[10:14] = id.to_bytes(4, "big")
        header[14:18] = frameTime.to_bytes(4, "big")
        header[18] = header[18] | (gzip << 0) # Set the data compression flag
        if gzip and gzipWbits:
            header[19] = gzipWbits
        elif gzip:
            raise ValueError("The gzipWbits argument must be set if gzip is True")
        return header
    

    def write_frame_time_to_file(self,  path:str , frameTime:int):
        with open(path, "r+b") as f:
            f.seek(14)
            f.write(frameTime.to_bytes(4, "big"))
    

    def screenshot(self, fileName:str):
        """ 
        Save the current display buffer to a .binFrame file.
        Arguments:
            filename (str): The name of the file of the screenshot.
        """
        fileFormat = ".binFrame"
        gc.collect()

        if self.SDavailable:
            self.mount_SD(True)      
            targetFolder = self.sdMountPoint + self.screenshotFolder
        else:
            targetFolder = self.screenshotFolder

        self.init_file_destination(targetFolder)
   
        prefix = len(os.listdir(targetFolder))

        screenshotName = "0"*(4-len(str(prefix))) + str(prefix) + fileName + fileFormat
        
        # make sure that a screenshot with the same name does not already exist
        while screenshotName in os.listdir(targetFolder):
            prefix += 1
            screenshotName = "0"*(4-len(str(prefix))) + str(prefix) + fileName + fileFormat
        
        screenshotPath = targetFolder + "/" + screenshotName
        # print(f"Saving: {screenshotPath}")

        with open(screenshotPath, 'xb') as f:
            if self.enableRecordingCompression:
                f.write(self.create_binFrame_header(self.width, self.height, prefix, 0, True, self.compressionWbits))
                d = deflate.DeflateIO(f, deflate.GZIP, self.compressionWbits)
                try:
                    d.write(self.buffer) # type: ignore
                except:
                    self.enableRecordingCompression = False
                    f.seek(0)
                    f.write(self.create_binFrame_header(self.width, self.height, prefix, 0, False))
                    f.write(self.buffer)
                finally:
                    d.close()
            else:
                f.seek(0)
                f.write(self.create_binFrame_header(self.width, self.height, prefix, 0, False))
                f.write(self.buffer)
            f.close()

        if self.SDavailable:
            self.mount_SD(False)


    def init_file_destination(self, path:str):
        directories:list[str] = path.split("/")
        if directories[0] == "":
            directories.pop(0)

        for depth in range(len(directories)):
            try:
                if not directories[depth] in os.listdir("/" +  "/".join(directories[:depth])):
                    os.mkdir("/" +  "/".join(directories[:depth+1]))
            except OSError:
                pass


    def record(self, folderName:str, lastFrameDuration:int):
        """ 
        Save the current display buffer to a .binFrame file.
        Arguments:
            folderName (str): The name of the folder that the frames of the recording will be saved to.
            lastFrameDuration (int): The duration in ms of how long was the previous frame displayed for.
        """
        fileFormat = ".binFrame"
        gc.collect()

        if self.SDavailable:
            self.mount_SD(True)      
            targetFolder = self.sdMountPoint + self.recordingFolder
        else:
            targetFolder = self.recordingFolder
        
        self.init_file_destination(targetFolder)

        if not self.stillRecording:
            recordingFolderSuffix = len(os.listdir(targetFolder))
            self.currentRecordingFolder = "/" + folderName + "-" + "0"*(4-len(str(recordingFolderSuffix))) + str(recordingFolderSuffix)

            # make sure that the folder does not already exist
            while self.currentRecordingFolder[1:] in os.listdir(targetFolder):
                recordingFolderSuffix += 1
                self.currentRecordingFolder = "/" + folderName + "-" + "0"*(4-len(str(recordingFolderSuffix))) + str(recordingFolderSuffix)

            os.mkdir(targetFolder + self.currentRecordingFolder)
            self.currentFrameID = 0
            self.stillRecording = True
        else:
            lastFramePath = targetFolder + self.currentRecordingFolder + "/" + "0"*(4-len(str(self.currentFrameID-1))) + str(self.currentFrameID-1) + fileFormat
            self.write_frame_time_to_file(lastFramePath, lastFrameDuration)
            if not self.enableRecording:
                self.stillRecording = False
                return
        
        framePath = targetFolder + self.currentRecordingFolder + "/" + "0"*(4-len(str(self.currentFrameID))) + str(self.currentFrameID) + fileFormat
        # print(f"Saving: {framePath}")

        with open(framePath, 'xb') as f:
            if self.enableRecordingCompression:
                f.write(self.create_binFrame_header(self.width, self.height, self.currentFrameID, 0, True, self.compressionWbits))
                d = deflate.DeflateIO(f, deflate.GZIP, self.compressionWbits)
                try:
                    d.write(self.buffer) # type: ignore
                except:
                    self.enableRecordingCompression = False
                    f.seek(0)
                    f.write(self.create_binFrame_header(self.width, self.height, self.currentFrameID, 0, False))
                    f.write(self.buffer)
                finally:
                    d.close()
            else:
                f.seek(0)
                f.write(self.create_binFrame_header(self.width, self.height, self.currentFrameID, 0, False))
                f.write(self.buffer)
            f.close()

        if self.SDavailable:
            self.mount_SD(False)

        self.currentFrameID += 1


    def read_binFrame_header(self, path) -> dict:
        with open(path, 'rb') as f:
            if int.from_bytes(f.read(2), "big", signed=False) == 1:
                headerData = {}
                headerData["version"] = 1
                headerData["headerLength"] = 32
                headerData["width"] = int.from_bytes(f.read(4), "big", signed=False)
                headerData["height"] = int.from_bytes(f.read(4), "big", signed=False)
                headerData["id"] = int.from_bytes(f.read(4), "big", signed=False)
                headerData["frameTime"] = int.from_bytes(f.read(4), "big", signed=False)
                flagByte = f.read(1)
                headerData["gzip"] = self.is_bit_set(int.from_bytes(flagByte, "big", signed=False), 0)
                headerData["gzip_wbits"] = int.from_bytes(f.read(1), "big", signed=False)
                f.close()
                return headerData
            else:
                f.close()
                raise ValueError("Unsupported file version")
    
    
    @staticmethod
    def is_bit_set(byte: int, bitIndex: int) -> bool:
        return (byte >> bitIndex) & 1 == 1

    
    def blit_image_from_file(self, filePath:str, position:tuple[int, int], dimensions:tuple[int, int]=(0, 0), startingPositionInFile:tuple[int, int]=(0, 0), memLimit:int = 1000):
        """ 
        This function was added in order to solve problems with insufficient free memory space while loading big images from files.\n
        It blits an image to the image buffer while it limits memory usage according to the *memLimit* argument.
        Only if it is set too low, it loads the image at least one line of pixels at a time.
        Arguments:
            filePath (str): binary image file encoded in the RGB565 format.
            position (tuple[int, int]): The position where the image should be drawn on the display.
            dimensions (tuple[int, int]): The dimensions of the image that is drawn on the display.\n
                (Takes priority over the dimensions that may be saved in the .binFrame file, in case it is an asset that contains multiple images as states.)
            startingPositionInFile (tuple[int, int]): In case the file contains a bigger image than is specified by the dimensions parameter,
                this parameter can specify the position of the cutout of the image that will be drawn from the file.
            memLimit (int): Maximum amount of bytes of memory that can be used to draw the image.
        """

        assert startingPositionInFile[0] >= 0 and startingPositionInFile[1] >= 0 and dimensions[0] >= 0 and dimensions[1] >= 0

        if filePath.endswith(".binFrame"):
            header = self.read_binFrame_header(filePath)

            if dimensions == (0, 0):
                dimensions = (header["width"], header["height"])

            width, height = dimensions

            chunkSize = max(width, (memLimit//(width*2))*width) # in pixels
            chunkCount = (width*height)//(chunkSize) + (width*height)%(chunkSize)
            # *2 is in the calculation, because each pixel occupies two bytes

            with open(filePath, "rb") as imageFile:
                imageFile.seek(header["headerLength"])
                imageFile.seek(startingPositionInFile[0]*2+startingPositionInFile[1]*header["width"]*2)

                for chunk in range(chunkCount):
                    imageChunk = bytearray()
                    if width*height*2 >= chunk*width*2:
                        for i in range(chunkSize//width):
                            imageChunk += bytearray(imageFile.read(int(chunkSize*2)))
                            imageFile.seek(header["width"]*2)

                        self.blit(framebuf.FrameBuffer(imageChunk, width, chunkSize//width, framebuf.RGB565), position[0], position[1]+(chunk*(chunkSize//width)))
                    else:
                        for i in range(((width*height*2 - chunk*width*2))//width):
                            imageChunk = bytearray(imageFile.read(int(chunkSize*2)))
                            imageFile.seek(header["width"]*2)
                        self.blit(framebuf.FrameBuffer(imageChunk, width, (len(imageChunk)//2)//width, framebuf.RGB565), position[0], position[1]+(chunk*(chunkSize//width)))           
            
        elif filePath.endswith(".bin"):
            width, height = dimensions
            x, y = position

            try:     
                fileSize = os.stat(filePath)[6]
            except OSError:
                self.fill_rect(x, y, width, height, self.color(255, 0, 0))
                self.text("Image not found:", x, y, 0x0000)
                self.text(filePath, x, y+8, 0x0000)
                return

            # Skip the head data of the image if it is present
            if fileSize == ((width*height*2)+8):
                blockOffset = 8
            else:
                blockOffset = 0
            
            chunkSize = max(width, (memLimit//(width*2))*width)
            chunkCount = fileSize//(chunkSize*2) + min(1, (fileSize-blockOffset)%(chunkSize*2))
            # *2 is in the calculation, because each pixel occupies two bytes

            with open(filePath, "rb") as imageFile:
                if blockOffset > 0:
                    imageFile.seek(blockOffset)
                
                for chunk in range(chunkCount):
                    if not ((chunk+1)*chunkSize*2)>(fileSize-blockOffset):
                        imageChunk = bytearray(imageFile.read(int(chunkSize*2)))
                        self.blit(framebuf.FrameBuffer(imageChunk, width, chunkSize//width, framebuf.RGB565), x, y+(chunk*(chunkSize//width)))
                    else:
                        imagePartSize = (fileSize-blockOffset) - chunkSize*2*chunk
                        imageChunk = bytearray(imageFile.read(imagePartSize))
                        self.blit(framebuf.FrameBuffer(imageChunk, width, imagePartSize//2//width, framebuf.RGB565), x, y+(chunk*(chunkSize//width)))
                

                imageFile.close()

        else:
            raise ValueError(f"{filePath.split(".")[-1]} is an unsupported file format!")
        



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
    
    @staticmethod
    def calculate_luminance(R:int, G:int, B:int):
        """ 
        Calculates and returns the luminance of a given RGB888 color code.
        """
        return 0.2126 * R + 0.7152 * G + 0.0722 * B 
    
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

