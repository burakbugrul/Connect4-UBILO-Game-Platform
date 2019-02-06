import os
import subprocess


class Player:

    def __init__(self, name, path, input_path, id):
        self.name = name
        self.path = path
        self.input_path = input_path
        self.id = id

    def play_turn(self, time_limit):

        input_file = open(f"{self.input_path}", "r")
        output_file = open("out.txt", "w")

        cp = subprocess.run([f"./{self.path}"], stdin=input_file, stdout=output_file, timeout=time_limit)

        if cp.returncode != 0:
            cp.check_returncode()

        input_file.close()
        output_file.close()

        with open("out.txt", "r") as f:
            column = int(f.read())

        print()
        print(self.name, column)
        return column
