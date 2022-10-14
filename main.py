# coding=utf-8
from Computer import Computer
from Game import Game
from Player import Player
from View import View

if __name__ == '__main__':
    view = View(0, 0)
    width_count = view.GetPlayerAnswer("Please enter width count (default: 10):", 10)
    height_count = view.GetPlayerAnswer("Please enter height count (default: 10):", 10)
    mine_count = view.GetPlayerAnswer("Please enter mine count (default: 9):", 9)

    if width_count * height_count < mine_count:
        print "mine count is not more than grid count!!"
        exit(1)

    game = Game(width_count, height_count, mine_count)
    game.Join(Player("Player1"))
    game.Join(Computer("Computer"))
    game.Run()
