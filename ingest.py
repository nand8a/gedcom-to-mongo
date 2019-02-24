from enum import Enum
import sys
import logging
log = logging.getLogger(__name__)
# INT_IDX = Enum('START')


filename='/home/jacques/industria/nand/gedcom/ged/duplessis_utf8.ged'


def file_parser(fqfn):
    count = 0
    reading = True
    with open(fqfn, 'r',  encoding='utf-8-sig') as f:
        while reading:
            line = f.readline()
            # strip away leading whitespace
            line = line.lstrip(' ')
            line_split = line.split(' ')
            print(line_split[0:2])
            count += 1
            if count > 50:
                sys.exit()
            if line[0] == '0':
                f = _person_reader(f, line)


def _person_reader(file_handler, line):
    reading = True
    print('person_reader {}'.format(line))
    lines = []
    if 'INDI' not in line:
        return file_handler
    else:
        # add the first line of person record
        lines.append(line)
    while True:
        last_pos = file_handler.tell()
        line = file_handler.readline()
        line = line.lstrip(' ')
        if 'INDI' in line:
            # must deal sequentially due to max recursion depth
            file_handler.seek(last_pos)
            print('person_parser')
            _person_parser(lines)
            return file_handler
        else:
            print('appending...')
            lines.append(line)


def _person_sub(lines, current_i, current_level):
    """
    :param lines: list of lines
    :param current_i: the current index into the list
    :param current_level: the current 'level' (where level in [2,3,4,...]
    :return: a dictionary where all level elements are nested at the same depth
    """
    i = current_i
    level_dict = {}
    # we increment only after the first run of the loop
    print('_person_sub: params: current_i: {}, current_level: {}'.format(current_i, current_level))
    print('called with line: {}'.format(lines[i]))
    while i < len(lines):
        split_lines = lines[i].rstrip('\n').split(' ')
        level, key = split_lines[0], split_lines[1].lower()
        if current_level == '1':
            # special case, return either root {key: None} or {key: value}
            value = None
            try:
                value = split_lines[2]
            except Exception as e:
                pass
            i += 1
            return {key: value}, i
        if level != current_level:
            break
        level_dict[key] = ' '.join(split_lines[2:])
        print('person_sub: level: {}, i: {}, line: {}'.format(level, i, lines[i]))
        i += 1
    return level_dict, i


def _person_parser(lines):
    person_dict = {}
    i = 0
    line = lines[i]
    print(lines)
    while i < len(lines):
        if 'INDI' in line:
            identifier = line.split(' ')[1]
            log.debug('INDI: {}'.format(identifier))
            person_dict['_id'] = identifier
            i += 1
            line = lines[i]
        if '1 NAME' in line:
            name = line.split(' ')[2:]
            log.debug('NAME: {}'.format(name))
            person_dict['name'] = {'name': name}
            i += 1
            while i < len(lines) and lines[i].split(' ')[0] != '1':
                level = line.split(' ')[0]
                local_dict, i = _person_sub(lines, i, level)
                person_dict['name'].update(local_dict)
                line = lines[i]
        if lines[i].startswith('1'):
            local_dict, i = _person_sub(lines, i, lines[i].split(' ')[0])
            print(local_dict)
            person_dict.update(local_dict)
            key = list(local_dict.keys())[0]
            print(key)
            print('----')
            print(person_dict)
            print(person_dict[key])
            while lines[i].split(' ')[0] != '1':
                local_dict, i = _person_sub(lines, i, lines[i].split(' ')[0])
                print(local_dict)
                person_dict[key] = local_dict
    print(person_dict)
    exit(1)

file_parser(filename)