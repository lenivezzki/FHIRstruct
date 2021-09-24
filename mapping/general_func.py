

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


def recursive_flatten_generator(array):
    lst = []
    for i in array:
        if isinstance(i, list):
            lst.extend(recursive_flatten_generator(i))
        else:
            lst.append(i)
    return lst