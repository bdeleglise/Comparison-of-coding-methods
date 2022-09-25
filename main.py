import sys

import encode

#path access path of the results files
RESULT_TEXT_FILE_PATH = 'result_text.csv'
RESULT_IMAGE_FILE_PATH = 'result_image.csv'

"""
To run encoding in the terminal :
python main.py TYPE MODE ALGO FILE [DEBUG]
TYPE is the type of the file -i for an image or -t for a text
MODE this is the reading option: 
for images -RGB to encode the 3 axes or -GRAY to convert the image to grayscale
for texts -Unicode to consider that the symbols are encoded on 1 byte -M to simply read the message and -RAND to generate a random message
ALGO specifies the algo to use:
-ALL for all
-AR for arithmetic 
-PRE for predictive
-PREAR for predictive and arithmetic in sequence
FILE gives the file studied and for a random generation the size of it
DEBUG optional and enables debugging
"""
def main():
    #Test arguments
    if len(sys.argv) < 5:
        print('Error, not enough parameters')
        exit(1)

    debug = False
    if len(sys.argv) == 6 and sys.argv[5] == '-d':
        debug = True

    if sys.argv[1] == '-i':
        print('encode an image')
        encode.encode_image(sys.argv[2], sys.argv[3], sys.argv[4], RESULT_IMAGE_FILE_PATH, debug)
    elif sys.argv[1] == '-t':
        print('encode a message')
        encode.encode_text(sys.argv[2], sys.argv[3], sys.argv[4], RESULT_TEXT_FILE_PATH, debug)
    else:
        print('Wrong first parameter, it should be -i or -t')
        exit(1)


if __name__ == '__main__':
    main()

