import numpy as np
import copy

class UltTTT():

    #####################
    # Terminology
    #
    # Board     - Entire 9x9 playing board with all individual Xs, Os, and free spaces
    # Box       - One of the 9 indiviual 3x3 playing areas within the overall board
    # Big Board - Higher level 3x3 playing board, represents won and contested boxes on the overall playing board
    #
    ######################

    def __init__(self):
        
        self._board = np.zeros((9,9), dtype=np.int8)
        self._big_board = np.zeros((3,3), dtype=np.int8)
        self._play_box = -1
        self._first_players_turn = True
        self._winner = ""
        self._finished = False

    def get_box(self, board_num):
        board_x = int(board_num / 3) * 3
        board_y = (board_num % 3) * 3
        square = np.array(self._board[board_x:board_x+3, board_y:board_y+3])
        return square

    def get_moves(self):
        if self._finished:
            return []
        if self._play_box >= 0:
            board_x = int(self._play_box / 3) * 3
            board_y = int(self._play_box % 3) * 3
            return (np.argwhere(self._board[board_x:board_x+3, board_y:board_y+3] == 0) + [board_x, board_y])
        else:
            return np.argwhere(self._board == 0)

    def make_move(self, move: np.ndarray):
        # print()
        # print(self._board)
        # print(self._big_board)
        # print(f"Turn: Player {1 if self._first_players_turn else 2}")
        # print(f"Move: {move}")

        if self._finished:
            print(f"No moves to play. Player {1 if self._first_players_turn else 2} won the game!")
            # print(self._board)
            # print(self._big_board)
            # exit(1)
            return self._board, self._big_board, self._play_box

        legal_moves = self.get_moves()
        if len(legal_moves) == 0:
            self._finished = True
            self.winner = "Draw"
            return self._board, self._big_board, self._play_box
        
        is_legal_move = any(np.array_equal(move, legal_move) for legal_move in legal_moves)
        if not is_legal_move:
            print(f"Invalid Move {move}!\nLegal Moves:\n{legal_moves}")
            return self._board, self._big_board, self._play_box

        # Update the board with the move    
        self._board[move[0]][move[1]] = 2 if self._first_players_turn else -2  

        # Update the game state
        box_status = self.check_box(self.get_box(board_num=self._play_box if self._play_box != -1 else int(move[0] / 3) * 3 + int(move[1] / 3)))
        if box_status == "win":
            self._big_board[int(move[0] / 3)][int(move[1] / 3)] = 2 if self._first_players_turn else -2
            if self.check_box(self._big_board) == "win":
                self._finished = True
                self._winner = "Player 1" if self._first_players_turn else "Player 2"
                return self._board, self._big_board, self._play_box
            elif self.check_box(self._big_board) == "draw":
                self._finished = True
                self._winner = "Draw"
                return self._board, self._big_board, self._play_box
        elif box_status == "draw":
            self._big_board[int(move[0] / 3)][int(move[1] / 3)] = 1
            if self.check_box(self._big_board) == "draw":
                self._finished = True
                self._winner = "Draw"
                return self._board, self._big_board, self._play_box

        if self._big_board[move[0] % 3][move[1] % 3] != 0:
            self._play_box = -1
        else:
            self._play_box = ((move[0] % 3) * 3)  + (move[1] % 3)

        self._first_players_turn = not self._first_players_turn

        # print(self._board)
        # print(self._big_board)

        return self._board, self._big_board, self._play_box
            
    def make_move_copy(self, move: np.ndarray):
        new_game = copy.deepcopy(self)
        new_game.make_move(move)
        return new_game

    def check_box(self, board):
        for i in range(3):
            if abs(np.sum(board[i])) == 6:
                return "win"
            if abs(np.sum(board[0:3, i])) == 6:
                return "win"
        if abs(board[0][0] + board[1][1] + board[2][2]) == 6:
            return "win"
        if abs(board[0][2] + board[1][1] + board[2][0]) == 6:
            return "win"
        
        if len(np.argwhere(board)) == 9:
            return "draw"

        return "none"
    
    def gen_box_string(self, box_num):
        big_box = self._big_board[int(box_num / 3)][box_num % 3]
        box_str = ""
        if big_box == 0:
            box = self.get_box(box_num)
            for i in range(len(box)):
                for j in range(len(box[i])):

                    if j != 0:
                        box_str += "│ "
                    else:
                        box_str += "  "

                    if box[i][j] == 0:
                        box_str += " "
                    elif box[i][j] == 2:
                        box_str += "X"
                    elif box[i][j] == -2:
                        box_str += "O"
                    
                    box_str += " "

                if i != 2:
                    box_str += "\n "
                    box_str += "───┼───┼───\n"

        elif big_box == 2:
            box_str ="""  ___   ___ 
  \  \ /  / 
   \  '  /  
   /  .  \  
  /__/ \__\ """
            # box_str = textwrap.dedent(box_str)
        elif big_box == -2:
            box_str = """    _____   
   / ___ \  
  | |   | | 
  | |___| | 
   \_____/  """
        elif big_box == 1:
            box_str = """            
   _______  
  |_______| 
            
            """

        return box_str

    def display_board(self):
        box = 0
        for i in range(3):
            print("               ║               ║              ")
            row_string_arr = " \n \n \n \n \n \n \n \n \n \n \n"
            for j in range(3):
                box_str = self.gen_box_string(box)
                if j != 2:
                    row_string_arr = "\n".join([x + y + "  ║ " for x,y in zip(row_string_arr.splitlines(), box_str.splitlines()) ])
                else:
                    row_string_arr = "\n".join([x + y + "  " for x,y in zip(row_string_arr.splitlines(), box_str.splitlines()) ])
                box += 1
            print(row_string_arr)
            if int(self._play_box / 3) != i or self._play_box < 0: 
                print("               ║               ║              ")
            else:
                under_string = ""
                highlight = self._play_box % 3
                for x in range(3):
                    if x != highlight:
                        under_string += "               ║"
                    else:
                        under_string += " ^^^^^^^^^^^^^ ║"
                print(under_string[:-1])
            if i != 2:
                print("═══════════════╬═══════════════╬═══════════════")

    def play_game(self):
        while not self._finished:
            self.display_board()
            print()
            move_input = 0
            box_input = self._play_box
            if self._play_box >= 0:
                print(f"Play Box: {self._play_box}")
                print(f"Player {1 if self._first_players_turn else 2}'s Turn")
                move_input = int(input(f"Move: "))
            else:
                print("Play Box: Any")
                print(f"Player {1 if self._first_players_turn else 2}'s Turn")
                box_input = int(input("Please select a play box: "))
                move_input = int(input(f"Move: "))
            self.make_move(np.array([int(box_input/ 3)*3 + (int(move_input / 3)), (box_input % 3) * 3 + (move_input % 3) ]))
        self.display_board()
        print()
        print(f"Player {1 if self._first_players_turn else 2} Wins!")

                

def main():
    var = UltTTT()
    var.play_game()



if __name__ == "__main__":
    main()