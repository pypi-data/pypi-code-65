# Importing Class
from oopsImplementation import directoryOrganiser

# Importing Libraries
import time


# Package Function
def organiser():

    # Using Error Handling Techniques to Handle Error(s)
    try:

        print('''
Where do you want to Organise your Files?
1. Downloads [System]
2. Any Other Location
Enter the Full Path to your Directory [Just Press ENTER for Case 1] ->''')
        path = input()
        start = time.time()
        moveFilesObject = directoryOrganiser(path)
        moveFilesObject.checkCondition()
        end = time.time()
        print('Time Elapsed : ', round(end - start, 2), 'seconds')

    except Exception as exception:

        print("Please Try Again! An Unexpected Error has Occurred!")
        print(f"Type : {type(exception)}")
        print(f"Error : {exception}")


# Commenting out for Packaging.
'''
# Main Method
if __name__ == '__main__':
    organiser()
'''