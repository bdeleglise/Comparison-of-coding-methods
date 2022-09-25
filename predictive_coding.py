"""
Parts of this code are taken from and inspired by the code of
https://github.com/gabilodeau/INF8770/blob/master/Codage%20predictif%20sur%20image.ipynb
"""
import numpy as np


# Allows to do a predictive coding on a text
def text_predictive_coding(message):
    encoded_message = []
    predictor = ord(message[0])
    encoded_message.append(message[0])

    for i in range(1, len(message)):
        error = ord(message[i]) - predictor
        predictor = ord(message[i])
        encoded_message.append(error)

    return encoded_message


# Allows to do a predictive coding on an image
# Code taken from https://github.com/gabilodeau/INF8770/blob/master/Codage%20predictif%20sur%20image.ipynb
def imgage_predictive_coding(image):
    # Duplication des colonnes et rangées pour les frontières.
    col = image[:, 0]
    image = np.column_stack((col, image))
    col = image[:, len(image[0]) - 1]
    image = np.column_stack((col, image))
    row = image[0, :]
    image = np.row_stack((row, image))
    row = image[len(image) - 1, :]
    image = np.row_stack((row, image))

    # Matrice de prédiction. Un pixel est prédit à partir de ses 3 voisins.
    matpred = [[0.33, 0.33], [0.33, 0.0]]

    # Calcul des prédictions et des erreurs de prédictions.
    erreur = np.zeros((len(image) - 2, len(image[0]) - 2))
    imagepred = np.zeros((len(image) - 2, len(image[0]) - 2))
    for i in range(1, len(image) - 2):
        for j in range(1, len(image[0]) - 2):
            imagepred[i][j] = image[i - 1][j - 1] * matpred[0][0] + image[i - 1][j] * matpred[0][1] + image[i][j - 1] * \
                              matpred[1][0]
            erreur[i][j] = imagepred[i][j] - image[i][j]

    return imagepred, erreur
