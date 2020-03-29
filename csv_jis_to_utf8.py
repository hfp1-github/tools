import os
import argparse
from distutils.util import strtobool
import glob
import pandas as pd


def path_append_tag(paths, suffix):
# ファイルパスの拡張子の前にsuffixをつけて返す
    ret_list = []
    for p in paths:
        filename, ext = os.path.splitext(p)
        savepath = filename + suffix + ext
        ret_list.append(savepath)

    return ret_list

parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=\
    '''
       csvの文字コードをshift-jis → utf-8に変換
       dir下のcsvを再起呼び出しする。
    '''
    )

parser.add_argument('dir', help='変換対象が入っているディレクトリ')
parser.add_argument('is_update', help='上書き設定. falseなら_convを付けて保存', type=strtobool)

args = parser.parse_args()

dirpath = os.path.abspath(args.dir)
is_update = args.is_update

# ディレクトリ配下のcsvパス取得
csv_paths = glob.glob(os.path.join(dirpath, '**.csv'), recursive=True)

# 保存パス作成
if is_update:
    savepaths = csv_paths
else:
    savepaths = path_append_tag(csv_paths, '_conv')

# 保存
for p, savepath in zip(csv_paths, savepaths):
    try:
        df = pd.read_csv(p, header=None, encoding='shift-jis')
        df.to_csv(savepath, header=False, index=False, encoding='utf-8')
        print('Success convert: {}'.format(p))
    except:
        print('Failed convert: {}'.format(p))

print('Complete.')