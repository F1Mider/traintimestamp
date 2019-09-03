import pandas as pd
import csv
import datetime
import re


def to_time(timestamp: int, hour: int) -> (str, int):
    """
    Transforms timestamps into datetime.time

    :param timestamp: the timestamp that went through try_to_time
    :param hour: the hour passed from the previous line
    :return: A string that converts from datetime.time and the hour for this timestamp
    """
    timestamp = int(timestamp)
    if timestamp // 10000 > 0 or hour is None:
        hour = timestamp // 10000
    if timestamp // 10000 == 24:
        hour = 0
    minute = timestamp % 10000 // 100
    sec = timestamp % 100

    return datetime.time(hour, minute, sec).strftime('%H:%M:%S'), hour


def to_scheduled_time(timestamp: int) -> (str):
    """
    Transforms timestamps into datetime.time

    :param timestamp: the timestamp that went through try_to_time
    :return: A string that converts from datetime.time and the hour for this timestamp
    """
    timestamp = int(timestamp)

    hour = timestamp // 100
    minute = timestamp % 100

    return datetime.time(hour, minute).strftime('%H:%M')


def try_to_time(timestamp: int) -> bool:
    """
    Determine whether the integer passed in can be transformed into datetime.time

    :param timestamp: A string extracted from the acutal time file
    :return: Boolean: whether this string can be transformed into datetime.time
    """
    try:
        hour = None
        if timestamp / 10000 > 0:
            hour = timestamp // 10000
            if timestamp // 10000 == 24:
                hour = 0
        minute = timestamp % 10000 // 100
        sec = timestamp % 100
        datetime.time(hour, minute, sec)
    except ValueError:
        return False
    except TypeError:
        return False

    return True


def to_int(timestamp: str) -> bool:
    """
    Transforms the timestamp into integer and check if it can be transformed into datetime.time. If so, return True.
    If the string cannot be transformed into integer and then datetime.time, return False

    :param timestamp: the string to be transformed
    :return: A boolean whether the string can be transformed into datetime.time
    """
    try:
        timestamp = int(timestamp)
    except ValueError:
        return False
    except TypeError:
        return False
    return try_to_time(timestamp)


def process_file(fi: list) -> list:
    """
    Takes in the actual timesheet and process line by line to extract the actual time for each station

    :param fi: The list read from the txt file
    :return: The time for all stations read from the file
    """
    all_time = []
    hour = None
    fii = iter(fi)
    for line in fii:
        if line == '\n':
            all_time.append([])
            while '/' not in line:
                line = next(fii)
        if '/' in line:
            ln1 = line.split(' ')
            ln2 = re.findall('\d+/\d+|\d+/--|--/\d+|\d+/—|—/\d+|\d+/|/\d+\n|/\d+', ln1[0])
            if '/' not in ln1[0]:
                ln = re.findall('\d+', ln1[0])
                if len(ln) > 0:
                    time, hour = to_time(ln[0], hour)
                    all_time.append([time,''])
                    all_time.append((['','']))
                continue
            # if len(ln2) == 0:
            #     continue
            ln = ln2[0].split('/')

            if to_int(ln[0]):
                time, hour = to_time(ln[0], hour)
                all_time.append([time,''])
            elif ln[0] == '--' or ln[0] == '—':
                all_time.append(['ˇ',''])
            else:
                all_time.append(['ˇ',''])

            if len(ln) > 1:
                if to_int(ln[1]):
                    time, hour = to_time(ln[1], hour)
                    all_time.append([time,''])
                elif ln[1] == '—\n' or ln[1] == '--\n':
                    all_time.append(['——',''])
                else:
                    all_time.append(['——', ''])
            else:
                all_time.append(['',''])
        elif line == '？\n' or line == '?\n':
            all_time.append('?')
            all_time.append((['', '']))
        else:
            ln = re.findall('\d+', line)
            if len(ln) > 0:
                time, hour = to_time(ln[0], hour)
                all_time.append([time,''])
                all_time.append((['','']))
    return all_time


def main():
    """ The main function that will be executed first.

    :return:
    """

    a = '20190819.txt'
    c = '20190819.csv'
    # Process file
    with open(a, 'r', encoding='utf-8') as fi:
        actual = process_file(fi)

    print(actual)

    with open(c, "w", encoding='utf-8') as output:
        writer = csv.writer(output, lineterminator='\n')
        writer.writerows(actual)


if __name__ == '__main__':
    main()