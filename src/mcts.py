from ultimatetictactoe import UltTTT
import numpy as np
import math
import copy
import random
import time

class MCTS_Node():
    pass

class MCTS_Node():
    def __init__(self, state:UltTTT, parent=None, action=None, first_player=True, exploration_constant=0.1, sim_policy=None):
        self.state = state
        self.parent = parent
        self.action = action
        self.first_player = first_player
        self.exploration_constant = exploration_constant
        self.sim_policy = sim_policy
        self.children = []
        self.visits = 0
        self.value = 0.0
        self.unexplored_moves = np.random.default_rng().permutation(self.state.get_moves())

    def is_fully_explored(self):
        return len(self.unexplored_moves) == 0
        
    def add_unexplored_child(self):
        new_action = self.unexplored_moves[0]
        new_state = self.state.make_move_copy(new_action)
        new_node = MCTS_Node(state=new_state, parent=self, action=new_action, first_player=(not self.first_player), exploration_constant=self.exploration_constant, sim_policy=self.sim_policy)
        self.children.append(new_node)
        self.unexplored_moves = self.unexplored_moves[1:]
        return new_node

    def get_uct_child(self):
        ucts = np.zeros(len(self.children))
        for i in range(len(self.children)):
            child = self.children[i]
            value = child.value if self.first_player else -child.value
            ucts[i] = value + (self.exploration_constant * (math.sqrt(math.log(self.visits) / child.visits)))
        return self.children[np.argmax(ucts)]
    
    def choose_child(self):
        if not self.is_fully_explored():
            return self.add_unexplored_child()
        else:
            if len(self.children):
                return self.get_uct_child()
            else:
                return self
        
    def simulate(self):
        sim_game = copy.deepcopy(self.state)
        while(not sim_game._finished):
            try:
                move = self.sim_policy(sim_game)
                if sim_game._finished:
                    print("WTF")
                sim_game.make_move(move)
            except Exception as e:
                print(sim_game._board)
                print(sim_game._big_board)
                print(np.argwhere(sim_game._big_board))
                exit(0)
        ### All-or-nothing value
        if sim_game._winner == "Player 1": return 1
        elif sim_game._winner == "Player 2": return -1
        return 0
        ###
        ### Boxes + winner value
        # val = 0
        # for i in range(len(sim_game._big_board)):
        #     for j in range(len(sim_game._big_board[i])):
        #         if abs(sim_game._big_board[i][j]) == 2: 
        #             val += sim_game._big_board[i][j] / 2
        # if sim_game._winner == "Player 1": return val + 9
        # elif sim_game._winner == "Player 2": return val - 9
        # return val
        ###


    def backpropogate(self, node, reward):
        node.visits += 1
        node.value += ((reward - node.value) / node.visits)
        if node.parent:
            node.backpropogate(node.parent, reward)

    def traverse(self):
        if self.visits == 0:
            return self
        elif self.state._finished:
            return self
        else:
            return self.choose_child().traverse()
        
    def select_move(self):
        if len(self.children):
            return max(self.children, key=lambda c: c.visits).action
        else:
            return self.sim_policy(self.state)

def random_uniform_rollout_policy(state:UltTTT) -> np.ndarray:
    return random.choice(state.get_moves())


def play_bot(bot_time=20, player_turn="random"):
    game = UltTTT()
    thinking_time = bot_time
    bot_first = True
    if player_turn == "random":
        bot_first = random.random() > 0.5
    elif player_turn == "first":
        bot_first = False
    while not game._finished:
        if (bot_first and game._first_players_turn) or (not bot_first and not game._first_players_turn):
            game.display_board()
            print()
            box_input = game._play_box
            if game._play_box >= 0:
                print(f"Play Box: {game._play_box}")
            else:
                print("Play Box: Any")
            print(f"Bot's Turn")
            root = MCTS_Node(state=game, first_player=game._first_players_turn, exploration_constant=2, sim_policy=random_uniform_rollout_policy)
            start_time = time.time()
            finished = False
            while(not finished):
                node = root.traverse()
                node.backpropogate(node, node.simulate())
                finished = (time.time() - start_time) > thinking_time
            # root.children.sort(key=lambda c: c.visits, reverse=True)
            # for child in root.children:
            #     print(f"Move: {child.action} | Visits: {child.visits:>4}, Value: {child.value:>6.2}")
            bot_move = root.select_move()
            print(f"Move: {root.select_move()}")
            game.make_move(bot_move)
        else:
            game.display_board()
            print()
            box_input = game._play_box
            if game._play_box >= 0:
                print(f"Play Box: {game._play_box}")
                print(f"Human's Turn")
                move_input = int(input(f"Move: "))
            else:
                print("Play Box: Any")
                print(f"Human's Turn")
                box_input = int(input("Please select a play box: "))
                move_input = int(input(f"Move: "))
            game.make_move(np.array([int(box_input/ 3)*3 + (int(move_input / 3)), (box_input % 3) * 3 + (move_input % 3) ]))


def test():
    game = UltTTT()
    thinking_time = 20
    game.make_move(np.array([4,4]))
    root = MCTS_Node(state=game, first_player=False, exploration_constant=2, sim_policy=random_uniform_rollout_policy)
    start_time = time.time()
    finished = False
    while(not finished):
        node = root.traverse()
        node.backpropogate(node, node.simulate())
        finished = (time.time() - start_time) > thinking_time
    root.children.sort(key=lambda c: c.visits, reverse=True)
    for child in root.children:
        print(f"Move: {child.action} | Visits: {child.visits:>4}, Value: {child.value:>6.2}")
    print(root.select_move())

def main():
    play_bot()


if __name__ == "__main__":
    main()
    # test()