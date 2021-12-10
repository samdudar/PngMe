# A program that encodes and decodes a message in an image using steganography.
# The user is prompted to write a message, input a file path to an image, then 
# that message (if it fits) is written into image's pixels, specifically using 
# the least significant bit of an RGB pixel (the blue pixel); the image is then 
# decoded and the message is printed for the user to read (stdout). I chose PNG 
# as the default output image format because it is lossless in order to insure 
# message integrity.
#
# Image data is handled using Pillow:
# https://pillow.readthedocs.io/en/stable/
# 
# To install Pillow:
# 'python3 -m pip install --upgrade pip'
# 'python3 -m pip install --upgrade Pillow'
#
# To run:
# 'python3 pngme.py'
#
# @author Sam Dudar, 2021

from PIL import Image

def get_message() -> str:
# Get user input
    return input('Your message to encode: ')

def bin_length(message: str) -> int:
# Returns total bit length of message
# 8 bits per letter, plus 1 bit for coda (NUL symbol for end of message)
    return 8*(len(message) + 1)

def is_image_bigger_than_message(img: Image, message: str) -> bool:
    return img.width*img.height >= bin_length(message)

def area(img: Image) -> int:
# Returns area of image
    return img.width*img.height

def bin_repr_deci(int_deci: int, number_of_figures: int) -> str:
    # Binary representation of a decimal number, set precisely number_of_figures in length
    # Padded with leading zeroes to fit to number_of_figures length
    x = format(int_deci, 'b')
    if len(x) < number_of_figures:
        for i in range(0, number_of_figures - len(x)):
            x = '0' + x
    return x

def cat_elements(iter) -> str:
# Returns concatenated elements of interable
    l = ""
    for i in iter:
        l = l + i
    return l

def to_bin_repr(message: str) -> str:
    # Returns list of binary representations of each char in message
    x = []
    for c in message:
        x.append(bin_repr_deci(ord(c), 8))
    return cat_elements(x)

def encode_message_in_image(bin_message: str, im: Image):
# Observe the following characteristic of an image:
# 1. Given L = len(message), w = width, h = height,
#   message mapped onto image (w,h) fills all points,
#   from (0,0) to (L%w,L//w)

# 2. For position (x,y) in pixel data of image, an index in message
#   is given at (y*w + x)

    if bin_message[-8] != 8*'0':
        bin_message += 8*'0'
    # ensure coda is added
    
    L = len(bin_message)
    w = im.width
    h = im.height
    x = y = 0
    while (x,y) != (L%w, L//w):
        r = im.getpixel((x,y))[0]
        g = im.getpixel((x,y))[1]
        b = im.getpixel((x,y))[2]
        a = im.getpixel((x,y))[3]
        # get all pixel data
        # pixel data is at point (x,y)

        message_index = bin_message[y*w + x]
        # index in message is (y*w + x)
        
        # set bits into pixels here
        if int(message_index) == 0 and b % 2 == 1:
            im.putpixel((x,y), (r, g, b-1, a))
        elif int(message_index) == 1 and b % 2 == 0:
            im.putpixel((x,y), (r, g, b+1, a))
        x += 1
        if x % w == 0:
            y += 1
            x = 0

def save_encoded_image(image: Image):
# Save image as PNG
    filename = ((image.filename).split(sep='.'))[0]
    image.save(filename + '_encoded.png')

def all_blue(im: Image) -> list:
# Return all blue pixel value information
    blues = []
    w = im.width
    h = im.height
    for y in range(0,h):
        for x in range(0,w):
            blues.append(im.getpixel((x,y))[2])
    return blues

def blue_to_bin(all_blues: list) -> list:
# Return the 8-bit values within the list of raw all_blues from an image.
# Finding the NUL coda will stop the conversion of int to bin.
    bin_vals = []
    cur = ""
    for i in range(0,len(all_blues)):
        cur += str(all_blues[i]%2)
        if len(cur) == 8:
            bin_vals.append(cur)
            if cur == 8*'0':
                bin_vals.pop()
                return bin_vals
            cur = ""
    return bin_vals

def bin_to_chr(bin_str: str):
# Returns the ASCII character equivalent of a binary string
    return chr(int(('0b'+ bin_str),2))

def print_message(encoded_message_list):
    s = ''
    for i in encoded_message_list:
        s += bin_to_chr(i)
    print(s)

def main():
    raw_input = get_message()

    image_orig_path = input("Path to image: ")
    
    print("Your message needs an image of at least " + str((len(raw_input) + 1)*8) + ' pixels for it to fit.')

    image = Image.open(image_orig_path)

    print('Your image is ' + str(image.width) + 'x' + str(image.height) + ' or ' + str(area(image)) + ' pixels.')

    can_fit = is_image_bigger_than_message(image, raw_input)

    print('Message can fit in this image? ' + str(can_fit))

    if can_fit:

        bin_message =  to_bin_repr(raw_input)

        print('Your message is represented in binary as this: \n' + bin_message)

        print('Now encoding into image...')

        encode_message_in_image(bin_message, image)

        print('Message encoded.')

        encoded_filename = ((image.filename).split(sep='.'))[0] + '_encoded.png'

        print('Saving message as ' + encoded_filename + ' in default directory...')
        save_encoded_image(image)
        print('Encoded image saved')
        print('Attempting to read image for message...')

        encoded_image = Image.open(encoded_filename)

        print('Read image.')

        print('Extracting pixel information...')
        blues = all_blue(encoded_image)

        print('Pixel information extracted.')

        print('Decoding message in pixels...')

        blue_as_bin = blue_to_bin(blues)

        print('Your decoded message: ')
        print_message(blue_as_bin)

    else:
        print('Please write a smaller message or use a bigger picture')

if __name__ == "__main__":
    main()