import time
import random
from enum import Enum
import common
from common import ForeColor, BackColor
from common import Console as Con

# turn on ansi escape sequences in win cmd :

Con.activate_ansi_esc_seq_in_win_cmd()

# consts:

WARN_OUT_OF_RANGE = 'Некорректный ввод: Размер поля не должен быть меньше 2-х! ' + \
    common.PLEASE_REPEAT
DIM = 3
GAMERS_FORE_COLORS = [ForeColor.BRIGHT_YELLOW, ForeColor.BRIGHT_CYAN]
GAMERS_BACK_COLORS = [None, None]
WINNERS_FORE_COLORS = [ForeColor.BLACK, ForeColor.BLACK]
WINNERS_BACK_COLORS = [BackColor.BRIGHT_YELLOW, BackColor.BRIGHT_CYAN]


# types:

class CellState(Enum):
    EMPTY = -1
    O = 0
    X = 1


class TableSymb:
    HORIZ = '\u2550'
    VERT = '\u2551'

    TOP_LEFT = '\u2554'
    TOP_RIGHT = '\u2557'
    TOP_TO_VERT = '\u2566'

    BTM_LEFT = '\u255a'
    BTM_RIGHT = '\u255d'
    BTM_TO_VERT = '\u2569'

    LEFT_TO_HORIZ = '\u2560'
    RIGHT_TO_HORIZ = '\u2563'

    CROSS = '\u256c'


class DifficultyLevel(Enum):
    EASY = 0
    HARD = 1


class GameDesk:
    X_NAME = ' крестики '
    O_NAME = ' нолики '
    X_SYMBOL = 'X'
    O_SYMBOL = 'O'
    __CELL_PADDING = 3
    __WANR_INCORRECT_CELL_NUM = 'Некорректный ввод: Требуется ввести номер свободной ячейки игрового поля! ' + common.PLEASE_REPEAT

    def __init__(self, dimension: int, difficulty: DifficultyLevel) -> None:
        self.gameover = False
        self.winner = CellState.EMPTY.value
        self.__winner_indices = []
        self.gamers_fore_colors = GAMERS_FORE_COLORS
        self.gamers_back_colors = GAMERS_BACK_COLORS
        self.winners_fore_colors = WINNERS_FORE_COLORS
        self.winners_back_colors = WINNERS_BACK_COLORS
        self.whose_turn = CellState.X.value
        self.human = CellState.X.value
        self.difficulty_level = difficulty

        self._dim = max(dimension, 2)
        self.__desk = [CellState.EMPTY for _ in range(dimension * dimension)]

        horizontals = [list(range(dimension*row, dimension * (row+1)))
                       for row in range(dimension)]
        verticals = [list(range(col, col+dimension*(dimension-1)+1, dimension))
                     for col in range(dimension)]
        diag_main = [[i * dimension+i for i in range(dimension)]]
        diag_minor = \
            [[i for i in range(dimension-1, dimension *
                               (dimension-1)+1, dimension-1)]]
        self.__scanlines = horizontals + verticals + diag_main + diag_minor
        self.__con_pos_stored = False

    def __check_for_winner(self):
        for scanline in self.__scanlines:
            states = {self.__desk[idx] for idx in scanline}
            if len(states) == 1 and states != {CellState.EMPTY}:
                self.__winner_indices = scanline
                self.gameover = True
                self.winner = list(states)[0].value
                return
                # return (winner, scanline)
        if self.__desk.count(CellState.EMPTY) == 0:
            self.gameover = True
            self.winner = CellState.EMPTY.value
            # return (winner, None)
        # return None

    @staticmethod
    def __cell_name_by_index(index):
        return str(index+1)

    def __get_cell_string(self, index, h_size, placeholder_mode=False):
        is_winner_cell = self.gameover and index in self.__winner_indices
        cell_value = self.__desk[index]
        cell_string = ' ' * h_size
        if cell_value == CellState.EMPTY:
            if not placeholder_mode:
                cell_string = GameDesk.__cell_name_by_index(
                    index).center(h_size)
        else:
            gamer_idx = cell_value.value
            if not placeholder_mode:
                cell_string = GameDesk.X_SYMBOL.center(h_size) \
                    if cell_value == CellState.X \
                    else GameDesk.O_SYMBOL.center(h_size)
            fore_color = self.winners_fore_colors[gamer_idx] if is_winner_cell else self.gamers_fore_colors[gamer_idx]
            back_color = self.winners_back_colors[gamer_idx] if is_winner_cell else self.gamers_back_colors[gamer_idx]
            cell_string = Con.format(
                cell_string, bold=True, blink=is_winner_cell, fore_color=fore_color, back_color=back_color)

        return cell_string

    def __render_gamers_state(self, highlighted_gamer):
        x_name = GameDesk.X_NAME
        o_name = GameDesk.O_NAME
        legend_length = 1 + len(x_name) + len(o_name)

        if highlighted_gamer == CellState.X.value:
            sec_gamer = CellState.O.value
            x_name = Con.format(x_name, bold=True, italic=True,
                                fore_color=self.winners_fore_colors[highlighted_gamer], back_color=self.winners_back_colors[highlighted_gamer])
            o_name = Con.format(o_name, bold=True, italic=True,
                                fore_color=self.gamers_fore_colors[sec_gamer], back_color=self.gamers_back_colors[sec_gamer])
        elif highlighted_gamer == CellState.O.value:
            sec_gamer = CellState.X.value
            o_name = Con.format(o_name, bold=True, italic=True,
                                fore_color=self.winners_fore_colors[highlighted_gamer], back_color=self.winners_back_colors[highlighted_gamer])
            x_name = Con.format(x_name, bold=True, italic=True,
                                fore_color=self.gamers_fore_colors[sec_gamer], back_color=self.gamers_back_colors[sec_gamer])
        Con.center_cursor_h(-legend_length//2)
        print(f'{x_name}|{o_name}')

    def __print_row(self, index_from, cell_h_size, center=False):
        dim = max(2, self._dim)
        mids_plus_one = dim - 1
        hoziz_line = TableSymb.HORIZ * cell_h_size

        value_line = TableSymb.VERT
        for i in range(index_from, index_from + dim):
            value_line += self.__get_cell_string(i, cell_h_size) \
                + TableSymb.VERT

        placeholder_line = TableSymb.VERT
        for i in range(index_from, index_from + dim):
            placeholder_line += self.__get_cell_string(i, cell_h_size, True) \
                + TableSymb.VERT

        upper_frame = ''
        bottom_frame = ''
        if index_from == 0:
            upper_frame = TableSymb.TOP_LEFT + hoziz_line \
                + mids_plus_one * (TableSymb.TOP_TO_VERT + hoziz_line) \
                + TableSymb.TOP_RIGHT
        else:
            upper_frame = TableSymb.LEFT_TO_HORIZ + hoziz_line \
                + mids_plus_one * (TableSymb.CROSS + hoziz_line) \
                + TableSymb.RIGHT_TO_HORIZ

            if index_from == dim*(dim-1):
                bottom_frame = TableSymb.BTM_LEFT + hoziz_line \
                    + mids_plus_one * (TableSymb.BTM_TO_VERT + hoziz_line) \
                    + TableSymb.BTM_RIGHT

        def do_margin(): pass
        if center:
            (columns, _) = Con.get_size()
            left_margin = max(0, (columns - len(upper_frame))//2)
            if left_margin > 0:
                def do_margin():
                    Con.move_cursor(left_margin)

        do_margin()
        print(upper_frame)
        do_margin()
        print(placeholder_line)
        do_margin()
        print(value_line)
        do_margin()
        print(placeholder_line)
        if bottom_frame != '':
            do_margin()
            print(bottom_frame)

    def __render(self, center=False):

        self.__render_gamers_state(self.whose_turn)

        last_cell_number = len(self.__desk)
        cell_h_size = len(str(last_cell_number))+2*GameDesk.__CELL_PADDING
        if cell_h_size % 2 == 0:
            cell_h_size -= 1

        for row_index in range(self._dim):
            cell_index_from = row_index * self._dim
            self.__print_row(cell_index_from, cell_h_size, center)

    def toss_who_human(self, iterations, pause_sec=0.1):  # жребий кем играть пользщвателю
        common.print_centered('Жеребъёвка кем будет играть пользователь:')
        gamers = [CellState.O.value, CellState.X.value]
        for _ in range(iterations):
            self.__render_gamers_state(self.human)
            time.sleep(pause_sec)
            Con.move_cursor(0, -1)
            # Con.clear_line()
            self.human = random.choice(gamers)
        self.__render_gamers_state(self.human)

        which_symbol = 'крестиками' if self.human == CellState.X.value else 'ноликами'
        common.print_centered(f'Пользователь играет {which_symbol}!')
        common.print_centered('Первыми начинают ходить крестики.'
                              ' Нажмите Enter чтобы начать...', end='')
        input()
        Con.move_cursor(0, -4)
        Con.clear_below_cursor()

    def __find_optimum_cell_index(self, opponent_cell_state: CellState):
        max_filled_cells_by_opponent = 0
        max_filled_cells_indexes = None
        for scanline in self.__scanlines:
            scanline_cells_values = [self.__desk[idx] for idx in scanline]
            empty_count = scanline_cells_values.count(CellState.EMPTY)
            if empty_count > 0:
                i_count = scanline_cells_values.count(opponent_cell_state)
                if i_count > max_filled_cells_by_opponent:
                    max_filled_cells_by_opponent = i_count
                    max_filled_cells_indexes = scanline
        if max_filled_cells_indexes is None:
            return None

        for i in max_filled_cells_indexes:
            if self.__desk[i] == CellState.EMPTY:
                return i

    def __go_turn(self):
        # определяем чей ход:
        human = self.human
        whose_turn = self.whose_turn
        gamers = {CellState.O.value, CellState.X.value}
        opponent = (gamers - {whose_turn}).pop()
        gamer_mark = CellState(whose_turn)

        empty_cell_indexes = [idx for idx, cell_val in enumerate(
            self.__desk) if cell_val == CellState.EMPTY]

        if whose_turn == human:
            # логика для человека:
            cell_number = common.get_user_input_int(
                'Ваш ход: ',
                GameDesk.__WANR_INCORRECT_CELL_NUM,
                lambda n: (n-1) in empty_cell_indexes,
                center=True)

            self.__desk[cell_number-1] = gamer_mark

        else:
            # логика ии-игрока:
            rnd_idx = random.choice(empty_cell_indexes)
            if self.difficulty_level == DifficultyLevel.HARD:
                idx_optimum = self.__find_optimum_cell_index(
                    CellState(opponent))
                if idx_optimum is not None:
                    rnd_idx = idx_optimum

            self.__desk[rnd_idx] = gamer_mark

            self.__clear_game_screen()
            self.__render(center=True)
            common.print_centered(
                f'Ход ИИ: {GameDesk.__cell_name_by_index(rnd_idx)}.')
            time.sleep(0.5)
            if len(empty_cell_indexes) > 1:  # делаем паузу-ввод только если ячейки ещё не кончились
                common.print_centered(
                    'Нажмите Enter чтобы продолжить...', end='')
                input()

        self.whose_turn = opponent

    def __clear_game_screen(self):
        if self.__con_pos_stored:
            Con.restore_cursor_pos()
            Con.clear_below_cursor()
        else:
            Con.store_cursor_pos()
            self.__con_pos_stored = True

    def __congratulations(self):
        if self.winner == CellState.EMPTY.value:
            print()
            print(Con.format('Ура! Победила ничья! \U0001F46F', center=True,
                  bold=True, italic=True, fore_color=ForeColor.BRIGHT_WHITE))
        elif self.winner == self.human:
            print()
            print(Con.format('Поздравляю, вы победитель! \U0001F37E', center=True,
                  bold=True, italic=True, fore_color=ForeColor.BRIGHT_GREEN))
        else:
            print()
            print(Con.format('Игра окончена. Вы проиграли \U0001F479', center=True,
                  bold=True, italic=True, fore_color=ForeColor.BRIGHT_RED))

        print()

    def run(self):
        while not self.gameover:
            self.__clear_game_screen()
            self.__render(center=True)
            self.__go_turn()
            self.__check_for_winner()
            self.__clear_game_screen()
            self.__render(center=True)

        self.__congratulations()

    def _debug_make_x_winner_on_mid_horizontal(self):
        dim = self._dim
        for i in range(dim//2*dim, dim//2*dim + dim):
            self.__desk[i] = CellState.X

    def _debug_make_o_winner_on_main_diag(self):
        dim = self._dim
        for i in range(dim):
            self.__desk[i * dim+i] = CellState.O

    def _debug_print_diagnostics(self):
        print(self.__scanlines)
        print(self.__desk)


# main flow:

user_answer = True

while(user_answer):
    # Con.clear()
    Con.clear_screen()
    Con.set_cursor_pos()

    common.print_title("Игра Крестики-нолики\nверсия 1.0",
                       fore_color=ForeColor.BRIGHT_WHITE, center=True)

    Con.store_cursor_pos()

    cust_dim = common.get_user_input_int('Задайте размер квадратного поля: ',
                                         WARN_OUT_OF_RANGE,
                                         lambda a: a > 1,
                                         center=True)

    dif_lvl = common.get_user_input_int_range('Задайте уровень сложности: '
                                              '\n\t0 \u2014 лёгкий,\n\t1 \u2014 сложный\n?: ',
                                              0, 1, center=True)
    Con.restore_cursor_pos()
    Con.clear_below_cursor()

    game = GameDesk(cust_dim, DifficultyLevel(dif_lvl))
    game.toss_who_human(20)
    game.run()

    # gd._debug_print_diagnostics()
    # game._debug_make_x_winner_on_mid_horizontal()
    # game._debug_make_o_winner_on_main_diag()
    # winner_info = game.__check_for_winner()
    # if winner_info is not None:
    #     print(winner_info[0])
    #     print(winner_info[1])

    # game.__render(center=True)

    user_answer = common.ask_for_repeat(center=True)
