import os
import shutil
import glob
import json

def search_diff(pre_states, current_states):
    '''
    過去vs現在でディレクトリ内を比較し、以下をリストで返す。
        ・更新日時に差分があるファイルパス
        ・新規作成されたディレクトリパス
    '''

    diff_file = []
    diff_dir = []
    for path, mtime in current_states.items():
        if path in pre_states:
            if not pre_states[path] == current_states[path]:
                if os.path.isfile(path):
                    diff_file.append(path)
        else:
            if os.path.isfile(path):
                diff_file.append(path)
            else:
                diff_dir.append(path)

    return diff_file, diff_dir

def create_check_point(dirpath):
    current_dir = os.getcwd()
    # 現在の状態取得
    os.chdir(dirpath)
    paths = glob.glob('**', recursive=True)
    current_states = {f:os.stat(f).st_mtime for f in paths}
    os.chdir(current_dir)
    
    # 状態を保存
    root_dir = os.path.abspath(os.path.dirname(dirpath))
    savefile_name = 'check_point_{}.json'.format(os.path.basename(dirpath))
    save_dir = os.path.join(root_dir, '__diff_check_point')
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)

    with open(os.path.join(save_dir,savefile_name), "w", encoding='utf-8') as f:
        json.dump(current_states, f, ensure_ascii=False, indent=4, sort_keys=False, separators=(',', ': '))

    print('  Created check point file.\n  {}'.format(os.path.join(save_dir,savefile_name)))

def output_diff(dirpath, output_dir, update_save_point=True):
    # 絶対パスに変換
    dirpath = os.path.abspath(dirpath)
    output_dir = os.path.abspath(output_dir)

    root_dir = os.path.abspath(os.path.dirname(dirpath))

    # セーブポイントロード
    savefile_name = 'check_point_{}.json'.format(os.path.basename(dirpath))
    save_dir = os.path.join(root_dir, '__diff_check_point')
    with open(os.path.join(save_dir,savefile_name), "r", encoding='utf-8') as f:
        pre_states = json.load(f)

    # 現在の状態を取得
    os.chdir(dirpath)
    paths = glob.glob('**', recursive=True)
    current_states = {f:os.stat(f).st_mtime for f in paths}

    # 差分取得
    diff_file, diff_dir = search_diff(pre_states, current_states)
    _diff_file_dirs = set([os.path.dirname(p) for p in diff_file if os.path.isfile(p)])
    diff_file_dirs = [p for p in _diff_file_dirs if p != '']

    print('diff:\nfiles: {}\ndir: {}'.format(diff_file, diff_dir))


    # 差分コピー先のディレクトリ構造を生成
    os.chdir(output_dir)
    [os.makedirs(p, exist_ok=True) for p in diff_file_dirs]
    [os.makedirs(p, exist_ok=True) for p in diff_dir]

    # 差分をコピー
    [shutil.copyfile(os.path.join(dirpath, p), p) for p in diff_file]

    if update_save_point:
        with open(os.path.join(save_dir,savefile_name), "w", encoding='utf-8') as f:
            json.dump(current_states, f, ensure_ascii=False, indent=4, sort_keys=False, separators=(',', ': '))

    os.chdir(root_dir)
    

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=\
        '''
        ファイル差分検出スプリクト。
        予めチェックポイントを作成し、チェックポイントと現在での差分を検出し、ファイル出力する。
        '''
        )

    parser.add_argument('dir', help='差分を取るディレクトリ')
    parser.add_argument('-o', '--output_dir', help='差分を出力するディレクトリ', default=None)
    parser.add_argument('-u', '--update_check_point', help='チェックポイントの上書き設定', default='t')

    args = parser.parse_args()

    update_save_point = args.update_check_point == 't'

    if not args.output_dir:
        create_check_point(args.dir)

        if not os.path.exists(args.output_dir):
            os.makedirs(args.output_dir, exist_ok=True)

        output_diff(args.dir, args.output_dir, update_save_point)
