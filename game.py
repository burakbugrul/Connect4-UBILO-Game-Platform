from player import Player
from time import sleep
import requests
import json

class Game:

    def __init__(self, n=8, m=9, time_limit=3):

        self.players = []
        self.symbols = ["X", "O", "-"]  # X -> first player, O -> second player, - -> empty cell
        self.winner = -1

        if not isinstance(time_limit, int):
            time_limit = 2
        if not isinstance(n, int):
            n = 7
        if not isinstance(m, int):
            m = 8

        self.n = n
        self.m = m
        self.time_limit = time_limit
        self.table = [[self.symbols[-1]] * m for _ in range(n)]

    def get_players(self):

        for i in range(2):

            path = input(f"Enter the executable path of Player {i}: ")
            name = path
            input_path = f"{i}.in"

            player = Player(name, path, input_path, i)

            self.players.append(player)

    def write_table(self, player):

        with open(player.input_path, "w") as f:
            f.write(' '.join(map(str, [self.n, self.m, self.symbols[player.id], self.symbols[player.id ^ 1],
                                       self.symbols[-1], self.time_limit])))
            f.write('\n')

            for row in self.table:
                f.write(' '.join(row))
                f.write('\n')

    def make_move(self, column, symbol):

        empty = self.symbols[-1]

        if not ( 0 <= column < self.m ):
            return False

        if self.table[0][column] != empty:
            return False

        for i in range(self.n):
            if i == self.n - 1 or self.table[i + 1][column] != empty:
                self.table[i][column] = symbol
                break

        return True

    def check_winning(self):

        for i in range(self.n - 3):
            for j in range(self.m - 3):
                for func in [lambda place: [place[0] + 1, place[1]], lambda place: [place[0], place[1] + 1],
                             lambda place: [place[0] + 1, place[1] + 1]]:

                    s = set()
                    p = [i, j]

                    for _ in range(4):
                        s.add(self.table[p[0]][p[1]])
                        p = func(p)

                    if len(s) == 1 and list(s)[0] != self.symbols[-1]:
                        return True

        return False

    def check_tie(self):

        for i in range(self.n):
            if self.table[i].count(self.symbols[-1]) > 0:
                return False

        return True

    def print_table(self):

        for i in range(self.n):
            print(' '.join(self.table[i]))

        print('-' * (self.m + 1))

    def play(self):

        turn = 0
        self.winner = "TIE"
        cnt = 0

        requests.post('https://us-central1-ubilo-connect-4.cloudfunctions.net/set_current_game',
                      json={
                          "player0": self.players[0].name,
                          "player1": self.players[1].name
                      })

        while not self.check_tie():

            cnt += 1

            self.write_table(self.players[turn])

            try:

                column = self.players[turn].play_turn(self.time_limit)

                requests.post('https://us-central1-ubilo-connect-4.cloudfunctions.net/update_current_game',
                              json={
                                  "turn": cnt,
                                  "column": column
                              })
            except:

                self.winner = self.players[turn ^ 1].name
                print("Couldn't get user output")

                requests.post('https://us-central1-ubilo-connect-4.cloudfunctions.net/update_current_game',
                              json={
                                  "turn": cnt,
                                  "column": -1
                              })
                break

            if not self.make_move(column, self.symbols[self.players[turn].id]):
                self.winner = self.players[turn ^ 1].name
                break

            self.print_table()

            if self.check_winning():
                self.winner = self.players[turn].name
                break

            sleep(1)

            turn ^= 1

        print(f"THE WINNER IS {self.winner}" if self.winner != "TIE" else "IT IS A TIE :(")
        print(f"Number of turns: {cnt}")

        flags = [False, False]

        game = {
            "player0": self.players[0].name,
            "player1": self.players[1].name,
            "winner": self.winner,
            "turns": cnt,
            "scoreboard": "ubilowinter19"
        }

        if self.players[0].name != self.players[1].name:

            print("Updating the scoreboard")

            while True:

                if not flags[0]:

                    resp = requests.post('https://us-central1-ubilo-connect-4.cloudfunctions.net/add_game_result',
                                         json=game)

                    if json.loads(resp.text)["status"] == "success":
                        flags[0] = True

                if not flags[1]:

                    resp = requests.post('https://us-central1-ubilo-connect-4.cloudfunctions.net/update_scoreboard',
                                         json=game)

                    if json.loads(resp.text)["status"] == "success":
                        flags[1] = True

                if flags[0] & flags[1]:
                    break

            print("Scoreboard is updated.")
