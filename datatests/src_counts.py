
import argparse
import re


# move to unittest like setup
def get_birth_date(filename):  # pragma: no cover
    """
    get a birth and date for each individual
    :param filename:
    :return:
    """
    indi_list = []
    with open(filename, 'r', encoding='utf-8-sig') as f:
        for line in f:
            if bool(re.search('0 @[A-Z0-9]*@ INDI', line)):
                indi = line
            if bool(re.search('^1 BIRT$', line)):
                line = f.readline()
                if bool(re.search('^2 DATE', line)):
                    indi_list.append(indi.replace('\n', ''))
    return indi_list


def _count(obj, item):
    """
    Count in either a list or add on to an integer
    :param obj: either an integer or a list of individuals
    :param item: an string containing the indi code
    :return: inc(obj), or append(item)
    """
    if isinstance(obj, list):
        obj.append(item)
    else:
        obj += 1
    return obj


def _get_file_handler(filename, encoding='utf-8-sig'):
    f = open(filename, 'r', encoding=encoding)
    return f


def get_death(fh, sub_key=None, counting_obj=0):
    """
    get a death and date for each individual, there could be a 'PLAC' interspersed
    :param fh: a file handler to the source file that we want to check
    :return: a single integer count, or a list of individuals for debugging purposes
    """
    line = fh.readline()
    indi = None

    while not (line is None or line == ""):
        if bool(re.search('0 @[A-Z0-9]*@ INDI', line)):
            indi = line.replace('\n', '')
        line = fh.readline()
        if bool(re.search('^1 DEAT$', line)):  # explicit match on death
            if sub_key is None:
                counting_obj = _count(counting_obj, indi)
            else:
                while not (line.startswith('0') or line == ""):
                    if bool(re.search('^[0-9] {}'.format(sub_key), line)):
                        counting_obj = _count(counting_obj, indi)
                        break
                    line = fh.readline()
                    print(line)
    return counting_obj


if __name__ == '__main__':  # pragma: no cover
    parser = argparse.ArgumentParser(description='this function prints a list to stdout where ' 
                                                 'members of the list are such that they adhere '
                                                 'to some constraint')
    parser.add_argument('-f', '--file', required=True, help="gedcom file")
    parser.add_argument('-b', '--birth', action='store_true', help='a toggle to print a list of people with birth dates')
    parser.add_argument('-d', '--death', default="", help='provide a subkey (e.g. DEAT, PLAC)of the death event that you '
                                                          'want to count,, or use "" to count deaths only')
    parser.add_argument('-l', '--list', action='store_true', help='list the individual keys (useful for debugging)')

    args = parser.parse_args()

    if args.list:
        counting_obj = []
    else:
        counting_obj = 0

    if args.birth and args.death:
        raise ValueError('this helper/printer function can only return one query response at a time')

    if args.birth:
        print('{}'.format('\n'.join(get_birth_date(args.file))))

    fh = _get_file_handler(args.file)
    if args.death:
        print('{}'.format('\n'.join(get_death(fh, sub_key=args.death, counting_obj=counting_obj))))
        print('{}'.format('\n'.join(get_death(fh, sub_key=args.death, counting_obj=counting_obj))))
    fh.close()

