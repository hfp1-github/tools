import os
import pandas as pd
import numpy as np
import argparse, textwrap
from distutils.util import strtobool

parser = argparse.ArgumentParser(
    formatter_class=argparse.RawTextHelpFormatter,
    description=\
        textwrap.dedent('''\
            csvをnpyに変換
        '''
    ))

parser.add_argument('filepath', help='変換対象')
parser.add_argument('exists_header', help='入力ファイルにヘッダがあるかどうか', type=strtobool)
parser.add_argument('exists_index', help='入力ファイルにインデックスがあるかどうか', type=strtobool)

# ---parse
args = parser.parse_args()
filepath = args.filepath
exists_header = 0 if args.exists_header else None
index_col = 0 if args.exists_index else None

print('--- Start.')
if not os.path.exists(filepath):
    raise Exception('File {} is not found.'.format(filepath))

filename, _ = os.path.splitext(filepath)
df = pd.read_csv(filepath, encoding='utf-8', header=exists_header, index_col=index_col)
np.save(filename + '.npy', df.values)

print('--- End.')
