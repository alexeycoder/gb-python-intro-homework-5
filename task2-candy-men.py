# Создайте программу для игры с конфетами человек против человека.
# 1) Добавьте игру против бота
# 2) Подумайте как наделить бота 'интеллектом'
# *Правила:* На столе лежит 150 конфет. Играют два игрока делая ход друг после друга.
# Первый ход определяется жеребьёвкой. За один ход можно забрать не более чем 28 конфет.
# Все конфеты оппонента достаются сделавшему последний ход.
# Сколько конфет нужно взять первому игроку, чтобы забрать все конфеты у своего конкурента?

from enum import Enum
import time
import random
import common
from common import ForeColor, BackColor
from common import Console as Con

# turn on ansi escape sequences in win cmd :

Con.activate_ansi_esc_seq_in_win_cmd()

# consts:

CANDIES_TOTAL = 150
CANDIES_PER_TURN = 28


# types:

class DifficultyLevel(Enum):
    EASY = 0
    HARD = 1


class Gamer(Enum):
    HUMAN = 0
    AI = 1

    @staticmethod
    def get_next(gamer):
        match gamer:
            case Gamer.HUMAN:
                return Gamer.AI
            case Gamer.AI:
                return Gamer.HUMAN


class CandyGame:
    __fore_colors = {Gamer.HUMAN: ForeColor.BRIGHT_CYAN,
                     Gamer.AI: ForeColor.BRIGHT_MAGENTA}

    def __init__(self, candies_total, candies_per_turn, difficulty: DifficultyLevel) -> None:
        self.candies_total = candies_total
        self.candies_per_turn = candies_per_turn
        self.difficulty_level = difficulty
        self.whose_turn = Gamer.HUMAN
        self.turns_count = 0
        self.range_str = f'от 1 до {candies_per_turn}'
        self.gameover = False
        self.winner = None

    @staticmethod
    def __print_horizontal_line():
        console_width, _ = Con.get_size()
        print('\n'+'\u2508'*console_width)

    @staticmethod
    def __to_readable(number):
        if number == 1 or (number > 20 and (number % 10) == 1):
            return '1 конфету'
        elif number in [2, 3, 4] or (number > 20 and (number % 10) in [2, 3, 4]):
            return f'{number} конфеты'
        else:
            return f'{number} конфет'

    def __get_candies_to_take_optimum(self):
        optimum = self.candies_total % (self.candies_per_turn + 1)
        if optimum == 0:
            return None
        return optimum

    def toss_who_goes_first(self):
        CandyGame.__print_horizontal_line()
        self.whose_turn = random.choice([Gamer.HUMAN, Gamer.AI])
        print(Con.format('Жеребьёвка:', italic=True))
        if self.whose_turn == Gamer.HUMAN:
            print(Con.format('Вам достаётся первый ход!',
                  bold=True, fore_color=ForeColor.BRIGHT_WHITE))
        else:
            print(Con.format('Вы ходите вторым!', bold=True,
                  fore_color=ForeColor.BRIGHT_WHITE))

    def __go_turn(self):
        CandyGame.__print_horizontal_line()

        whose_turn = self.whose_turn
        fcolor = CandyGame.__fore_colors[whose_turn]
        self.gameover = self.candies_total <= self.candies_per_turn
        self.winner = whose_turn
        candies_to_take = 0
        self.turns_count += 1
        print(f'{self.turns_count}. ', end='')

        if whose_turn == Gamer.HUMAN:
            # HUMAN
            print(Con.format('Ваш ход', bold=True, italic=True,
                  underline=True, fore_color=fcolor))
            if self.gameover:
                print(
                    f'Число оставшихся конфет {self.candies_total} меньше чем можно взять за ход.')
                print(Con.format('Поздравляю, вы победитель! \U0001F37E',
                                 bold=True, italic=True, fore_color=ForeColor.BRIGHT_GREEN))
                return

            print(f'Осталось конфет: {self.candies_total}', end='')
            hint_value = self.__get_candies_to_take_optimum()
            if hint_value is None:
                print()
            else:
                hint_value_str = CandyGame.__to_readable(hint_value)
                print(Con.format(f' (Подсказка: возмите {hint_value_str})',
                                 italic=True, fore_color=ForeColor.GRAY))

            candies_to_take = common.get_user_input_int_range(
                f'Сколько забираете конфет ({self.range_str})?: ', 1, self.candies_per_turn)
        else:
            # AI
            print(Con.format('Ход ИИ', bold=True, italic=True,
                  underline=True, fore_color=fcolor))

            if self.gameover:
                print(
                    f'Число оставшихся конфет {self.candies_total} меньше чем можно взять за ход.')
                print(Con.format('Игра окончена. Вы проиграли \U0001F479',
                                 bold=True, italic=True, fore_color=ForeColor.BRIGHT_RED))
                return

            print(f'Осталось конфет: {self.candies_total}')
            if self.difficulty_level == DifficultyLevel.EASY:
                candies_to_take = random.randint(1, self.candies_per_turn)
            else:
                candies_to_take = self.__get_candies_to_take_optimum()
                if candies_to_take is None:
                    candies_to_take = random.randint(1, self.candies_per_turn)

            time.sleep(0.5)
            print(f'ИИ забирает {CandyGame.__to_readable(candies_to_take)}')

        self.candies_total -= candies_to_take
        self.whose_turn = Gamer.get_next(whose_turn)

    def run(self):
        while not self.gameover:
            self.__go_turn()


# main flow:

user_answer = True

while(user_answer):
    Con.clear()
    common.print_title('Игра "Отбери все конфетки", версия 1.0',
                       fore_color=ForeColor.BRIGHT_WHITE)

    dif_lvl = common.get_user_input_int_range('Задайте уровень сложности: '
                                              '\n\t0 \u2014 лёгкий,\n\t1 \u2014 сложный\n?: ',
                                              0, 1)

    game = CandyGame(CANDIES_TOTAL, CANDIES_PER_TURN, DifficultyLevel(dif_lvl))
    game.toss_who_goes_first()
    game.run()

    print()
    user_answer = common.ask_for_repeat()
