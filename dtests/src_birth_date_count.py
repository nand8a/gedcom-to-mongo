
import argparse
import re


# move to unittest like setup
def get_indi(filename):  # pragma: no cover
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


if __name__ == '__main__': # pragma: no cover
    parser = argparse.ArgumentParser('test')
    parser.add_argument('-f', '--file', required=True, help="gedcom file")

    args = parser.parse_args()
    print('{}'.format('\n'.join(get_indi(args.file))))

