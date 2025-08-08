# About this project
This is a complete overhaul of a project I started in my free time. This means that I have large parts of the code already written, but I decided to completely restructure the code by starting over in order to make it much more expandable and actually worthy of publishing on GitHub.
My goal is to make a toolset that allows for creating games and other GUI applications for Raspberry Pi Pico equipped with a display.

# How to run
1. Install MicroPython on your Pi Pico Board: \[Credit: [raspberrypi.com](https://www.raspberrypi.com/documentation/microcontrollers/micropython.html)\]
[![MicroPython tutorial](https://raw.githubusercontent.com/Martix2222/GamePico/refs/heads/master/.original%20assets/MicroPython%20tutorial%20thumb%20-%20cropped.svg)](https://www.raspberrypi.com/documentation/microcontrollers/images/MicroPython.webm)
2. Upload all files and folders that do not start with a "." from this repository to the Pico. (This includes all assets!)
3. Run main.py or restart the Pico and let it run automatically.


## Compatibility
This project is currently compatible only with the original raspberry Pi Pico, Pico 2 and Pico 2W. Because of RAM size restraints the project is currently incompatible with the raspberry Pi Pico W. It is possible to run it on raspberry Pi Pico W by flashing it with firmware of the non-W version because that frees up some RAM normally used by the wireless driver. However, I do not guarantee that this configuration will be stable.

## Features
Currently I focus on making this project fully compatible with Raspberry Pi Pico equipped with the [Pico-LCD-1.3](https://www.waveshare.com/product/raspberry-pi/boards-kits/pico-lcd-1.3.htm) display from Waveshare.
There is also support for the [Pico-UPS-A](https://www.waveshare.com/pico-ups-a.htm) module from Waveshare with integration into the main menus.

## Recommended hardware
1. [Raspberry Pi Pico 2 W](https://www.raspberrypi.com/products/raspberry-pi-pico-2/?variant=pico-2-w) \[Required\]
2. [1.3inch LCD Display Module for Raspberry Pi Pico](https://www.waveshare.com/product/raspberry-pi/boards-kits/pico-lcd-1.3.htm) \[Required\]
3. [UPS Module for Raspberry Pi Pico](https://www.waveshare.com/product/raspberry-pi/boards-kits/pico-ups-a.htm?___SID=U)
4. [Micro SD Storage Expansion Board](https://www.aliexpress.com/item/1005005591145849.html) (From Aliexpress, because that's where I found it the cheapest)
# Credits
**_NOTE:_** Most of the libraries credited have been modified in order to function properly with this project.
## Reference code for module drivers
I used this code largely unmodified or with some minor changes or feature additions
- [Pico-UPS-A](https://www.waveshare.com/wiki/Pico-UPS-A#Demo_codes)
- [Pico-LCD-1.3](https://www.waveshare.com/wiki/Pico-LCD-1.3#Demo_Download)
    - I also used a color conversion function written by Tony Goodhew for [thepihut.com](https://thepihut.com/blogs/raspberry-pi-tutorials/coding-colour-with-micropython-on-raspberry-pi-pico-displays)
- [sdcard](https://github.com/micropython/micropython-lib/blob/master/micropython/drivers/storage/sdcard/sdcard.py)
    - MicroPython driver for SD cards using SPI bus. [Original repository](https://github.com/micropython/micropython-lib/tree/master)

## Other libraries used
- [FONTS](https://thepihut.com/blogs/raspberry-pi-tutorials/advanced-text-with-micropython-on-raspberry-pi-pico-displays?)
    - Again by Tony Goodhew for [thepihut.com](https://thepihut.com)

---
---

### Disclaimers
- This is an independent project made for the Raspberry Pi Pico but it is in no way affiliated with the official Raspberry Pi Ltd.
- And about AI use in this project; Generally I try to avoid AI as much as possible. Especially AI art. **All assets used in this project are either mine or the author will be credited appropriately.** And when it comes to code, the original code was written with some help from GitHub Copilot (before I started this rewrite project) and since I'm still learning sometimes desperate times require desperate solutions which sometimes do contain asking a chatbot how to accomplish a specific thing. But I try to minimize even those uses.