# Project name: PassportParser / ver: R0.1.0
# Author: Zakharov Bogdan Sergeevich [https://github.com/bogdanchik-s]
# Python version: 3.10.9

import re
from io import TextIOWrapper


MONTH_NUMBERS = {
    'января': '01',
    'февраля': '02',
    'марта': '03',
    'апреля': '04',
    'мая': '05',
    'июня': '06',
    'июля': '07',
    'августа': '08',
    'сентября': '09',
    'октября': '10',
    'ноября': '11',
    'декабря': '12'
}


def parse_passport_data(passport_data: str, debug: bool = False) -> str:
    # Убираем лишние слова и символы
    passport_data = re.sub(
        r'\bПаспорт\b|\bвыдан\b|\bот\b|\bСерия\b|\bНомер\b|\bДата выдачи\b|,', '',
        passport_data, flags=re.IGNORECASE
    )

    # Убираем лишние пробелы между словами и в начале и конце строки
    passport_data = re.sub(r'\s+', ' ', passport_data).strip()

    def remove_matched_substring(match_obj: re.Match) -> str:
        return str.strip(match_obj.string[:match_obj.start()] + match_obj.string[match_obj.end():])

    series_match_obj = re.search(r'№?(\d{4})', passport_data)

    # Если серия присутствует в passport_str
    if series_match_obj is not None:
        series = series_match_obj.group().replace('№', '')
        passport_data = remove_matched_substring(match_obj=series_match_obj)
    else:
        series = ''
    
    number_match_obj = re.search(r'№?(\d{6})', passport_data)

    # Если номер присутствует в passport_str
    if number_match_obj is not None:
        number = number_match_obj.group().replace('№', '')
        passport_data = remove_matched_substring(match_obj=number_match_obj)
    else:
        number = ''

    date_issue_match_obj = re.search(r'(\d{2})(\.|\s)((\d{2})|(\D+))(\.|\s)(\d{4})(\s?г?\.?)', passport_data)

    # Если дата выдачи присутствует в passport_str
    if date_issue_match_obj is not None:
        date_issue = re.sub(r'\s?г?\.?$', '', date_issue_match_obj.group()).strip()
        
        # Если месяц в буквенном формате, то делаем замену на цифры
        date_issue_month_literal_match_obj = re.search(r'\s(\D+)\s', date_issue)

        if date_issue_month_literal_match_obj is not None:
            date_issue_month_literal = date_issue_month_literal_match_obj.group().strip().lower()
            date_issue = re.sub(
                date_issue_month_literal_match_obj.re,
                f'.{MONTH_NUMBERS.get(date_issue_month_literal, date_issue_month_literal)}.',
                date_issue
            )
        
        passport_data = remove_matched_substring(match_obj=date_issue_match_obj)
    else:
        date_issue = ''

    code_department_match_obj = re.search(r'((\d{3})|(\s{3}))-((\d{3})|(\s{3}))', passport_data)

    # Если код подразделения присутствует в passport_str
    if code_department_match_obj is not None:
        code_department = code_department_match_obj.group()
        passport_data = remove_matched_substring(match_obj=code_department_match_obj)
    else:
        code_department = ''

    department = passport_data

    del passport_data

    if debug:
        print(f'Серия: {series}')
        print(f'Номер: {number}')
        print(f'Место выдачи: {department}')
        print(f'Код подразделения: {code_department}')
        print(f'Дата выдачи: {date_issue}')

    return series, number, department, code_department, date_issue


def write_passport_to_file(
    *passport_data, separator: str = '|',
    file: TextIOWrapper | str, file_close_needed: bool = True
) -> None:
    if isinstance(file, str):
        file = open(file=file, mode='w', encoding='utf-8')
    
    file.write(separator.join(pd if len(pd) > 0 else '[Пусто]' for pd in passport_data) + '\n')

    if file_close_needed:
        file.close()


def main(
    input_passport_file: TextIOWrapper | str,
    output_passport_file: TextIOWrapper | str,
    separator: str = '|', 
    debug: bool = False
) -> None:
    if isinstance(input_passport_file, str):
        input_passport_file = open(file=input_passport_file, mode='r', encoding='utf-8')

    with input_passport_file:
        passports_lines = input_passport_file.readlines()
        passports_count = len(passports_lines)

        for p_idx, passport_line in enumerate(passports_lines):
            if debug:
                print(f'Паспорт [{p_idx} строка]:')

            passport_data = parse_passport_data(passport_data=passport_line, debug=debug)
            write_passport_to_file(
                *passport_data, separator=separator,
                file=output_passport_file, file_close_needed=False
            )

            if debug:
                print('-' * 25)
            else:
                print(f'\rПроцесс: {p_idx+1} / {passports_count}', end='')

                if p_idx == passports_count - 1:
                    print('\rПроцесс завершен. Обработанные данные успешно сохранены.')

        output_passport_file.close()


if __name__ == '__main__':
    from argparse import ArgumentParser, FileType

    arg_parser = ArgumentParser(
        prog='PassportParser',
        description='Программа для разбора паспортных данных в одной строке на подстроки',
        epilog=(
            '© Захаров Богдан Сергеевич (ZBS) / 2024. '
            'Автор программы не несет ответственности за используемые при работе конфиденциальные данные людей'
        ),
        add_help=False
    )

    # Общие параметры
    arg_main_group = arg_parser.add_argument_group(title='Общие параметры')
    arg_main_group.add_argument('-c', '--country', default='ru', help='Страна выдачи паспорта')
    arg_main_group.add_argument(
        '-d', '--debug', action='store_true', default=False,
        help='Вывод отладочной информации в терминал'
    )
    arg_main_group.add_argument('-h', '--help', action='help', help='Справка')

    # Параметры для входных данных
    arg_input_data_group = arg_parser.add_argument_group(title='Параметры для входных данных')
    arg_input_data_group.add_argument(
        '-i', '--input-file', type=FileType(mode='r', encoding='utf-8'), default='./passports.txt',
        help='Путь к входному файлу с паспортными данными'
    )

    # Параметры для выходных данных
    arg_output_data_group = arg_parser.add_argument_group(title='Параметры для выходных данных')
    arg_output_data_group.add_argument(
        '-o', '--output-file', type=FileType(mode='w', encoding='utf-8'), default='./passports_done.txt',
        help='Путь к выходному файлу с паспортными данными'
    )
    arg_output_data_group.add_argument(
        '-s', '--separator', default='|',
        help='Разделитель между значениями паспортных данных в выходном файле'
    )

    options = arg_parser.parse_args()

    main(
        input_passport_file=options.input_file,
        output_passport_file=options.output_file,
        separator=options.separator,
        debug=options.debug
    )
