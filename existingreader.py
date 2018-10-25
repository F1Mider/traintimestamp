import pandas as pd
import csv
import re


# def process_file(df):
#     # print(df[0])
#     row_iterator = df.iterrows()
#     new = pd.DataFrame(columns = ['A', 'B', 'C'])
#     for index, row in row_iterator:
#         print(row[0])
#         if not pd.isna(row[0]) and len(re.findall('\d+:\d+:\d+', row[0])) > 0:
#             new.loc[-1] = row
#         # print(row[2])
#     for row in new:
#         print(row)
#     return []

def cleanup(f):
    for station in f:
        if ":" in station[1] or "レ" in station[1] or '〃' in station[1] or station[1] == ' ':
            print(station[1])
            station[1] = ""
    return f


def println(li):
    for line in li:
        print(line)


def process_file(fi):
    medium = []
    for line in fi:
        ln = line.split(',')

        c0 = re.findall('\d+:\d+:\d+', ln[0])
        c2 = re.findall('\d+:\d+:\d+', ln[2])
        if ln[0] == 'ˇ' or ln[2] == 'ˇ':
            c0 = '--'
            c2 = '--'
            ln[0] = '--'
            ln[2] = '--'
        elif ln[0] == '——' or ln[2] == '——':
            c0 = '--'
            c2 = '--'
            ln[0] = '--'
            ln[2] = '--'
        if ln[0] == '圖定時刻':
            c0 = '--'
            c2 = '--'
        print(c0)
        if c0 or c2:
            medium.append(ln)
    medium = cleanup(medium)
    println(medium)
    final = []
    current = []
    for line in medium:
        if line[1] is "":
            current.append(line[0])
            current.append(line[2])
        elif line[0] == '圖定時刻':
            final.append(current)
            current = ['圖定時刻']
        else:
            if len(current) == 3:
                current.append("")
                current.append("")
                final.append(current)
            else:
                final.append(current)
            current = []
            current.append(line[1])
            current.append(line[0])
            current.append(line[2])
    current.append("")
    current.append("")
    final.append(current)
    print(final)
    ultimate = []
    for line in final:
        current = []
        print(line)
        if not line:
            print(line)
            continue
        elif line == ['圖定時刻']:

            ultimate.append(current)
            continue
        current.append(line[0])
        if line[1] == "" and line[3] == "":
            current.append("")
            current.append("レ")
        else:
            current.append(line[1])
            current.append(line[3])
        current.append(line[2])
        current.append(line[4])
        ultimate.append(current)
    return ultimate


def main():
    """ The main function that will be executed first.

    :return:
    """

    filename = 'data/180324.csv'
    file = 'output/18-03-24.csv'

    # test = pd.read_excel("2018tdbj.xlsx", '180321', header = None)
    # print(test[1])

    with open(filename, 'r', encoding='utf-8') as fi:
        actual = process_file(fi)

    with open(file, "w", encoding='utf-8') as output:
        writer = csv.writer(output, lineterminator='\n')
        writer.writerows(actual)


    # df = pd.read_csv(filename, header=None)
    # df = df.drop(columns=[3,4,5,6,7])
    # process_file(df)


if __name__ == '__main__':
    main()