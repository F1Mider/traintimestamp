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
                    all_time.append(time)
                continue
            # if len(ln2) == 0:
            #     continue
            ln = ln2[0].split('/')
            station = []

            if to_int(ln[0]):
                time, hour = to_time(ln[0], hour)
                station.append(time)
            elif ln[0] == '--' or ln[0] == '—':
                station.append('--')
            else:
                station.append(None)

            if len(ln) > 1:
                if to_int(ln[1]):
                    time, hour = to_time(ln[1], hour)
                    station.append(time)
                elif ln[1] == '—\n' or ln[1] == '--\n':
                    station.append('--')
                else:
                    station.append(None)
            else:
                station.append(None)
            all_time.append(station)
        elif line == '？\n' or line == '?\n':
            all_time.append('?')
        else:
            ln = re.findall('\d+', line)
            if len(ln) > 0:
                time, hour = to_time(ln[0], hour)
                all_time.append(time)
    return all_time


def combine_file(actual_time: list, scheduled_time: pd.DataFrame) -> list:
    """
    Takes the scheduled time DataFrame read from the csv file and combine with actual time list

    :param actual_time: The list of actual times processed from process_file() method
    :param scheduled_time: The pandas.DataFrame read from the csv file for station names and scheduled times
    :return: A combined list with scheduled time and actual time for each station
    """
    master_time = []
    row_iterator = scheduled_time.iterrows()
    i = 0
    sta = False
    pass_sta = False
    current = []
    for index, row in row_iterator:
        arr_time = None
        if i < len(actual_time) and not actual_time[i]:
            master_time.append([])
            i += 1
        if pd.notna(row[0]):
            station = re.split('\?|\xa0',row[0])[0]
            sta = True
            if row[1] == 'レ':
                pass_sta = True
            elif pd.isna(row[1]):
                arr_time = '--'
            else:
                arr_time = row[1][:5]
            current.append(station)
            current.append(arr_time)

        elif sta:
            if pd.isna(row[1]):
                dep_time = '--'
            else:
                dep_time = row[1][:5]
            if pass_sta:
                current.append('レ')
                if len(actual_time[i]) == 2:
                    current.append(actual_time[i][0])
                    current.append(actual_time[i][1])
                else:
                    current.append(None)
                    current.append(actual_time[i])
            else:
                current.append(dep_time)
                if arr_time == '--':
                    current.append(arr_time)
                else:
                    current.append(actual_time[i][0])
                if dep_time == '--':
                    current.append(dep_time)
                else:
                    current.append(actual_time[i][1])
            print(current)
            master_time.append(current)
            sta = False
            pass_sta = False
            i += 1
            current = []
    print(master_time)

    return master_time


def combine_file_new(actual_time: list, scheduled_time: pd.DataFrame) -> list:
    """
    Takes the scheduled time DataFrame read from the csv file and combine with actual time list
    Using the new format of scheduled time

    :param actual_time: The list of actual times processed from process_file() method
    :param scheduled_time: The pandas.DataFrame read from the csv file for station names and scheduled times
    :return: A combined list with scheduled time and actual time for each station
    """
    master_time = []
    row_iterator = scheduled_time.iterrows()
    i = 0
    pass_sta = False
    current = []
    for index, row in row_iterator:
        arr_time = None
        if i < len(actual_time) and not actual_time[i]:
            master_time.append([])
            i += 1
        if pd.notna(row[0]):
            station = row[0]
            current.append(station)
            if pd.isna(row[1]) and pd.isna(row[2]):
                current.append('')
                current.append('レ')
                if len(actual_time[i]) == 2:
                    current.append(actual_time[i][0])
                    current.append(actual_time[i][1])
                else:
                    current.append(None)
                    current.append(actual_time[i])
            else:
                if not pd.isna(row[1]):
                    arr_time = to_scheduled_time(row[1])
                else:
                    arr_time = '--'
                current.append(arr_time)
                if not pd.isna(row[2]):
                    dep_time = to_scheduled_time(row[2])
                else:
                    dep_time = '--'
                current.append(dep_time)
                if arr_time == '--':
                    current.append(arr_time)
                else:
                    current.append(actual_time[i][0])
                if dep_time == '--':
                    current.append(dep_time)
                else:
                    current.append(actual_time[i][1])
            print(current)
            master_time.append(current)
            i += 1
            current = []
    print(master_time)

    return master_time


def get_filename() -> tuple:
    """
    Choose from the preset year / month combinations as the file name to be processed

    :return: A tuple of three files that will be the input/output file names and a Boolean indicator for the format of
    scheduled time
    """
    # year = '2016'
    # year = '2017'
    # year = '2018'
    year = '2019'
    # month = '01'
    # month = '02'
    # month = '03'
    # month = '04'
    # month = '05'
    # month = '06'
    # month = '07'
    month = '08'
    # month = '09'
    # month = '10'
    # month = '11'
    # month = '12'
    new_type = True
    # new_type = False
    actual = 'data/' + year + month + '.txt'
    scheduled = 'data/' + year + month + '.csv'
    combined = 'output/' + year + '-' + month + '.csv'
    return actual, scheduled, combined, new_type


def main():
    """ The main function that will be executed first.

    :return:
    """

    a, s, c, n = get_filename()
    # Process file
    with open(a, 'r', encoding='utf-8') as fi:
        actual = process_file(fi)

    scheduled = pd.read_csv(s, header=None)
    print(scheduled)
    if n:
        master = combine_file_new(actual, scheduled)
    else:
        master = combine_file(actual, scheduled)

    with open(c, "w", encoding='utf-8') as output:
        writer = csv.writer(output, lineterminator='\n')
        writer.writerows(master)


if __name__ == '__main__':
    main()