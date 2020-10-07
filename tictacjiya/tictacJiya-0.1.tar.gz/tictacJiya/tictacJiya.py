from random import *
from time import *


class TicTacToeJiya:
    def __init__(self):
        print("Tic Tac Toe Jiya [we will be using 'A' and 'J'")
        print("1 - TicTacToeJiya Single Player, against the Computer")
        print("2 - TicTacToeJiya with a friend")
        print("3 - Press 3 to allow a computer vs. computer game")
        TicTacToeJiya.Choice = input("Please Choose your style of game: ")
        while TicTacToeJiya.Choice not in ['1','2','3']:
            TicTacToeJiya.Choice = input("Please choose one of the options as your style of play [1,2,3]: ")
        if TicTacToeJiya.Choice == '1':
            TicTacToeJiya.game_style = "Single"
        elif TicTacToeJiya.Choice == '2':
            TicTacToeJiya.game_style = "Multiplayer"
        else:
            print("\nComputer v Computer \n")
            TicTacToeJiya.game_style = "Computer vs. Computer"
        Board()
        TicTacToeJiya.Type = choice(['A','J'])
        TicTacToeJiya.Round()



        if TicTacToeJiya.game_result == True:
            print(TicTacToeJiya.WinningType, "Wins!")
        else:
            print("Woah! both of you are equally good! This is a DRAW! You may want to play another game to see who wins")
        PlayAgain = input("Do you want to play again? Yes or No: ")
        if PlayAgain in ["Yes", "yes", "y", "Y"]:
            print()
            TicTacToeJiya()

    def Round():
        TicTacToeJiya.game_result = False
        while not TicTacToeJiya.game_result:
            if TicTacToeJiya.game_style in ["Single","Multiplayer"]:
                TicTacToeJiya.Move()
                TicTacToeJiya.who_wins()
                TicTacToeJiya.change_type()
            if TicTacToeJiya.game_style != "Multiplayer" and TicTacToeJiya.game_result == False:# If Single Player and the Game has not been Won...
                print(TicTacToeJiya.Type+"'s Go...")
                sleep(1)
                Computer.GetComputersMove()
                TicTacToeJiya.who_wins()
                TicTacToeJiya.change_type()

    def Move():
        TicTacToeJiya.confirm_space()#asks for your position on the board
        Board.PrintBoard()#shows the board

    def change_type():
        if TicTacToeJiya.Type == 'A':
            TicTacToeJiya.Type = 'J'
        else:
            TicTacToeJiya.Type = 'A'

    def confirm_space():
        Valid = False
        print(TicTacToeJiya.Type+"'s Go...")#J's Go... / A's Go...
        while not Valid:
            Position = input("Please type where you wish to place: ")
            while Position.isdigit() == False or int(Position) > 9 or int(Position) <= 0:#Ensures the player does not type an incorrect location to place in
                Position = input("Please type a valid integer between 1 and 9: ")
            TicTacToeJiya.Position = int(Position)
            if Board.Space[TicTacToeJiya.Position-1] == 'A' or Board.Space[TicTacToeJiya.Position-1] == 'J':#9 on the keypad would refer to index 8, as starts from 0 but keypad starts at 1
                Valid = False
                print("That is an invalid square, please try again ")
            else:
                Valid = True
        Board.Space[TicTacToeJiya.Position-1] = TicTacToeJiya.Type

    def who_wins():
        if ((Board.Space[0]== TicTacToeJiya.Type) and (Board.Space[1] == TicTacToeJiya.Type) and (Board.Space[2] == TicTacToeJiya.Type)) or (
            (Board.Space[3]== TicTacToeJiya.Type) and (Board.Space[4] == TicTacToeJiya.Type) and (Board.Space[5] == TicTacToeJiya.Type)) or (
            (Board.Space[6]== TicTacToeJiya.Type) and (Board.Space[7] == TicTacToeJiya.Type) and (Board.Space[8] == TicTacToeJiya.Type)) or (
            #Row Check^^^^^^^
            (Board.Space[0]== TicTacToeJiya.Type) and (Board.Space[3] == TicTacToeJiya.Type) and (Board.Space[6] == TicTacToeJiya.Type)) or (
            (Board.Space[1]== TicTacToeJiya.Type) and (Board.Space[4] == TicTacToeJiya.Type) and (Board.Space[7] == TicTacToeJiya.Type)) or (
            (Board.Space[2]== TicTacToeJiya.Type) and (Board.Space[5] == TicTacToeJiya.Type) and (Board.Space[8] == TicTacToeJiya.Type)) or (
            #Column Check^^^^
            (Board.Space[0]== TicTacToeJiya.Type) and (Board.Space[4] == TicTacToeJiya.Type) and (Board.Space[8] == TicTacToeJiya.Type)) or (
            (Board.Space[2]== TicTacToeJiya.Type) and (Board.Space[4] == TicTacToeJiya.Type) and (Board.Space[6] == TicTacToeJiya.Type)):
            #Diagonal Check^^
            TicTacToeJiya.WinningType = TicTacToeJiya.Type
            TicTacToeJiya.game_result = True
        if TicTacToeJiya.game_result != True:
            DrawCheck = 0
            for i in range(0,9):
                if Board.Space[i] == ' ':
                    DrawCheck = DrawCheck + 1
            if DrawCheck == 0:
                TicTacToeJiya.game_result = 'Draw'

class Computer:
    def GetComputersMove():
        Computer.FindEmptySpaces()
        Computer.ComputerMove()
        Board.PrintBoard()

    def FindEmptySpaces():
        Computer.EmptySpaces = []
        for i in range(0,9):
            if Board.Space[i] == ' ':
                Computer.EmptySpaces.append(i) # Adds them to a list for future reference

    def ComputerMove(): #teaches computer to play the game and win using the algorithm below
        Computer.Change = False
        OriginalType = TicTacToeJiya.Type
        for j in range(0,2):
            for i in range(0,len(Computer.EmptySpaces)):
                if not Computer.Change:
                    Computer.CheckComputerWin((Computer.EmptySpaces[i]))
                if Computer.Change:    # If there is a change...
                    Board.Space[Computer.EmptySpaces[i]] = OriginalType # Fills in the space
                    TicTacToeJiya.Type = OriginalType
                    return
            TicTacToeJiya.change_type() #switches the type, to see if any draws are available AFTER checking for wins
        TicTacToeJiya.Type = OriginalType
        Board.Space[choice(Computer.EmptySpaces)] = OriginalType # If no places were found to have a effect, randomize the location...

    def CheckComputerWin(SpaceToCheck):
        if (SpaceToCheck in [6,3,0] and Board.Space[SpaceToCheck + 1] == TicTacToeJiya.Type and Board.Space[SpaceToCheck + 2] == TicTacToeJiya.Type) or (#Left Side Checks     |
            SpaceToCheck in [7,4,1] and Board.Space[SpaceToCheck + 1] == TicTacToeJiya.Type and Board.Space[SpaceToCheck - 1] == TicTacToeJiya.Type) or (#Central Column check | Horizontal Checks
            SpaceToCheck in [8,5,2] and Board.Space[SpaceToCheck - 1] == TicTacToeJiya.Type and Board.Space[SpaceToCheck - 2] == TicTacToeJiya.Type) or (#Right Side Check     |
            SpaceToCheck in [6,7,8] and Board.Space[SpaceToCheck - 3] == TicTacToeJiya.Type and Board.Space[SpaceToCheck - 6] == TicTacToeJiya.Type) or (#Top Row Check     |
            SpaceToCheck in [5,4,3] and Board.Space[SpaceToCheck - 3] == TicTacToeJiya.Type and Board.Space[SpaceToCheck + 3] == TicTacToeJiya.Type) or (#Middle Row Check  | Vertical Checks
            SpaceToCheck in [2,1,0] and Board.Space[SpaceToCheck + 3] == TicTacToeJiya.Type and Board.Space[SpaceToCheck + 6] == TicTacToeJiya.Type) or (#Bottom Row Check  |
            SpaceToCheck == 0 and Board.Space[SpaceToCheck + 4] == TicTacToeJiya.Type and Board.Space[SpaceToCheck + 8] == TicTacToeJiya.Type) or ( #Bottom Left  |
            SpaceToCheck == 2 and Board.Space[SpaceToCheck + 2] == TicTacToeJiya.Type and Board.Space[SpaceToCheck + 4] == TicTacToeJiya.Type) or ( #Bottom Right | Diagonal
            SpaceToCheck == 6 and Board.Space[SpaceToCheck - 2] == TicTacToeJiya.Type and Board.Space[SpaceToCheck - 4] == TicTacToeJiya.Type) or ( #Top Left     | Checks
            SpaceToCheck == 8 and Board.Space[SpaceToCheck - 4] == TicTacToeJiya.Type and Board.Space[SpaceToCheck - 8] == TicTacToeJiya.Type) or ( #Top Right    |
            SpaceToCheck == 4 and ((Board.Space[SpaceToCheck + 2] == TicTacToeJiya.Type and Board.Space[SpaceToCheck - 2] == TicTacToeJiya.Type) or ( # Centre Piece, | Top-Left to Bottom-Right  | Diagonal
                Board.Space[SpaceToCheck + 4] == TicTacToeJiya.Type and Board.Space[SpaceToCheck - 4] == TicTacToeJiya.Type))):                     # Centre Piece, | Top-Right to Bottom-Left  | Checks
            Computer.Change = True
class Board:
    def __init__(self):
        if TicTacToeJiya.game_style in ["Single", "Multiplayer"]:
            Board.Space = ['7','8','9',#show the players which space each of the number represents
                            '4','5','6',
                            '1','2','3']
            print("This is how the board is labeled")
            Board.PrintBoard()
        Board.Space = [' ',' ',' ',
                        ' ',' ',' ',
                        ' ',' ',' ']
        if TicTacToeJiya.game_style not in ["Single","Multiplayer"]:
            Board.PrintBoard()
            sleep(1)

    def PrintBoard(): #Prints the Board, mirrors a laptop's keypad
        print('',Board.Space[6],'|',Board.Space[7],'|',Board.Space[8],'')
        print('---|---|---')
        print('',Board.Space[3],'|',Board.Space[4],'|',Board.Space[5],'')
        print('---|---|---')
        print('',Board.Space[0],'|',Board.Space[1],'|',Board.Space[2],'')



TicTacToeJiya()
