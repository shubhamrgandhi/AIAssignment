##############

#Your program can go here.

import numpy as np
from math import sqrt, log
import random
from tqdm import tqdm
import time
# import os
import sys
import matplotlib.pyplot as plt

NROWS = 6
NCOLS = 5
ITER1 = 10
ITER2 = 10
# There will be two players, one will be represented by '1' and the other by '-1'

# Function to create a game with number of rows = nrows and number of columns = ncols in the grid
# Initialize all positions with zeros
def createGame(nrows = NROWS, ncols = NCOLS):
    NROWS = nrows
    NCOLS = ncols
    game = np.zeros((nrows, ncols), dtype = int)
    return game


# Function to check if considered move is valid or not
def isValidMove(game, row, col):
    if(game[row][col] == 0):
        return True
    else:
        return False
    

# Function to get all valid moves
def validMoves(game):
    nrows = game.shape[0]
    ncols = game.shape[1]
    moves = []
    for col in range(ncols):
        if(game[nrows-1][col] == 0):
            moves.append(col)
    return moves


# Function to place a piece on the game board given a player and a column 
# Returns 1 if the move was carried out else returns 0
def makeMove(game, player, col):
    for row in range(NROWS):
        # displayGame(game)
        # print(row, "   ",col)
        if(isValidMove(game, row, col)):
            game[row][col] = player
            lastMove = [row, col]
            return game, lastMove
    return game, [-1, -1]


# Function to display a given move
def dispMove(move):
    print("Last Move : ", move[0], ", ", move[1])


# Function to check if a particular player has won
def checkIfWon(game, player, lastMove):
    nrows = game.shape[0]
    ncols = game.shape[1]

    if(lastMove[0] == -1):
        return False

    # Checking for vertical connected 4
    if(lastMove[0] >= 3):
        count = 0
        col = lastMove[1]
        for row in range(lastMove[0], lastMove[0]-4, -1):
            if(game[row][col] == player):
                count += 1
            if(count >= 4):
                return True

    # Checking for horizontal connected 4
    count = 0
    row = lastMove[0]
    col = lastMove[1]
    while(col >= 0):
        if(game[row][col] == player):
            count += 1
            col -= 1
        else:
            break

    col = lastMove[1] + 1
    while(col < ncols):
        if(game[row][col] == player):
            count += 1
            col += 1
        else:
            break
    
    if(count >= 4):
        return True

    # Checking for bottom left to top right diagonal connected 4
    count = 0
    row = lastMove[0]
    col = lastMove[1]
    while(row < nrows and col < ncols and row >= 0 and col >= 0):
        if(game[row][col] == player):
            count += 1
            row += 1
            col += 1
        else:
            break

    
    row = lastMove[0]-1
    col = lastMove[1]-1

    while(row >= 0 and col >= 0 and row < nrows and col < ncols):
        if(game[row][col] == player):
            count += 1
            row -= 1
            col -= 1
        else:
            break

    if(count >= 4):
        return True

    # Checking for bottom right to top left diagonal connected 4
    count = 0
    row = lastMove[0]
    col = lastMove[1]
    while(row < nrows and col >= 0 and col < ncols and row >= 0):
        if(game[row][col] == player):
            count += 1
            row += 1
            col -= 1
        else:
            break

    row = lastMove[0]-1
    col = lastMove[1]+1

    while(row >= 0 and col < ncols and row < nrows and col >= 0):
        if(game[row][col] == player):
            count += 1
            row -= 1
            col += 1
        else:
            break

    if(count >= 4):
        return True

    return False


# Function to check if the game is a draw
def checkDraw(game):
    nrows = game.shape[0]
    ncols = game.shape[1]
    for col in range(ncols):
        if(game[nrows-1][col] == 0):
            return False
    return True


# Function to display current game state
def displayGame(game):
    nrows = game.shape[0]
    ncols = game.shape[1]
    print("Current Game board status: \n")
    for row in range(nrows-1, -1, -1):
        for col in range(ncols):
            print(game[row][col], end = "\t")
        print("\n")


# Function to copy current game state
def copyGame(game):
    g = createGame()
    for row in range(game.shape[0]):
        for col in range(game.shape[1]):
            g[row][col] = game[row][col]
    return g


# Function to reset the game to starting state with only zeros
def resetGame(game):
    game = np.zeros(game.shape, dtype = int)
    return game, [-1, -1]


class Node:
    def __init__(self, game, player, parent=None, column=None, C = sqrt(2)):
        self.column = column
        self.parent = parent
        self.player = player
        self.untriedMoves = validMoves(game)
        self.children = []
        self.validMoves=[]
        self.wins = 0
        self.visits = 0
        self.reward = 0
        self.C = C

    def uct(self):
        bestScore = 0
        bestChild = None
        c = self.C
        for child in self.children:
            if child.visits == 0 :
                score = 10000
            else:
                score = child.reward / child.visits + c*sqrt(log(self.visits) / child.visits)
            if (score > bestScore):
                bestChild = child
                bestScore = score
        return bestChild

    def addChild(self, col, state):
        child = Node(copyGame(state), self.player*(-1), parent=self, column=col, C = self.C)
        self.untriedMoves.remove(col)
        ncols = state.shape[1]
        for c in range(ncols):
            if(c in self.untriedMoves and not(c in validMoves(state))):
                self.untriedMoves.remove(c)
        # print(self.untriedMoves, "\t", col)
        self.children.append(child)
        return child

    # def addChildren(self, game):
        
    #     # self.untriedMoves.remove(col)
    #     ncols = game.shape[1]
    #     for c in range(ncols):
    #         child = Node(copyGame(game), self.player*(-1), parent=self, column=c)
    #         if(not(c in validMoves(game))):
    #             self.untriedMoves.remove(c)
    #             self.children.append(child)
    #             self.validMoves.append(c)
    #     # print(self.untriedMoves, "\t", col)
        
    #     # return child

    def update(self, result, reward):
        self.visits += 1
        self.wins += result
        self.reward += reward

    def dispNode(self):
        print("Column : ", self.column)
        print("Player : ", self.player)
        if(self.parent):
            print("Parent Column : ", self.parent.column)
        else:
            print("Parent Does not exist!")
        print("Untried Moves : ", self.untriedMoves)
        print("Children : ", self.children)
        print("Wins : ", self.wins)
        print("Reward : ", self.reward)
        print("Visits : ", self.visits)
        # time.sleep(2)
        
# def copyNode(node, state):
#     temp = Node(game = state, player = node.player, parent = node.parent, column = node.column)
#     temp.children = node.children
#     temp.untriedMoves = node.untriedMoves
#     temp.reward = node.reward
#     temp.visits = node.visits
#     temp.wins = node.wins
#     return temp



def MCTS(game, player, iter, root = None, lastMove = [-1, -1]):
     
    for it in range(iter):
        # print("MCTS iter : ", it)
        node = root
        state = copyGame(game)

        # Selection
        while (len(node.untriedMoves) == 0 and len(node.children) != 0):
            node = node.uct()
            if(node.column not in validMoves(state)):
                continue
            state, lastMove = makeMove(state, node.player, node.column)
            # node.untriedMoves.remove(lastMove[1])
            # if(lastMove[0] == -1):
            #     displayGame(state)
            #     node.dispNode()
            #     print("PROBLEM IS IN SELECTION")
            #     sys.exit()
            # print(" MCTS iter : ", it)
            # print("\n\nSELECTION!!!!!!!!!")
            # print("lastMove : ", dispMove(lastMove))
            # node.dispNode()
            # displayGame(state)
            # time.sleep(1)
            # os.system('cls')

        # Expansion
        if len(node.untriedMoves) != 0:
            ncols = game.shape[1]
            for c in range(ncols):
                if(c in node.untriedMoves and not(c in validMoves(state))):
                    node.untriedMoves.remove(c)
            if(len(node.untriedMoves) == 0):
                break
            col = random.choice(node.untriedMoves)
            state, lastMove = makeMove(state, node.player, col)
            # if(lastMove[0] == -1):
            #     displayGame(state)
            #     node.dispNode()
            #     print("PROBLEM IS IN EXPANSION")
            #     sys.exit()
            node = node.addChild(col, state)
            # print(" MCTS iter : ", it)
            # print("\n\nEXPANSION!!!!!!!!!")
            # print("lastMove : ", dispMove(lastMove))
            # node.dispNode
            # displayGame(state)
            # time.sleep(5)
            # os.system('cls')


            # if len(node.untriedMoves) != 0:
            # ncols = game.shape[1]
            # # for c in range(ncols):
            # #     if(c in node.untriedMoves and not(c in validMoves(game))):
            # #         node.untriedMoves.remove(c)
            # # if(len(node.untriedMoves) == 0):
            # #     break
            # node.addChildren(state)
            # col = random.choice(node.validMoves)
            # state, lastMove = makeMove(state, node.player, col)
            # if(lastMove[0] == -1):
            #     while True:
            #         print("PROBLEM IS IN EXPANSION")

            # node=node.children[col]
            
            
            
            # node.untriedMoves.remove(lastMove[1])
            
            # node = node.addChild(col, state)
            # print(" MCTS iter : ", it)
            # print("\n\nEXPANSION!!!!!!!!!")

        # Simulation
        while len(validMoves(state)) != 0 and not(checkDraw(state)) and not(checkIfWon(state, player, lastMove)):
            column = random.choice(validMoves(state))
            player *= -1
            state, lastMove = makeMove(state, player, column)
            # if(lastMove[0] == -1):
            #     print("PROBLEM IS IN SIMULATION")
            #     sys.exit()
            # print(" MCTS iter : cls", it)
            # print("\n\nSIMULATION!!!!!!!")
            # dispMove(lastMove)
            # displayGame(state)
            # if(checkIfWon(state, player, lastMove)):
            #     print("Player : ", player, " won")
            # if(checkDraw(state)):
            #     print("It is a draw")
            # time.sleep(1)
            # os.system('cls')

        # Backprop
        while node is not None:
            if(state[lastMove[0]][lastMove[1]] == player):
                if(checkDraw(state) == True):
                    node.update(0, 0.5)
                else:
                    node.update(1, 10)
            else:
                if(checkDraw(state) == True):
                    node.update(0, 0.5)
                else:
                    node.update(0, -5)
            # print("MCTS iter : ", it)
            # print("\n\nBACKPROPAGATION!!!!!!!!!")
            # node.dispNode()
            node = node.parent
    # root.dispNode()
    return root, root.uct().column


def playGame(numGame, iter1, iter2, C = sqrt(2)):
    game = createGame()
    node1 = Node(game, 1, C = C)
    node2 = Node(game, -1, C = C)
    col1 = -1
    col2 = -1
    lastMove1 = [-1, -1]
    lastMove2 = [-1. -1]
    playername1, playername2 = None, None
    player = 1
    if(numGame >= 50):
        playername1 = "MC40"
        playername2 = "MC200"
    else:
        playername1 = "MC200"
        playername2 = "MC40"
    while(True):
        if(player == 1):
            ncols = game.shape[1]
            state = game
            # for c in range(ncols):
            #     if(c in validMoves(state)):
            #         state, _ = makeMove(game, player, c)
            #         node1.addChild(c, state) 
            # print("\n\nPLAYER 1'S NODE INFO : \n\n")
            # node1.dispNode()
            # print("\n\n")
            node1, col1 = MCTS(copyGame(game), player, iter1, node1)
            game, lastMove1 = makeMove(game, player, col1)
            # print("\n\nGAME INFO : \n\nGame number : ", numGame)
            # print("Player 1 : " , playername1, " has played\n")
            # dispMove(lastMove1)
            # print("Col : ", col1)
            # displayGame(game)
            # if(lastMove1[0] == -1):
            #     print("lastMove became -1")
            #     sys.exit()
            # time.sleep(1)
            # os.system('cls')
            if(checkIfWon(game, player, lastMove1) == True):
                print("Player 1 : ", playername1, " has won!\n")
                if(playername1 == "MC40"):
                    return 1
                else:
                    return -1
            if(checkDraw(game) == True):
                print("This game is a draw!\n")
                return 0
            player *= -1
        else:
            node2, col2 = MCTS(copyGame(game), player, iter2, node2)
            # print("PLAYER 2'S NODE INFO : \n\n")
            # node2.dispNode()
            game, lastMove2 = makeMove(game, player, col2)
            # print("\n\n\nGAME INFO : \n\n\nGame Number : ", numGame)
            # print("Player 2 : " , playername2, " has played\n")
            # dispMove(lastMove2)
            # print("Col : ", col2)
            # displayGame(game)
            # if(lastMove1[0] == -1):
            #     print("lastMove became -1")
            #     sys.exit()
            # time.sleep(1)
            # os.system('cls')
            if(checkIfWon(game, player, lastMove2) == True):
                print("Player 2 : ", playername2, " has won!\n")
                if(playername2 == "MC40"):
                    return 1
                else:
                    return -1
            if(checkDraw(game) == True):
                print("This game is a draw!\n")
                return 0
            player *= -1


# def Qrandom():



# def playQgame(n, Q):
    


# def Qlearn(Q):


###############

def PrintGrid(positions):
    print('\n'.join(' '.join(str(x) for x in row) for row in positions))
    print()

def main():
    # mc200winratios = []
    # cvalues = []
    # for i in range(10, 20, 1):
    #     c = i/10
    #     cvalues.append(c)
    #     mc40wins = 0
    #     mc200wins = 0
    #     for numGame in tqdm(range(100)):
    #         print("\n")
    #         if(numGame < 50):
    #             result = playGame(numGame, ITER1, ITER2, c)
    #         else:
    #             result = playGame(numGame, ITER2, ITER1, c)
    #         if(result == 1):
    #             mc40wins += 1
    #         elif(result == -1):
    #             mc200wins += 1
    #     print("MC40 win ratio : ", mc40wins / 100)
    #     print("MC200 win ratio : ", mc200wins / 100)
    #     mc200winratios.append(mc200wins/100)
    
    # plt.plot(cvalues, mc200winratios, label = "mc200winratios vs cvalues")
    # plt.show()

    print("Enter part a or c for which you want the models to play : ")
    part = input()
    if(part == 'a'):
        mc40wins = 0
        mc200wins = 0
        for numGame in tqdm(range(100)):
            print("\n")
            if(numGame < 50):
                result = playGame(numGame, ITER1, ITER2)
            else:
                result = playGame(numGame, ITER2, ITER1)
            if(result == 1):
                mc40wins += 1
            elif(result == -1):
                mc200wins += 1
        print("MC40 win ratio : ", mc40wins / 100)
        print("MC200 win ratio : ", mc200wins / 100)

    elif(part == 'c'):
        Q = {}

    else:
        print("Invalid part")

    # game = createGame(6, 5)
    # print("Enter player (1 or -1) who will start: ")
    # player = int(input())
    # print("Player ", player, " will start!\n")
    # lastMove = [-1, -1]
    # while(not(checkIfWon(game, player, lastMove))):
    #     print("\nPlayer ", player, "Please enter a column to place token (Enter -1 to reset game): ")
    #     col = int(input())
    #     if(col >= game.shape[1]):
    #         print("Invalid column input!")
    #         continue
    #     if(col == -1):
    #         print("Resetting")
    #         game, lastMove = resetGame(game)
    #         displayGame(game)
    #         continue
    #     game, lastMove = makeMove(game, player, col)
    #     if(lastMove[0] == -1):
    #         print("\nInvalid Move!\n")
    #         continue
    #     displayGame(game)
    #     if(checkIfWon(game, player, lastMove)):
    #         print("Player ", player, " has won!")
    #         break
    #     if(checkDraw(game)):
    #         print("It is a draw!")
    #         break
    #     player *= -1
    
    # print("************ Sample output of your program *******")

    # game1 = [[0,0,0,0,0],
    #       [0,0,0,0,0],
    #       [0,0,1,0,0],
    #       [0,2,2,0,0],
    #       [1,1,2,2,0],
    #       [2,1,1,1,2],
    #     ]


    # game2 = [[0,0,0,0,0],
    #       [0,0,0,0,0],
    #       [0,0,1,0,0],
    #       [1,2,2,0,0],
    #       [1,1,2,2,0],
    #       [2,1,1,1,2],
    #     ]

    
    # game3 = [ [0,0,0,0,0],
    #           [0,0,0,0,0],
    #           [0,2,1,0,0],
    #           [1,2,2,0,0],
    #           [1,1,2,2,0],
    #           [2,1,1,1,2],
    #         ]

    # print('Player 2 (Q-learning)')
    # print('Action selected : 2')
    # print('Value of next state according to Q-learning : .7312')
    # PrintGrid(game1)


    # print('Player 1 (MCTS with 25 playouts')
    # print('Action selected : 1')
    # print('Total playouts for next state: 5')
    # print('Value of next state according to MCTS : .1231')
    # PrintGrid(game2)

    # print('Player 2 (Q-learning)')
    # print('Action selected : 2')
    # print('Value of next state : 1')
    # PrintGrid(game3)
    
    # print('Player 2 has WON. Total moves = 14.')
    
if __name__=='__main__':
    main()