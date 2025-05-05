from machine import Pin, SPI, ADC, idle, reset
import os
import sys
import uselect
from time import sleep

# Save this file as ili9341.py https://github.com/rdagger/micropython-ili9341/blob/master/ili9341.py
from ili9341 import Display, color565
# Save this file as xglcd_font.py https://github.com/rdagger/micropython-ili9341/blob/master/xglcd_font.py
from xglcd_font import XglcdFont
screen = {
    'width':	 320,
    'height':	 240,
    }
# Function to set up SPI for TFT display
display_spi = SPI(1, baudrate=30000000,  sck=Pin(18), mosi=Pin(23), miso=Pin(19))
# Set up display
display = Display(display_spi, cs=Pin(5), dc=Pin(2), rst=Pin(4),
                  width=screen['width'], height=screen['height'], rotation=180,bgr = True)
def rgb_to_565(rgb):
    return color565(rgb[2], rgb[1], rgb[0])  # Chuyển RGB → BGR

color = { 
    'red': 		rgb_to_565((255, 0, 0)),
    'green':	rgb_to_565((0, 255, 0)),
    'blue': 	rgb_to_565((0, 0, 255)), 
    'yellow': 	rgb_to_565((255, 255, 0)), 
    'purple': 	rgb_to_565((255, 0, 255)), 
    'cyan': 	rgb_to_565((0, 255, 255)),
    'white': 	rgb_to_565((255, 255, 255)),
    'black': 	rgb_to_565((0, 0, 0)),
    }

def draw_turt(x_coords,y_coords):
    global start_x
    global start_y
    global row_dist
    global col_dist
    map_coords = [x_coords*row_dist + start_y, y_coords*col_dist + start_x]
    
    display.draw_image('images/tutel.raw', map_coords[1]-4, map_coords[0]-4 , 9, 9)

def draw_dot(x_coords, y_coords,r = 3,color = color['yellow']):
    global start_x
    global start_y
    global row_dist
    global col_dist
    map_coords = [x_coords*row_dist + start_y, y_coords*col_dist + start_x]
    
    display.fill_circle(map_coords[1], map_coords[0], r, color)
    return

def draw_overlay(x_coords,y_coords):
    global start_x
    global start_y
    global row_dist
    global col_dist
    map_coords = [x_coords*row_dist + start_y, y_coords*col_dist + start_x]
    
    display.fill_rectangle(map_coords[1]-4 ,map_coords[0]-4 ,9 ,9 ,color['black'])
    display.draw_line(map_coords[1]-9, map_coords[0],
                      map_coords[1]+9, map_coords[0], color['cyan'])
    
    display.draw_line(map_coords[1], map_coords[0]-9,
                      map_coords[1], map_coords[0]+9, color['cyan'])
    

def draw_map_layout(row,col):

    screen_width = 300
    screen_height = 210
    
    global start_x 
    start_x = int(row/4+5)
    global start_y 
    start_y = int(col/4+10)
    display.fill_rectangle(0, 10, 319, 240-20, color['black'])
    
    global row_dist
    row_dist = int(screen_height/(row-1))
    global col_dist 
    col_dist = int(screen_width/(col-1))
    
    end_x = start_x + (col-1) * col_dist
    end_y = start_y + (row-1) * row_dist
    
    for r in range(row):
        display.draw_line(start_x, start_y+r*row_dist,
                          end_x  , start_y+r*row_dist, color['cyan'])
    for c in range(col):
        display.draw_line(start_x+ c*col_dist, start_y,
                          start_x+ c*col_dist, end_y, color['cyan'])
        
def handle_command(command):
    """
    Handle a full command received over serial.
    :param command: (String) the command to handle
    """
    global current_coords
    global old_coords
    if not command:
        return

    print("ESP32 received command:", command)

    if "x= " in command:
        #sys.stdout.buffer.write(b"x recieved\n")
        x = command[3:]
        display.fill_rectangle(55,230,10,8,color['black'])
        display.draw_text(60, 230, x, font, color['red'], color['black'])
        current_coords[0] = int(x)
        
    elif "y= " in command:
        #sys.stdout.buffer.write(b"y recieved\n")
        y = command[3:]
        display.fill_rectangle(155,230,10,8,color['black'])
        display.draw_text(160, 230, y, font, color['blue'], color['black'])
        current_coords[1] = int(y)
        
        draw_overlay(old_coords[0],old_coords[1])
        draw_turt(current_coords[0],current_coords[1])
        draw_overlay(old_coords[0],old_coords[1])
        old_coords = current_coords[:]

    elif "dir= " in command:
        #sys.stdout.buffer.write(b"direction recieved\n")
        direction = int(command[4:])
        x=280
        y=228
        if direction == 0:
            display.draw_image('images/0deg.raw', x, y, 10, 10)
        elif direction == 90:
            display.draw_image('images/90deg.raw', x, y, 20, 20)
        elif direction == 180:
            display.draw_image('images/180deg.raw', x, y, 10, 10)
        else:
            display.draw_image('images/270deg.raw', x, y, 10, 10)
    elif "map= " in command:
        row = int( ( command[5:].split('x') )[0] )
        col = int( ( command[5:].split('x') )[1] )
        draw_map_layout(row,col)
    elif "obs= " in command:
        x_coords = int( ( command[4:].split('x') )[0] )
        y_coords = int( ( command[4:].split('x') )[1] )
        draw_dot(x_coords, y_coords)
    else:
        #sys.stdout.buffer.write(b"error\n")
        return
    
    sleep(0.001)

def readSerial():
    """
    Reads characters from serial input and buffers them until newline.
    :return: full command string when newline is received; None otherwise
    """
    global buffer
    if serialPoll.poll(0):
        char = sys.stdin.read(1)
        if char == "\n":
            command = buffer.strip()
            buffer = ""
            return command
        else:
            buffer += char
    return None

serialPoll = uselect.poll()
serialPoll.register(sys.stdin, uselect.POLLIN)

buffer = ""
current_coords = [0,0]
old_coords = [0,0]
start_x = 0
start_y = 0
row_dist = 0
col_dist = 0

updated_coords = False
try:
    #display.invert()
    display.clear(color['black'])
    font = XglcdFont('fonts/wendy7x8.c', 7, 8)
    display.draw_text(0, 0, 'ESP32 turtle robot amr thinggy for advanced programming', font, color['yellow'], color['black'])
    #draw_turt(200,10)
    
    display.draw_text(50, 230, 'x: ', font, color['red'], color['black'])
    #display.fill_rectangle(60,230,10,8,color['red'])
    display.draw_text(150, 230, 'y: ' , font, color['blue'], color['black'])
    #display.fill_rectangle(160,230,10,8,color['blue'])

    display.draw_text(240, 230, 'direction: ', font, color['green'], color['black'])

#     draw_map_layout(10,10)
#     #draw_dot(1,1,2,color['red'])
#     draw_turt(1,1)
#     draw_overlay(1,1)
#     draw_turt(1,3)
    
    
    while True:
        message = readSerial()
        if message:
            handle_command(message)
    
except Exception as e:
    print('Error occured: ', e)
except KeyboardInterrupt:
    print('Program Interrupted by the user')        
    display.cleanup()
