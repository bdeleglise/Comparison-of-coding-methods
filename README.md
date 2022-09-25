# INF8770 Lab 1 - Comparison-of-coding-methods

In this directory you will find 2 methods of coding text and image files. The predictive coding which is implemented in the file predictive_coding.py. The arithmetic coding which is implemented in the file arithmeticcoding.py

## Run the tester

To test all the dataset you just need to execute the script tester.sh. 
All result will be saved in result_text.csv or result_image.csv.

```
./tester.sh
```

Be sure to have python and all packages installed.

## Run encoding individually

To run encoding in the terminal :
```
python main.py TYPE MODE ALGO FILE [DEBUG]
```

* TYPE is the type of the file -i for an image or -t for a text
* MODE this is the reading option: 
  - for images -RGB to encode the 3 axes or -GRAY to convert the image to grayscale
  - for texts -Unicode to consider that the symbols are encoded on 1 byte -M to simply read the message and -RAND to generate a random message
* ALGO specifies the algo to use:
  - ALL for all
  - AR for arithmetic 
  - PRE for predictive
  - PREAR for predictive and arithmetic in sequence
* FILE gives the file studied and for a random generation the size of it
* DEBUG is optional and enables debugging

## Source

* For predictive coding :
  - https://github.com/gabilodeau/INF8770/blob/master/Codage%20predictif%20sur%20image.ipynb

* For arithmetic coding :
  - https://github.com/gabilodeau/INF8770/blob/master/Codage%20arithmetique.ipynb
  - https://github.com/nayuki/Reference-arithmetic-coding
  - https://github.com/ahmedfgad/ArithmeticEncodingPython
  - https://marknelson.us/posts/2014/10/19/data-compression-with-arithmetic-coding.html