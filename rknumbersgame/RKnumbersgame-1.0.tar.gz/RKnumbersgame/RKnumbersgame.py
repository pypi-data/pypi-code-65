import random
import math

class Guess:
    '''
    Class to create number guessing game
    '''
    def __init__(self, lower=1, upper=50):
        '''
        Method to initialise & create function for number guessing game.
        The user chooses the lower and upper bounds for the integer range in scope. 
        The program then chooses an integer and gives the user a limited amount of 
        user input guesses to get the integer correctly.
        
        Inputs:
        lower - Lower integer value of number range to be looked at
        upper - Upper integer value of number range to be looked at
        '''
        self.upper = upper
        self.lower = lower
        self.guesses = round(math.log(upper - lower + 1, 2))
        self.answer = random.randint(lower, upper)
        self.count = 0

        # for calculation of minimum number of
        # guesses depends upon range
        while self.count < self.guesses:
            print("\n\tYou've only ", self.guesses - self.count," chances to guess the integer!\n")
            self.count += 1
             # taking guessing number as input
            guess = int(input("Guess a number:- ")) 

            # Condition testing
            if self.answer == guess:  
               print("Congratulations you did it in ", self.count, " tries")
               # Once guessed, loop will break 
               break
            elif self.answer > guess:
               print("You guessed too small!")
            elif self.answer < guess:
               print("You Guessed too high!")
        
        # If Guessing is more than required guesses, 
        # shows this output.
        if self.count >= self.guesses:
           print("\nThe number is {}".format(self.answer))
           print("\nBetter Luck Next time!")