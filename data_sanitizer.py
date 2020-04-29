import sys
import pandas as pd


def sanitize(argv):
    data = pd.read_csv(argv[1], delimiter='\t', decimal=",")
    data.loc[data['Point'] == 'non', 'Point'] = '10'
    data.to_csv(argv[2], encoding='utf-8', header=False, index=False,
                columns=['0ртм', '1ртм', '2ртм', '3ртм', '4ртм', '5ртм', '6ртм', '7ртм', '8ртм', '0ик', '1ик', '2ик',
                         '3ик', '4ик', '5ик', '6ик', '7ик', '8ик', 'Result', 'Point'])


if __name__ == '__main__':
    if len(sys.argv) > 1:
        sanitize(sys.argv)
