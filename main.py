import pandas as pd
import csv
import datetime
import re


def to_time(timestamp, hour):

    timestamp = int(timestamp)
    if timestamp // 10000 > 0 or hour is None:
        hour = timestamp // 10000
    min = timestamp % 10000 // 100
    sec = timestamp % 100

    return datetime.time(hour, min, sec).strftime('%H:%M:%S'), hour


def try_to_time(timestamp):
    try:
        if timestamp / 10000 > 0:
            hour = timestamp // 10000
        min = timestamp % 10000 // 100
        sec = timestamp % 100
        datetime.time(hour, min, sec)
    except ValueError:
        return False
    except TypeError:
        return False

    return True


def to_int(timestamp):
    try:
        timestamp = int(timestamp)
    except ValueError:
        return False
    except TypeError:
        return False
    return try_to_time(timestamp)


def process_file(fi):
    alltime = []
    hour = None
    fii = iter(fi)
    for line in fii:
        if line == '\n':
            while '/' not in line:
                line = next(fii)
        if '/' in line:
            ln1 = line.split(' ')
            ln2 = re.findall('\d+/\d+|\d+/--|--/\d+|\d+/—|—/\d+|\d+/|/\d+\n', ln1[0])
            print(ln2)
            if len(ln2) == 0:
                continue
            ln = ln2[0].split('/')
            station = []
            print(ln)

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
            alltime.append(station)
        elif line == '？\n' or line == '?\n':
            alltime.append('?')
        else:
            ln = re.findall('\d+', line)
            if len(ln)>0:
                time, hour = to_time(ln[0], hour)
                alltime.append(time)

    return alltime


def combine_file(actual_time, scheduled_time):
    master_time = []
    row_iterator = scheduled_time.iterrows()
    i = 0
    sta = False
    pass_sta = False
    current = []
    for index, row in row_iterator:
        if pd.notna(row[0]):
            station = row[0].split('?')[0]
            sta = True
            arrtime = None
            if row[1] == 'レ':
                pass_sta = True
            elif pd.isna(row[1]):
                arrtime = '--'
            else:
                arrtime = row[1][:5]
            current.append(station)
            current.append(arrtime)

        elif sta:
            if pd.isna(row[1]):
                deptime = '--'
            else:
                deptime = row[1][:5]
            if pass_sta:
                current.append('レ')
                if len(actual_time[i]) == 2:
                    current.append(actual_time[i][0])
                    current.append(actual_time[i][1])
                else:
                    current.append(None)
                    current.append(actual_time[i])
            else:
                current.append(deptime)
                current.append(actual_time[i][0])
                current.append(actual_time[i][1])
            # master_time.append(current)
            print(current)
            master_time.append(current)
            sta = False
            pass_sta = False
            i += 1
            current = []
    print(master_time)

    return(master_time)


def main():
    """ The main function that will be executed first.

    :return:
    """

    actual = []
    # Process file
    with open('201805.txt', 'r', encoding='utf-8') as fi:
        actual = process_file(fi)

    scheduled = pd.read_csv('201805.csv', header=None)
    master = combine_file(actual, scheduled)

    with open('2018-05.csv', "w") as output:
        writer = csv.writer(output, lineterminator='\n')
        writer.writerows(master)



if __name__ == '__main__':
    main()