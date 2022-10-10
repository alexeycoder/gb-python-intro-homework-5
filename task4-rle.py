# Реализуйте RLE алгоритм: реализуйте модуль сжатия и восстановления данных.
# Входные и выходные данные хранятся в отдельных текстовых файлах.

import os
import random
import common
from common import ForeColor, BackColor, Console as Con

# turn on ansi escape sequences in win cmd :

Con.activate_ansi_esc_seq_in_win_cmd()

# consts

FILES_DIR = 'task4_files'
SRC_FILENAME = 'some_text.txt'
OUT_ENC_FILENAME = 'rle_encoded.txt'
OUT_DEC_FILENAME = 'rle_decoded.txt'


# types:

class basic_rle:
    @staticmethod
    def encode(data_str: str):
        if data_str is None:
            return None
        if (data_len := len(data_str)) == 0:
            return ''
        encoded_str = ''
        series_char = data_str[0]
        count = 1
        i = 1
        while i < data_len:
            char = data_str[i]
            if char != series_char:
                encoded_str += str(count) + series_char
                series_char = char
                count = 1
            else:
                count += 1
            i += 1

        if count > 0:
            encoded_str += str(count) + series_char
        return encoded_str

    @staticmethod
    def decode(data_str: str) -> tuple[str, list]:
        errors_found = []
        if data_str is None:
            return (None, errors_found)
        if (data_len := len(data_str)) == 0:
            return ('', errors_found)
        decoded_str = ''
        i = 0
        qty_str = ''
        while i < data_len:
            item = data_str[i]
            if item.isdigit():
                qty_str += item
            else:
                if qty_str == '':
                    # сюда не должны попасть, если входящие данные корректные
                    errors_found.append(i)
                    # пропускаем индексы для которых следующий символ - буква,
                    # пока не встретим цифру - начало нового блока (кол-во:символ)
                    while i + 1 < data_len and not data_str[i+1].isdigit():
                        i += 1
                else:
                    # случай когда всё ОК:
                    decoded_str += item * int(qty_str)
                    qty_str = ''
            i += 1

        if qty_str != '':
            errors_found.append(data_len-1)

        return (decoded_str, errors_found)


# aux methods:

ALPHABET = ''.join(map(chr, range(ord('a'), ord('z')+1)))
ALPHABET += ALPHABET.upper()
PUNCTUATION = '.,-+_'


def generate_random_text(num_of_lines, max_words_per_line, max_leters_per_word, max_symbols_seq):
    max_punct_seq = max(5, max_symbols_seq//3)

    def generate_punctuation():
        mult = random.randint(1, max_punct_seq) \
            if random.choice([False, True, False]) \
            else 1
        return ' ' * random.randint(0, 2) \
            + random.choice(PUNCTUATION) * mult \
            + ' ' * random.randint(0, 2)

    def generate_word():
        letters_count = random.randint(2, max_leters_per_word)
        word = ''
        for _ in range(letters_count):
            mult = random.randint(1, max_symbols_seq) \
                if random.choice([False, True, False]) \
                else 1
            word += random.choice(ALPHABET) * mult

        return word

    def generate_line():
        line = ''
        for _ in range(2, max_words_per_line):
            line += generate_word() + generate_punctuation()
        return line + generate_word()

    random_text = ''
    for _ in range(num_of_lines-1):
        random_text += generate_line() + '\n'
    return random_text + generate_line()


def read_textfile_entirely(file_path):
    if not os.path.isfile(file_path):
        common.print_error(f'Файл {file_path} не найден.')
        return None
    try:
        if os.path.getsize(file_path) == 0:
            common.print_warning(f'Файл {file_path} пуст.')
            return None
    except OSError:
        common.print_error(f'Доступ к файлу {file_path} ограничен.')
        return None

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            file_content = file.read()
            return file_content
    except OSError:
        common.print_error(f'Не удалось прочитать файл {file_path}.')
        return None


def write_textfile(file_path, content) -> bool:
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
            return True
    except OSError:
        common.print_error(f'Ошибка: Не удалось записать в файл {file_path}!')
        return False


# main flow:

user_answer = True

while(user_answer):
    Con.clear()
    common.print_title(
        'Демонстрация базового алгоритма RLE кодирования и декодирования')

    path_to_source = os.path.join(FILES_DIR, SRC_FILENAME)
    path_to_encoded = os.path.join(FILES_DIR, OUT_ENC_FILENAME)
    path_to_decoded = os.path.join(FILES_DIR, OUT_DEC_FILENAME)

    print('Выбор источника данных:'
          f'\n\t0 \u2014 взять существующие данные из файла {path_to_source},'
          f'\n\t1 \u2014 сгенерировать новые данные случайным образом'
          f'\n\t\tи перезаписать файл источник {path_to_source}')

    select_way = common.get_user_input_int_range(
        Con.format('\nВаш выбор: ', bold=True,
                   fore_color=ForeColor.BRIGHT_WHITE), 0, 1)

    # горизонтальный разделитель
    console_width, _ = Con.get_size()
    print('\n', '\u2508'*console_width, '\n', sep='')

    # 0. ПОЛУЧАЕМ ИСХОДНЫЕ ДАННЫЕ

    source_text = None
    if select_way == 0:
        source_text = read_textfile_entirely(path_to_source)
        if source_text is None:
            user_answer = common.ask_for_repeat()
            continue

        print(Con.format(f'Файл {path_to_source}, содержащий исходный текст успешно прочитан.',
                         fore_color=ForeColor.GREEN))
    else:
        source_text = generate_random_text(num_of_lines=4, max_words_per_line=6,
                                           max_leters_per_word=7, max_symbols_seq=16)
        if write_textfile(path_to_source, source_text):
            print(Con.format(f'Исходный текст сгенерирован и успешно записан в файл {path_to_source}.',
                             fore_color=ForeColor.GREEN))
        else:
            exit()

    print(Con.format('\nСодержимое:\n',
                     italic=True, underline=True, fore_color=ForeColor.BRIGHT_WHITE))
    print(source_text)
    print()

    # 1. КОДИРУЕМ

    encoded_data = basic_rle.encode(source_text)
    print(Con.format(f'\nРезультат кодирования:\n',
                     italic=True, underline=True, fore_color=ForeColor.BRIGHT_WHITE))
    print(encoded_data)

    if write_textfile(path_to_encoded, encoded_data):
        print(Con.format(f'\nРезультат успешно записан в файл {path_to_encoded}',
                         fore_color=ForeColor.GREEN))

    print('\n', '\u2508'*console_width, '\n', sep='')

    # 2. ЧИТАЕМ ИЗ ФАЙЛА НАКОДИРОВАННОЕ

    source_encoded_text = read_textfile_entirely(path_to_encoded)
    if source_encoded_text is None:
        exit()

    print(Con.format(f'Файл {path_to_encoded}, содержащий RLE-сжатый текст успешно прочитан.',
                     fore_color=ForeColor.GREEN))

    print(Con.format(f'\nСодержимое:\n',
                     italic=True, underline=True, fore_color=ForeColor.BRIGHT_WHITE))
    print(source_encoded_text)
    print()

    # 3. ДЕКОДИРУЕМ ПРОЧИТАННОЕ

    decoded_data, errors = basic_rle.decode(source_encoded_text)
    print(Con.format(f'\nРезультат декодирования:\n',
                     italic=True, underline=True, fore_color=ForeColor.BRIGHT_WHITE))
    print(decoded_data)

    if len(errors) > 0:
        common.print_error(
            'При декодировании были выявлены ошибки в кодированных данных!')

    if write_textfile(path_to_decoded, decoded_data):
        print(Con.format(f'\nРезультат успешно записан в файл {path_to_decoded}',
                         fore_color=ForeColor.GREEN))

    print('\n', '\u2508'*console_width, '\n', sep='')

    # 4. СРАВНЕНИЕ

    print(Con.format(f'Сравнение данных:\n',
                     italic=True, underline=True, fore_color=ForeColor.BRIGHT_WHITE))

    if source_text == decoded_data:
        print(Con.format('Исходные данные и декодированные данные совпадают!',
              fore_color=ForeColor.YELLOW))
    else:
        print(Con.format(
            'Исходные данные и декодированные данные различаются!', fore_color=ForeColor.RED))

    src_len = len(source_text)
    enc_len = len(encoded_data)
    print(f'Размер исходных данных: {src_len} симв.')
    print(f'Размер кодированных данных: {enc_len} симв.')
    print(f'Степень сжатия: {src_len} / {enc_len} = {(src_len/enc_len):g}')
    print()

    user_answer = common.ask_for_repeat()
