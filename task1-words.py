# Напишите программу, удаляющую из текста все слова, содержащие "абв"

from enum import Enum
import os
import common
from common import ForeColor, BackColor, Console as Con

# turn on ansi escape sequences in win cmd :

Con.activate_ansi_esc_seq_in_win_cmd()

# consts:

FILES_DIR = 'task1_files'
SRC_FILENAME = 'source_text.txt'
OUT_FILENAME = 'result_text.txt'

WHITESPACES = ' \t\n\r\v\f'
PUNCTUATIONS = r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""


# types:

class TextEntityType(Enum):
    WHITESPACE = 0
    PUNCTUATION = 1
    WORD = 2

    @staticmethod
    def get_type(text_entity):
        if text_entity in WHITESPACES:
            return TextEntityType.WHITESPACE
        elif text_entity in PUNCTUATIONS:
            return TextEntityType.PUNCTUATION
        else:
            return TextEntityType.WORD


# methods:

def next_text_entity(source_str: str):
    if source_str is None or source_str == '':
        return
    source_len = len(source_str)
    current_entity = source_str[0]
    current_type = TextEntityType.get_type(current_entity)
    i = 1
    while i < source_len:
        test_char = source_str[i]
        test_char_type = TextEntityType.get_type(test_char)
        if test_char_type == current_type:
            current_entity += test_char
        else:
            yield (current_entity, current_type)
            current_entity = test_char
            current_type = test_char_type
        i += 1

    if current_entity != '':
        yield (current_entity, current_type)


def remove_words(source_text: str, word_contains: str):
    """ Удаление слов, содержащих последовательность букв,
    используя методы filter() и map(), и с сохранением
    пунктуации и конфигурации пробельных символов.
    """
    text_entities_gen = next_text_entity(source_text)
    filtered_entities = filter(
        lambda e: not (e[1] == TextEntityType.WORD and word_contains in e[0]),
        text_entities_gen)
    only_text_items = map(lambda e: e[0], filtered_entities)
    return ''.join(list(only_text_items))


def test_highlight_words(source_text: str, word_contains: str):
    """ Тестовый метод для подсветки слов на уделение.
    """
    def get_str_and_highlight_if_necessary(txt_ent: tuple[str, TextEntityType]):
        if txt_ent[1] == TextEntityType.WORD and word_contains in txt_ent[0]:
            return Con.format(txt_ent[0], italic=True, fore_color=ForeColor.BLACK, back_color=BackColor.BRIGHT_BLUE)
        return txt_ent[0]

    text_entities_gen = next_text_entity(source_text)
    only_text_items = map(
        get_str_and_highlight_if_necessary, text_entities_gen)
    return ''.join(list(only_text_items))


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


def get_letters_from_user():
    unallowed_set = set(WHITESPACES + PUNCTUATIONS)
    error_wrong_input = False
    while True:
        if error_wrong_input:
            common.print_error(
                'Некорректный ввод: Допустимы только буквенные символы! '+common.PLEASE_REPEAT)
        inp_str = input(Con.format('Введите последовательность букв: ',
                        bold=True, fore_color=ForeColor.BRIGHT_WHITE))
        error_wrong_input = len(set(inp_str) & unallowed_set) != 0
        if not error_wrong_input:
            return inp_str


# main flow:

user_answer = True

while(user_answer):
    Con.clear()
    common.print_title(
        'Удаление из текста всех слов, содержащих заданную последовательность букв'
        '\n(с сохранением пунктуации и конфигурации пробелов)')

    path_to_source = os.path.join(FILES_DIR, SRC_FILENAME)
    source_text = read_textfile_entirely(path_to_source)
    if source_text is None:
        exit()

    print(Con.format(f'Файл {path_to_source}, содержащий исходный текст успешно прочитан.',
                     fore_color=ForeColor.GREEN))
    print(Con.format('\nСодержимое файла:\n',
                     italic=True, underline=True, fore_color=ForeColor.BRIGHT_WHITE))

    print(source_text)

    print()
    pattern_str = get_letters_from_user()
    print()

    highlighted_text = test_highlight_words(source_text, pattern_str)
    print(highlighted_text)
    print()

    result_text = remove_words(source_text, pattern_str)
    print(Con.format(f'\nРезультат удаления слов, содержащих "{pattern_str}":\n',
                     italic=True, underline=True, fore_color=ForeColor.BRIGHT_WHITE))
    print(result_text)
    print()

    path_to_result = os.path.join(FILES_DIR, OUT_FILENAME)
    if write_textfile(path_to_result, result_text):
        print(Con.format(f'Результат успешно записан в файл {path_to_result}',
                         fore_color=ForeColor.GREEN))
        print()

    user_answer = common.ask_for_repeat()
