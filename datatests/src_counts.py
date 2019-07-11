import argparse
import re


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


##
# this is a dumb reader that is inefficient in that it runs over the file for each subcount. The reason for this
# is to verify the source data as simply as possible without writing another explicit parser, and without leaking the
# implementation of the actual application over so as to ensure that we have parsed the data correctly between the two
# interpretations.
##
def count_subs(fh, key, sub_key=None, counting_obj=0):
    """
    count how many times a key occurs, or how many times a key.sub_key occurs (the purpose fo this method is
    primarily to count sub_keys).
    This is written to stream over the file under the assumption that the files are small.
    :param key: a key or top structure to count (e.g. 'INDI', 'DEAT', 'BIRT)
    :param sub_key: a sub_key to count within the larger substructure; the assumption here is that the sub_key is at level 1.
    :param fh: a file handler to the source file that we want to check
    :return: a single integer count, or a list of individuals for debugging purposes
    """
    line = fh.readline()
    indi = None

    while not (line is None or line == ""):
        if bool(re.search('0 @[A-Z0-9]*@ INDI', line)):
            indi = line.replace('\n', '')
        line = fh.readline()
        if bool(re.search('^1 {}$'.format(key), line)):  # explicit match on super key
            if sub_key is None:
                counting_obj = _count(counting_obj, indi)
            else:
                line = fh.readline()
                while not (line.startswith('0') or line.startswith('1') or line == ""):
                    if bool(re.search('^[0-9] {}'.format(sub_key), line)):
                        counting_obj = _count(counting_obj, indi)
                        break
                    line = fh.readline()
    return counting_obj


if __name__ == '__main__':  # pragma: no cover
    parser = argparse.ArgumentParser(description='this function prints a list to stdout where ' 
                                                 'members of the list are such that they adhere '
                                                 'to some constraint')
    parser.add_argument('-f', '--file', required=True, help="gedcom file")
    parser.add_argument('-b', '--birth', nargs='?', const='birth_only',
                        default=None, help='a toggle to print a list of people with birth dates')
    parser.add_argument('-d', '--death', nargs='?', const='death_only', default=None,
                        help='provide a subkey (e.g. DEAT, PLAC)of the death event that you'
                             'want to count,, or use "" to count deaths only')
    parser.add_argument('-l', '--list', action='store_true', help='list the individual keys (useful for debugging)')

    args = parser.parse_args()

    if args.list:
        counting_obj = []
    else:
        counting_obj = 0

    if args.birth and args.death:
        raise ValueError('this helper/printer function can only return one query response at a time')

    # todo dry this out
    if args.birth:
        fh = _get_file_handler(args.file)
        if args.birth == 'birth_only':
            args.birth = None
        ans = count_subs(fh, 'BIRT', sub_key=args.birth, counting_obj=counting_obj)
        if args.list:
            print('{}'.format('\n'.join(ans)))
        else:
            print('{}'.format(ans))

        fh.close()


    if args.death:
        fh = _get_file_handler(args.file)
        if args.death == 'death_only':
            args.death = None  # necessary to organise arguments correctly - count only deaths now
        ans = count_subs(fh, 'DEAT', sub_key=args.death, counting_obj=counting_obj)
        if args.list:
            print('{}'.format('\n'.join(ans)))
        else:
            print('{}'.format(ans))
        fh.close()

