# coding=utf-8
from Game import Game


def get_player_answer(question, default_value=None, is_num=True):
    while True:
        try:
            ans = raw_input(question)
            if ans == '' and default_value is not None:
                return default_value
            if is_num:
                return int(ans)
            else:
                return ans
        except:
            print "Please enter valid value!"


if __name__ == '__main__':
    width_count = get_player_answer("Please enter width count (default: 10):", 10)
    height_count = get_player_answer("Please enter height count (default: 10):", 10)
    mine_count = get_player_answer("Please enter height count (default: 9):", 9)

    if width_count * height_count < mine_count :
        print "mine count is not more than grid count!!"
        exit(1)

    game = Game(width_count, height_count, mine_count)
    game.run()
