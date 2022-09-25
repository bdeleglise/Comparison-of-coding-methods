"""
Parts of this code are taken from and inspired by the code of
https://github.com/gabilodeau/INF8770/blob/master/Codage%20arithmetique.ipynb
https://github.com/nayuki/Reference-arithmetic-coding
https://github.com/ahmedfgad/ArithmeticEncodingPython
"""
import numpy
import matplotlib.pyplot as py
import arithmeticcoding


# Allows to do an arithmetic coding on a text
def text_arithmetic_coding(message, debug):
    ascii_message = []

    for i in range(0, len(message)):
        ascii_message.append(ord(message[i]))

    # Parameters to change depending on message size
    min_symb = 0
    max_symb = max(ascii_message)

    # Read input file once to compute symbol frequencies
    freqs = get_frequencies(ascii_message, min_symb, max_symb)

    if debug is True:
        print(freqs)

    freqs_length = write_frequencies(freqs)
    binary_code = compress(freqs, ascii_message, min_symb)

    if debug is True:
        print("The binary code is: {binary_code}".format(binary_code=binary_code))

    return freqs, freqs_length, binary_code, min_symb


# Allows to do an arithmetic coding on a message composed of a sequence of errors
def error_arithmetic_coding(message, debug):
    ascii_message = []

    for i in range(0, len(message)):
        if isinstance(message[i], int) or isinstance(message[i], numpy.int32):
            ascii_message.append(message[i])
        else:
            ascii_message.append(ord(message[i]))

    # Paramètre à changer selon l'encodage
    min_symb = min(ascii_message)
    max_symb = max(ascii_message)

    neg_value = False
    # the minimum of the frequency table is 0, so we add an offset to add the negative numbers
    if min_symb < 0:
        neg_value = True
        max_symb += abs(min_symb)

    freqs = get_frequencies(ascii_message, min_symb, max_symb, neg_value)

    if debug is True:
        print(freqs)

    freqs_length = write_frequencies(freqs)
    binary_code = compress(freqs, ascii_message, min_symb, neg_value)

    if debug is True:
        print("The binary code is: {binary_code}".format(binary_code=binary_code))
    return freqs, freqs_length, binary_code, min_symb


# Allows to do an arithmetic coding on an image
def image_arithmetic_coding(image, debug):
    image = image.astype('uint8')
    message = image.flatten()

    # The value of a pixel on an axis is in 8bits
    min_symb = 0
    max_symb = 255

    freqs = get_frequencies(message, min_symb, max_symb)
    if debug is True:
        print(freqs)

    freqs_length = write_frequencies(freqs)
    binary_code = compress(freqs, message, min_symb)

    if debug is True:
        print("The binary code is: {binary_code}".format(binary_code=binary_code))
    return freqs, freqs_length, binary_code, min_symb


# Allows to execute the arithmetic algo
# Inspired by https://github.com/nayuki/Reference-arithmetic-coding
def compress(freqs, message, min_symb, neg_value=False):
    enc = arithmeticcoding.ArithmeticEncoder(32)
    for i in range(0, len(message)):
        if neg_value:
            symbol = message[i] + abs(min_symb)
        else:
            symbol = message[i] - min_symb
        enc.write(freqs, symbol)
    enc.finish()  # Flush remaining code bits
    return enc.binary_code


# Allows to calculate the length to save the frequencies table
# We need 8 bits to encode the symbol and 32 to encode an int
def write_frequencies(freqs):
    nb_symbols = 0
    for i in range(0, len(freqs.frequencies)):
        if freqs.get(i) > 0:
            nb_symbols += 1
    return nb_symbols * 40


# Allows to calculate frequencies table
# Inspired by https://github.com/nayuki/Reference-arithmetic-coding
def get_frequencies(message, min_symb, max_symb, neg_value=False):
    freqs = arithmeticcoding.SimpleFrequencyTable([0] * (max_symb - min_symb + 1))
    for i in range(0, len(message)):
        if neg_value:
            freqs.increment(message[i] + abs(min_symb))
        else:
            freqs.increment(message[i] - min_symb)
    return freqs


# Allows to decode a text encoded with the arithmetic decoding to text that the result is correct
def text_arithmetic_decoding(message, binary_code, freqs, min_symb, as_string, debug=False):
    dec = arithmeticcoding.ArithmeticDecoder(32, binary_code)
    decoded_msg = []

    for i in range(0, len(message)):
        symbol = dec.read(freqs) + min_symb
        decoded_msg.append(chr(symbol))

    if as_string:
        decoded_msg = "".join(decoded_msg)

    if debug is True:
        print("Decoded Message: {msg}".format(msg=decoded_msg))

    return message == decoded_msg


# Allows to decode a list of error encoded with the arithmetic decoding to text that the result is correct
def error_arithmetic_decoding(message, binary_code, freqs, min_symb, image=False, debug=False):
    dec = arithmeticcoding.ArithmeticDecoder(32, binary_code)
    decoded_msg = []

    for i in range(0, len(message)):
        symbol = dec.read(freqs) + min_symb
        decoded_msg.append(symbol)

    if image is False:
        decoded_msg[0] = chr(decoded_msg[0])

    if debug is True:
        print("Decoded Message: {msg}".format(msg=decoded_msg))
    return message == decoded_msg


# Allows to decode an image encoded with the arithmetic decoding to text that the result is correct
# Inspired by https://github.com/ahmedfgad/ArithmeticEncodingPython
def image_arithmetic_decoding(image, binary_code, freqs, min_symb, debug):
    message = image.astype('uint8').flatten()

    dec = arithmeticcoding.ArithmeticDecoder(32, binary_code)
    decoded_msg = []

    for i in range(0, len(message)):
        symbol = dec.read(freqs) + min_symb
        decoded_msg.append(symbol)

    if debug:
        print("Decoded Message: {msg}".format(msg=decoded_msg))

    # Reshape the image to its original shape.
    decoded_img = numpy.reshape(decoded_msg, image.shape)

    if debug:
        # Show the original and decoded images.
        fig, ax = py.subplots(1, 2)
        ax[0].imshow(image, cmap="gray")
        ax[0].set_title("Original Image")
        ax[0].set_xticks([])
        ax[0].set_yticks([])
        ax[1].imshow(decoded_img, cmap="gray")
        ax[1].set_title("Reconstructed Image")
        ax[1].set_xticks([])
        ax[1].set_yticks([])
        py.show()

    return decoded_msg == message
