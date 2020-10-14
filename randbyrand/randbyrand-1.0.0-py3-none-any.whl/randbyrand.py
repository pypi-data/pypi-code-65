import requests
import zipfile
import os
import numpy as np
import pandas as pd

URL_MILLION_RANDOM_DIGITS = "https://www.rand.org/content/dam/rand/pubs/monograph_reports/MR1418/MR1418.digits.txt.zip"

def download_digits():
    """Downloads the digits in the original format to a digits.txt file"""
    r = requests.get(url=URL_MILLION_RANDOM_DIGITS)
    open("digits.zip", 'wb').write(r.content)
    zipfile.ZipFile("digits.zip", mode="r").extract("digits.txt")
    os.remove("digits.zip")

def get_digits(format="list"):
    """Returns the digits in the preferred format (list, numpy, pandas)"""
    
    # If the source file is missing, download it
    if not os.path.exists("digits.txt"):
        download_digits()
    
    digits = ""
    for line in open("digits.txt", "rt").readlines():
        # Ignore the first group of digits for each line, it is just the row number,
        # then remove any remaining spaces and newline charachters
        digits += list(line.split(" ", maxsplit=1))[1] \
                  .replace(" ", "").replace("\n", "")
    
    list_digits = [int(digit) for digit in digits]
    if format == "list":
        return list_digits
    elif format == "numpy":
        return np.array(list_digits)
    elif format == "pandas":
        return pd.DataFrame(list_digits)
    

def main():
    print("Testing the module randbyrand.")
    try:
        digits = get_digits()
    except:
        print("Downloading or reading digits failed.")
        return
    else:
        print("Downloading and reading digits succeded.")
    
    n = len(digits) 
    if n != 1000000:
        print("There should be one million digits, but only {} have benn loaded.".format(n))
        return
    else:
        print("One million digits have been retrieved correctly.")
    
    if digits[:5] == [1, 0, 0, 9, 7] and digits[999995:] == [4, 1, 9, 8, 8]:
        print("Heading and final digits match.")
    else:
        print("Heading and final digits do NOT match.")
        return
    
    try:
        digits = get_digits("numpy")
    except:
        print("Digits failed to load as Numpy array.")
        return
    else:
        print("Digits successfully loaded as Numpy array.")
    
    try:
        digits = get_digits("pandas")
    except:
        print("Digits failed to load as Pandas DataFrame.")
        return
    else:
        print("Digits successfully loaded as Pandas DataFrame.")
    
    print("All tests completed  successfully.")
    
if __name__ == "__main__":
    main()
    

