import codecs
import re
from more_itertools import unique_everseen

def read_list(filepath, codec):
    with codecs.open(filepath, 'r', codec) as file:
        data = file.readlines()
        data = [line.rstrip() for line in data]
    return data

def list_to_file(filepath, list_, codec):
    with codecs.open(filepath, 'w', codec) as file:
        for line in list_:
            line = line + '\n'
            file.write(line)

def delete_symb(string, regex):
    symb = re.findall(regex, string)
    symb = list(unique_everseen(symb))
    for item in symb:
        string = string.replace(item, ' ')
    string = re.sub(r'\s+', ' ', string)
    return string.lower()

def put_spaces(regex, string):
    k = re.findall(regex, string)
    aim = [i[0] + ' ' + i[1:] for i in k]
    for i, w in enumerate(k):
        string = string.replace(w, aim[i])
    return string

def put_spaces_abb(regex, string):
    l = re.findall(regex, string)
    aim =[]
    for i, w in enumerate(l):
        n = len(w)
        aim += [l[i][0]+' '+l[i][1:n-1]+' '+l[i][n-1]]
        string = string.replace(l[i], aim[i])
    return string


def recursive_flatten_generator(array):
    lst = []
    for i in array:
        if isinstance(i, list):
            lst.extend(recursive_flatten_generator(i))
        else:
            lst.append(i)
    return lst

def hascyr(s):
    lower = set('абвгдеёжзийклмнопрстуфхцчшщъыьэюя')
    return lower.intersection(s.lower()) != set()