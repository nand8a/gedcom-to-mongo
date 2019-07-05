
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


def get_death_date(filename):  # pragma: no cover
    """
    get a death and date for each individual
    :param filename:
    :return:
    """
    indi_list = []
    with open(filename, 'r', encoding='utf-8-sig') as f:
        for line in f:
            if bool(re.search('0 @[A-Z0-9]*@ INDI', line)):
                indi = line
            if bool(re.search('^1 DEAT$', line)):
                line = f.readline()
                if bool(re.search('^2 DATE', line)):
                    indi_list.append(indi.replace('\n', ''))
    return indi_list


if __name__ == '__main__':  # pragma: no cover
    parser = argparse.ArgumentParser(description='this function prints a list to stdout where ' 
                                                 'members of the list are such that they adhere '
                                                 'to some constraint')
    parser.add_argument('-f', '--file', required=True, help="gedcom file")
    parser.add_argument('-b', '--birth', action='store_true', help='a toggle to print a list of people with birth dates')
    parser.add_argument('-d', '--death', action='store_true', help='a toggle to print a list of people with death dates')

    args = parser.parse_args()

    if args.birth and args.death:
        raise ValueError('this helper/printer function can only return one query response at a time')

    if args.birth:
        print('{}'.format('\n'.join(get_birth_date(args.file))))

    if args.death:
        print('{}'.format('\n'.join(get_death_date(args.file))))
