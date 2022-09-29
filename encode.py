"""
Parts of this code are taken from and inspired by the code of https://github.com/gabilodeau/INF8770
"""

import numpy as np
from collections import Counter
import predictive_coding
import arithmetic_coding
import time
import matplotlib.pyplot as py

import random
import string

"""
This method allows you to process the encoding of a text file
"""


def encode_text(type, algo, file, output, debug):
    message = ""
    if type == '-Unicode' or type == '-M':
        f = open(file, "r", encoding="utf-8")
        message = f.read()
    elif type == '-RAND':
        letters = string.ascii_letters + string.digits + string.punctuation
        message = ''.join(random.choice(letters) for i in range(int(file)))
        file = "RANDOM with " + file
    else:
        exit(1)

    if debug is True:
        print(message)

    unicode = False
    if type == '-Unicode':
        unicode = True

    initial_length = compute_length(unicode, message, debug)
    arithmetic_coding_algo, predictive_coding_algo, predictive_arithmetic_coding = define_coding_method(algo)

    if predictive_coding_algo is True:
        print('Predictive coding')
        start = time.time()
        result = predictive_coding.text_predictive_coding(message)
        end = time.time()

        predicted_errors = result[1:]
        min_error = min(predicted_errors)
        max_error = max(predicted_errors)

        # 2 methods to stock errors

        """ First one
        to know how many bits occupy the error measurement we estimate that we need at most a sufficient number of 
        bits to represent the difference between the max and the min 
        
        in addition to that, for the decoding it will be necessary to store the first symbol on a maximum of 8 bits and 
        the min and max which can be negative and will occupy therefore a maximum of 9 bits. So we add 26 bits to the result
        """
        nbsymbolesMax = max_error - min_error + 1
        encoded_length = np.ceil(np.log2(nbsymbolesMax)) * len(predicted_errors)
        data_to_decode = 26

        """ Second one
        For the second method we estimate the minimum number of bits necessary to translate the errors and then 
        we set up a dictionary that must be saved
        
        for the dictionary 9 bits are used to encode one symbol because it can be negative and we need 
        np.ceil(np.log2(nbsymbolesMax)) to encode the minimum translation
         + 4bits to determine the minimum number
        """
        nbsymbolesMax = len(Counter(result))
        encoded_length_dict = np.ceil(np.log2(nbsymbolesMax)) * len(result)
        dictionary = nbsymbolesMax * (np.ceil(np.log2(nbsymbolesMax)) + 9) + 4

        write_text_result(file, unicode, initial_length,
                          encoded_length, data_to_decode,
                          1 - (encoded_length / initial_length),
                          1 - ((encoded_length + data_to_decode) / initial_length),
                          encoded_length_dict, dictionary,
                          1 - (encoded_length_dict / initial_length),
                          1 - ((encoded_length_dict + dictionary) / initial_length),
                          end - start,
                          "Predictive coding", "OK", output)

    if arithmetic_coding_algo is True:
        print('Arithmetic coding')
        start = time.time()
        freqs, freqs_length, binary_code, min_symb = arithmetic_coding.text_arithmetic_coding(message, debug)
        end = time.time()

        encoded_length = len(binary_code)

        # verif si ok
        status = arithmetic_coding.text_arithmetic_decoding(message, binary_code, freqs, min_symb, True, debug)

        if debug:
            print("Message Decoded Successfully? {result}".format(result=status))

        if status:
            status = "OK"
        else:
            status = "KO"
        write_text_result(file, unicode, initial_length,
                          encoded_length, freqs_length,
                          1 - (encoded_length / initial_length),
                          1 - ((encoded_length + freqs_length) / initial_length),
                          None, None, None, None,
                          end - start, "Arithmetic coding", status,
                          output)

    if predictive_arithmetic_coding is True:
        print('Predictive + Arithmetic coding')
        start = time.time()
        result = predictive_coding.text_predictive_coding(message)
        freqs, freqs_length, binary_code, min_symb = arithmetic_coding.error_arithmetic_coding(result, debug)
        end = time.time()

        encoded_length = len(binary_code)

        # verif si ok
        status = arithmetic_coding.error_arithmetic_decoding(result, binary_code, freqs, min_symb, False, debug)

        if debug:
            print("Message Decoded Successfully? {result}".format(result=status))

        if status:
            status = "OK"
        else:
            status = "KO"

        # we add 9bits to freq_length to stock the min_symb that can be a negative number
        write_text_result(file, unicode, initial_length,
                          encoded_length, freqs_length + 9,
                          1 - (encoded_length / initial_length),
                          1 - ((encoded_length + freqs_length + 9) / initial_length),
                          None, None, None, None,
                          end - start, "Predictive + Arithmetic coding", status,
                          output)


"""
This method allows you to process the encoding of an image file
"""


def encode_image(type, algo, file, output, debug):
    imagelue = py.imread(file)
    if type == "-RGB":
        encode_rgb_image(imagelue, algo, file, output, debug)
    elif type == "-GRAY":
        encode_gray_scale_image(imagelue, algo, file, output, debug)
    else:
        exit(1)


"""
This method allows you to process the encoding of an image 
on its tree rgb axis
"""


def encode_rgb_image(imagelue, algo, file, output, debug):
    x, y, z = np.shape(imagelue)

    # Code from https://instrovate.com/2019/06/14/using-python-splitting-colored-image-in-to-red-blue-green-component/
    # Split an image into red green blue matrix
    red = np.zeros((x, y), dtype=int)
    green = np.zeros((x, y), dtype=int)
    blue = np.zeros((x, y), dtype=int)
    for i in range(0, x):
        for j in range(0, y):
            red[i][j] = imagelue[i][j][0]
            green[i][j] = imagelue[i][j][1]
            blue[i][j] = imagelue[i][j][2]

    arithmetic_coding_algo, predictive_coding_algo, predictive_arithmetic_coding = define_coding_method(algo)

    counter = Counter(imagelue.astype('int').flatten())
    nbsymboles = len(counter)
    length_with_min_bit = np.ceil(np.log2(nbsymboles)) * imagelue.size

    if predictive_coding_algo is True:
        print('Predictive coding')
        encoded_length_red, data_to_decode_red, encoded_length_dict_red, dictionary_red, time_red = \
            process_one_axis_predictive_coding_algo(red, " RED", output, file, debug)
        encoded_length_green, data_to_decode_green, encoded_length_dict_green, dictionary_green, time_green = \
            process_one_axis_predictive_coding_algo(green, " GREEN", output, file, debug)
        encoded_length_blue, data_to_decode_blue, encoded_length_dict_blue, dictionary_blue, time_blue = \
            process_one_axis_predictive_coding_algo(blue, " BLUE", output, file, debug)

        initial_length = imagelue.size
        encoded_length = encoded_length_red + encoded_length_green + encoded_length_blue
        data_to_decode = data_to_decode_red + data_to_decode_green + data_to_decode_blue
        encoded_length_dict = encoded_length_dict_blue + encoded_length_dict_red + encoded_length_dict_green
        dictionary = dictionary_red + dictionary_green + dictionary_blue
        time = time_red + time_green + time_blue
        write_image_result(file, initial_length,
                           encoded_length,
                           data_to_decode,
                           1 - (encoded_length / (initial_length*8)),
                           1 - ((encoded_length + data_to_decode) / (initial_length*8)),
                           encoded_length_dict, dictionary,
                           1 - (encoded_length_dict / (initial_length*8)),
                           1 - ((encoded_length_dict + dictionary) / (initial_length*8)),
                           time,
                           "Predictive coding", "OK", output, "", 8, length_with_min_bit)

    if arithmetic_coding_algo is True:
        print('Arithmetic coding')
        encoded_length_red, freqs_length_red, time_red, status_red = process_one_axis_arithmetic_coding_algo(red,
                                                                                                             " RED",
                                                                                                             output,
                                                                                                             file, debug)
        encoded_length_green, freqs_length_green, time_green, status_green = process_one_axis_arithmetic_coding_algo(
            green, " GREEN", output, file, debug)
        encoded_length_blue, freqs_length_blue, time_blue, status_blue = process_one_axis_arithmetic_coding_algo(
            blue, " BLUE", output, file, debug)

        initial_length = imagelue.size
        encoded_length = encoded_length_red + encoded_length_green + encoded_length_blue
        freqs_length = freqs_length_red + freqs_length_green + freqs_length_blue
        time = time_red + time_green + time_blue
        write_image_result(file, initial_length,
                           encoded_length, freqs_length,
                           1 - (encoded_length / (initial_length*8)),
                           1 - ((encoded_length + freqs_length) / (initial_length*8)),
                           0, 0, 0, 0,
                           time, "Arithmetic coding", status_red and status_green and status_blue,
                           output, "", 8, length_with_min_bit)

    if predictive_arithmetic_coding is True:
        print('Predictive + Arithmetic coding')
        encoded_length_red, freqs_length_red, time_red, status_red = process_one_axis_predictive_arithmetic_coding(red,
                                                                                                                   " RED",
                                                                                                                   output,
                                                                                                                   file, debug)
        encoded_length_green, freqs_length_green, time_green, status_green = process_one_axis_predictive_arithmetic_coding(
            green, " GREEN", output, file, debug)
        encoded_length_blue, freqs_length_blue, time_blue, status_blue = process_one_axis_predictive_arithmetic_coding(
            blue, " BLUE", output, file, debug)

        initial_length = imagelue.size
        encoded_length = encoded_length_red + encoded_length_green + encoded_length_blue
        freqs_length = freqs_length_red + freqs_length_green + freqs_length_blue
        time = time_red + time_green + time_blue
        write_image_result(file, initial_length,
                           encoded_length, freqs_length,
                           1 - (encoded_length / (initial_length*8)),
                           1 - ((encoded_length + freqs_length) / (initial_length*8)),
                           0, 0, 0, 0,
                           time, "Predictive + Arithmetic coding", status_red and status_green and status_blue,
                           output, "", 8, length_with_min_bit)


"""
This method allows you to process the predictive_arithmetic_coding of an image 
on a specific axis 
"""


def process_one_axis_predictive_arithmetic_coding(image, color, output, file, debug):
    start = time.time()
    imagepred, erreur = predictive_coding.imgage_predictive_coding(image)
    erreur = erreur[:, 1:]
    erreur = np.column_stack([image[:, 0], erreur])
    erreur = erreur[1:, :]
    erreur = np.row_stack([image[0, :], erreur])
    erreurArr = erreur.astype('int').flatten()
    freqs, freqs_length, binary_code, min_symb = arithmetic_coding.error_arithmetic_coding(erreurArr, debug)
    end = time.time()
    encoded_length = len(binary_code)

    # verif si ok, for an image it can be very long because of the number of pixel so by default we don't do the verif
    status = "OK"
    if debug:
        status = arithmetic_coding.error_arithmetic_decoding(erreurArr, binary_code, freqs, min_symb, True, debug)

        result = True
        for i in range(0, len(status)):
            if status[i] is False:
                result = False
                break

        if result:
            status = "OK"
        else:
            status = "KO"

    initial_length = image.size
    if debug:
        write_image_result(file, initial_length,
                       encoded_length, freqs_length,
                       1 - (encoded_length / (initial_length*8)),
                       1 - ((encoded_length + freqs_length) / (initial_length*8)),
                       0, 0, 0, 0,
                       end - start, "Predictive + Arithmetic coding", status,
                       output, color, 8, None)

    return encoded_length, freqs_length, end - start, status


"""
This method allows you to process the arithmetic_coding of an image 
on a specific axis 
"""


def process_one_axis_arithmetic_coding_algo(image, color, output, file, debug):
    start = time.time()
    freqs, freqs_length, binary_code, min_symb = arithmetic_coding.image_arithmetic_coding(image, debug)
    end = time.time()

    encoded_length = len(binary_code)

    # verif si ok, for an image it can be very long because of the number of pixel so by default we don't do the verif
    status = "OK"
    if debug:
        status = arithmetic_coding.image_arithmetic_decoding(image, binary_code, freqs, min_symb, debug)

        result = True
        for i in range(0, len(status)):
            if status[i] is False:
                result = False
                break

        if result:
            status = "OK"
        else:
            status = "KO"

    initial_length = image.size
    if debug:
        write_image_result(file, initial_length,
                       encoded_length, freqs_length,
                       1 - (encoded_length / (initial_length*8)),
                       1 - ((encoded_length + freqs_length) / (initial_length*8)),
                       0, 0, 0, 0,
                       end - start, "Arithmetic coding", status,
                       output, color, 8, None)

    return encoded_length, freqs_length, end - start, status


"""
This method allows you to process the predictive_coding of an image 
on a specific axis 
"""


def process_one_axis_predictive_coding_algo(image, color, output, file, debug):
    start = time.time()
    imagepred, erreur = predictive_coding.imgage_predictive_coding(image)
    end = time.time()
    erreurArr = erreur.astype('int').flatten()
    min_error = min(erreurArr)
    max_error = max(erreurArr)

    """ First one
           to know how many bits occupy the error measurement we estimate that we need at most a sufficient number of 
           bits to represent the difference between the max and the min 

           in addition to that, for the decoding it will be necessary to store the first line and column 
           on a maximum of 8 bits and 
           the minimum and max which can be negative and will occupy therefore a maximum of 9 bits. 
           So we add (h+w-1)*8 + 18 bits to the result
    """
    nbsymbolesMax = max_error - min_error + 1
    encoded_length = np.ceil(np.log2(nbsymbolesMax)) * (erreur.size - len(image) - len(image[0]))
    data_to_decode = (len(image) + len(image[0]) - 1) * 8 + 18

    """ Second one
            For the second method we estimate the minimum number of bits necessary to translate the errors and then 
            we set up a dictionary that must be saved

        for the dictionary 9 bits are used to encode one symbol because it can be negative and we need 
        np.ceil(np.log2(nbsymbolesMax)) to encode the minimum translation
         + 4bits to determine the minimum number
    """
    erreur = erreur[:, 1:]
    erreur = np.column_stack([image[:, 0], erreur])
    erreur = erreur[1:, :]
    erreur = np.row_stack([image[0, :], erreur])
    erreurArr = erreur.astype('int').flatten()
    nbsymbolesMax = len(Counter(erreurArr))
    encoded_length_dict = np.ceil(np.log2(nbsymbolesMax)) * len(erreurArr)
    dictionary = nbsymbolesMax * (np.ceil(np.log2(nbsymbolesMax)) + 9) + 4

    initial_length = image.size

    if debug:
        write_image_result(file, initial_length,
                       encoded_length, data_to_decode,
                       1 - (encoded_length / (initial_length*8)),
                       1 - ((encoded_length + data_to_decode) / (initial_length*8)),
                       encoded_length_dict, dictionary,
                       1 - (encoded_length_dict / (initial_length*8)),
                       1 - ((encoded_length + dictionary) / (initial_length*8)),
                       end - start,
                       "Predictive coding", "OK", output, color, 8, None)

    return encoded_length, data_to_decode, encoded_length_dict, dictionary, end - start


"""
This method allows you to process the encoding of an image 
convert in gray level
"""


def encode_gray_scale_image(imagelue, algo, file, output, debug):
    # Code from https://github.com/gabilodeau/INF8770/blob/master/Codage%20arithmetique.ipynb
    image = imagelue.astype('float')
    image = rgb2gray(image)
    imageout = image.astype('uint8')

    initial_length = imageout.size

    counter = Counter(imageout.flatten())
    nbsymboles = len(counter)
    length_with_min_bit = np.ceil(np.log2(nbsymboles)) * initial_length

    if debug is True:
        # Code from https://github.com/gabilodeau/INF8770/blob/master/Codage%20arithmetique.ipynb
        fig1 = py.figure(figsize=(10, 10))
        py.imshow(imageout, cmap=py.get_cmap('gray'))
        py.show()

        hist, intervalles = np.histogram(imageout, bins=256)
        py.bar(intervalles[:-1], hist, width=2)
        py.xlim(min(intervalles) - 1, max(intervalles))
        py.show()

    arithmetic_coding_algo, predictive_coding_algo, predictive_arithmetic_coding = define_coding_method(algo)

    if predictive_coding_algo is True:
        print('Predictive coding')
        start = time.time()
        imagepred, erreur = predictive_coding.imgage_predictive_coding(image)
        end = time.time()

        if debug is True:
            # Code from https://github.com/gabilodeau/INF8770/blob/master/Codage%20arithmetique.ipynb
            hist, intervalles = np.histogram(erreur, bins=100)
            py.bar(intervalles[:-1], hist, width=2)
            py.xlim(min(intervalles) - 1, max(intervalles))
            py.show()

            fig2 = py.figure(figsize=(10, 10))
            imageout = imagepred.astype('uint8')
            py.imshow(imageout, cmap=py.get_cmap('gray'))
            py.show()

            fig3 = py.figure(figsize=(10, 10))
            erreur_amp = abs(erreur) * 5
            imageout = erreur_amp.astype('uint8')
            py.imshow(imageout, cmap=py.get_cmap('gray'))
            py.show()

        erreurArr = erreur.astype('int').flatten()
        min_error = min(erreurArr)
        max_error = max(erreurArr)

        # 2 methods to measure errors

        """ First one
        to know how many bits occupy the error measurement we estimate that we need at most a sufficient number of 
        bits to represent the difference between the max and the min 

        in addition to that, for the decoding it will be necessary to store the first line and column 
        on a maximum of 8 bits and 
        the minimum and max which can be negative and will occupy therefore a maximum of 9 bits. 
        So we add (h+w-1)*8 + 18 bits to the result
        """
        nbsymbolesMax = max_error - min_error + 1
        encoded_length = np.ceil(np.log2(nbsymbolesMax)) * (erreur.size - len(image) - len(image[0]))
        data_to_decode = (len(image) + len(image[0]) - 1) * 8 + 18

        """ Second one
        For the second method we estimate the minimum number of bits necessary to translate the errors and then 
        we set up a dictionary that must be saved

        for the dictionary 9 bits are used to encode one symbol because it can be negative and we need 
        np.ceil(np.log2(nbsymbolesMax)) to encode the minimum translation
         + 4bits to determine the minimum number
        """
        erreur = erreur[:, 1:]
        erreur = np.column_stack([image[:, 0], erreur])
        erreur = erreur[1:, :]
        erreur = np.row_stack([image[0, :], erreur])
        erreurArr = erreur.astype('int').flatten()
        nbsymbolesMax = len(Counter(erreurArr))
        encoded_length_dict = np.ceil(np.log2(nbsymbolesMax)) * len(erreurArr)
        dictionary = nbsymbolesMax * (np.ceil(np.log2(nbsymbolesMax)) + 9) + 4

        write_image_result(file, initial_length,
                           encoded_length, data_to_decode,
                           1 - (encoded_length / (initial_length*8)),
                           1 - ((encoded_length + data_to_decode) / (initial_length*8)),
                           encoded_length_dict, dictionary,
                           1 - (encoded_length_dict / (initial_length*8)),
                           1 - ((encoded_length_dict + dictionary) / (initial_length*8)),
                           end - start,
                           "Predictive coding", "OK", output, " GRAY level", 8, length_with_min_bit)

    if arithmetic_coding_algo is True:
        print('Arithmetic coding')
        start = time.time()
        freqs, freqs_length, binary_code, min_symb = arithmetic_coding.image_arithmetic_coding(image, debug)
        end = time.time()

        encoded_length = len(binary_code)

        # verif si ok, for an image it can be very long because of the number of pixel so by default we don't do the
        # verif
        status = "OK"
        if debug:
            status = arithmetic_coding.image_arithmetic_decoding(image, binary_code, freqs, min_symb, debug)

            result = True
            for i in range(0, len(status)):
                if status[i] is False:
                    result = False
                    break

            print("Message Decoded Successfully? {result}".format(result=result))

            if result:
                status = "OK"
            else:
                status = "KO"
        write_image_result(file, initial_length,
                           encoded_length, freqs_length,
                           1 - (encoded_length / (initial_length*8)),
                           1 - ((encoded_length + freqs_length) / (initial_length*8)),
                           0, 0, 0, 0,
                           end - start, "Arithmetic coding", status,
                           output, " GRAY level", 8, length_with_min_bit)

    if predictive_arithmetic_coding is True:
        print('Predictive + Arithmetic coding')
        start = time.time()
        imagepred, erreur = predictive_coding.imgage_predictive_coding(image)
        erreur = erreur[:, 1:]
        erreur = np.column_stack([image[:, 0], erreur])
        erreur = erreur[1:, :]
        erreur = np.row_stack([image[0, :], erreur])
        erreurArr = erreur.astype('int').flatten()
        freqs, freqs_length, binary_code, min_symb = arithmetic_coding.error_arithmetic_coding(erreurArr, debug)
        end = time.time()

        encoded_length = len(binary_code)

        # verif si ok, for an image it can be very long because of the number of pixel so by default we don't do the
        # verif
        status = "OK"
        if debug:
            status = arithmetic_coding.error_arithmetic_decoding(erreurArr, binary_code, freqs, min_symb, True, debug)

            result = True
            for i in range(0, len(status)):
                if status[i] is False:
                    result = False
                    break

            print("Message Decoded Successfully? {result}".format(result=result))

            if result:
                status = "OK"
            else:
                status = "KO"
        write_image_result(file, initial_length,
                           encoded_length, freqs_length,
                           1 - (encoded_length / (initial_length*8)),
                           1 - ((encoded_length + freqs_length) / (initial_length*8)),
                           0, 0, 0, 0,
                           end - start, "Predictive + Arithmetic coding", status,
                           output, " GRAY level", 8, length_with_min_bit)


# Source https://github.com/gabilodeau/INF8770/blob/master/Codage%20predictif%20sur%20image.ipynb
# Allows to convert an image in rgb into gray level
def rgb2gray(rgb):
    return np.dot(rgb[:, :], [0.299, 0.587, 0.114])


# Allows to define the coding method that will be used
def define_coding_method(algo):
    arithmetic_coding_algo = False
    predictive_coding_algo = False
    predictive_arithmetic_coding = False

    if algo == '-ALL':
        arithmetic_coding_algo = True
        predictive_coding_algo = True
        predictive_arithmetic_coding = True
    elif algo == '-AR':
        arithmetic_coding_algo = True
    elif algo == '-PRE':
        predictive_coding_algo = True
    elif algo == '-PREAR':
        predictive_arithmetic_coding = True
    else:
        print('Not Implemented Yet')
        exit(1)

    return arithmetic_coding_algo, predictive_coding_algo, predictive_arithmetic_coding


# Allows to compute the length of a message
def compute_length(unicode, message, debug):
    if unicode:
        length = 8 * len(message)
    else:
        counter = Counter(message)
        nbsymboles = len(counter)
        if debug is True:
            print(counter)
            print(nbsymboles)

        # From https://github.com/gabilodeau/INF8770/blob/master/Codage%20arithmetique.ipynb
        length = np.ceil(np.log2(nbsymboles)) * len(message)

    return length


# Allows to write in the result file the encoding result and info
def write_text_result(title, unicode, initial_length,
                      encoded_length, data_to_decode,
                      compression_encoded, compression_with_data_to_decode,
                      encoded_length_dict, dict_size,
                      compression_encoded_dict, compression_dict_with_data_to_decode,
                      time, algo,
                      status, output):
    if unicode is True:
        title += " read with utf8 (unicode)"

    f = open(output, "a")
    f.write(title + ";" + status + ";" + algo + ";" + str(initial_length) + ";" + str(encoded_length) + ";" + str(
        data_to_decode) + ";" + str(compression_encoded) + ";" + str(compression_with_data_to_decode)
            + ";" + str(encoded_length_dict) + ";" + str(dict_size)
            + ";" + str(compression_encoded_dict) + ";" + str(compression_dict_with_data_to_decode) + ";"
            + str(time) + "\n")
    f.close()


def write_image_result(title, initial_length,
                       encoded_length, data_to_decode,
                       compression_encoded, compression_with_data_to_decode,
                       encoded_length_dict, dict_size,
                       compression_encoded_dict, compression_dict_with_data_to_decode,
                       time, algo,
                       status, output, type, nbBits, length_with_min_bit):
    title += type
    f = open(output, "a")
    f.write(
        title + ";" + status + ";" + algo + ";" + str(initial_length * nbBits) + ";" + str(encoded_length) + ";" + str(
            data_to_decode+encoded_length) + ";" + str(compression_encoded) + ";" + str(compression_with_data_to_decode)
        + ";" + str(encoded_length_dict) + ";" + str(encoded_length_dict+dict_size)
        + ";" + str(compression_encoded_dict) + ";" + str(compression_dict_with_data_to_decode) + ";"
        + str(time) + ";" + str(length_with_min_bit) + "\n")
    f.close()
