import html
import os
import re
from enum import Enum

from bs4 import BeautifulSoup
from requests import get, HTTPError

CPE_DATA_URL = 'https://cpe.cse.nsysu.edu.tw/cpe/test_data/'


class FileType(Enum):
    code = 1
    testcase = 2


def get_soup(url: str, parser: str = 'html.parser'):
    return BeautifulSoup(get(url).text, parser)


def write_file(path: str, filename: str, extension: str, mode: str, contents: str):
    f = open(f'{path}\\{filename}.{extension}', mode, encoding='utf-8', newline='')
    f.write(contents)
    f.close()


def get_file(question_numbers: list, urls: list, path: str, file_type: FileType, filename: str = ''):
    if file_type == FileType.code:
        for url, number in zip(urls, question_numbers):
            soup = get_soup(url)
            code = html.unescape(str(soup.find(re.compile('pre'))))
            code = '\n'.join(code.split('\n')[1:-1])
            target_path = path + '\\' + number
            os.mkdir(target_path)
            write_file(target_path, number, 'cpp', 'w', code)
    elif file_type == FileType.testcase:
        for url, number in zip(urls, question_numbers):
            soup = get_soup(url)
            in_, out_ = ['\n'.join(str(x).replace('\r', '').split('\n')[1:-1]) for x in
                         soup.find_all(re.compile('pre'))]
            target_path = path + '\\' + number
            write_file(target_path, filename, 'in', 'w', in_)
            write_file(target_path, filename, 'out', 'w', out_)


def main():
    print('Input would be like:1990-01-01\nEnter 0 to exit.')
    while True:
        try:
            date = str(input('Enter the date of exam︰'))
            if date == '0':
                return
            if len(date) != 10 or date[4] != '-' or date[7] != '-':
                print('Wrong input format, please try again.')
                continue

            # get the main files.
            target_url = CPE_DATA_URL + date
            soup = get_soup(target_url)
            result_urls = [str(x.get('href')) for x in soup.find_all('a') if '.php' in str(x)]
            if not result_urls:
                raise HTTPError

            # get the URLs and numbers.
            code_urls = [x for x in result_urls if ('testData' not in x and '_' not in x)]
            testcase_urls = [x for x in result_urls if (x not in code_urls and '_' not in x)]
            question_numbers = list([x[59:-4] for x in code_urls])

            # set directory.
            path = '.\\CPE-' + date
            os.mkdir(path)

            # get the files.
            get_file(question_numbers, code_urls, path, FileType.code)
            get_file(question_numbers, testcase_urls[::2], path, FileType.testcase, '0')
            get_file(question_numbers, testcase_urls[1::2], path, FileType.testcase, '1')
            print('Successfully download.')

        except FileExistsError:
            print(f'Please delete CPE-{date} directory and try again.')
        except HTTPError:
            print('The website might be offline or the date isn\'t correct, maybe try again later.')
        except EOFError:
            break


if __name__ == '__main__':
    main()
