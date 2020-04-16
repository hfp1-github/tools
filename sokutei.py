import os
import sys
import re
import pandas as pd
from time import sleep
import subprocess
from datetime import datetime as dt
import argparse, textwrap
import cProfile
import pstats
import io

ps_columns = 'pid,rss,cmd'

def output_cProfile_to_text(filepath):
    s = io.StringIO()
    ps = pstats.Stats(filepath, stream=s).sort_stats('cumtime')
    ps.print_stats()
    filename, _ = os.path.splitext(filepath)

    with open(filename + '.txt', 'w') as f:
        f.write(s.getvalue())

def run_test(command, prefix='', interval=1):
    print('Command: {}'.format(command))
    with open('{}_command.txt'.format(prefix), 'w', encoding='utf-8') as f:
        f.write(command)

    profile_path = '{}_profile.stats'.format(prefix)
    _command = 'python3 -m cProfile -o {} {}'.format(profile_path, command)
    _command = re.split(' +', _command)

    # psコマンド(grepとこのファイルの実行を除外)
    ps_cmd = 'ps a -o {} | grep -v grep | grep -v *{} |  grep "{}"'.format(ps_columns, __file__, command)
    timestamp_fmt = "%Y/%m/%d %H:%M:%S"

    # topコマンド
    # top_grep_cmd = 'top -c -n 1 | grep -v grep | grep -v *{} |  grep "{}"'.format(__file__, command)
    # top_grep_cmd = 'top -c -n 1 -o \%CPU | grep -v grep | grep "{}"'.format(__file__, command)
    # top_all_cmd = top_all_cmd.split(' ')
    # print(top_grep_cmd)
    ret = None
    ps_grep = []
    ps_time = []
    top_grep = []

    try:
        # コマンド実行
        proc_main = subprocess.Popen(_command, shell=False, stderr=subprocess.PIPE, stdout=subprocess.PIPE, encoding='utf-8')
        # proc_top_all = subprocess.Popen(top_all_cmd, shell=False, stdout=subprocess.PIPE, encoding='utf-8')
        # proc
        proc_cmd = 'cat /proc/{}/status'.format(proc_main.pid)
        top_grep_cmd = 'top -p {} -c -n 1 -o \%CPU | grep python3'.format(proc_main.pid)
        print(proc_main.pid)
        # プロセス終了(ret = None)までループ
        while ret is None:
            proc_status = subprocess.Popen(proc_cmd, shell=True, stdout=subprocess.PIPE, encoding='utf-8')
            proc_status_str = str(proc_status.communicate()[0])
            
            ps_proc = subprocess.Popen(ps_cmd, shell=True, stdout=subprocess.PIPE, encoding='utf-8')
            ps_grep.append(str(ps_proc.communicate()[0]))
            ps_time.append(str(dt.now().strftime(timestamp_fmt)))

            proc_top_all = subprocess.Popen(top_grep_cmd, shell=True, stdout=subprocess.PIPE, encoding='utf-8')
            top_grep.append(str(proc_top_all.communicate()[0]))


            sleep(interval)
            ret = proc_main.poll()
    except Exception as e:
        print(e)
        print("error")
        # console
        with open('{}_console.txt.'.format(prefix), 'w', encoding='utf-8') as f:
            f.write(str(proc_main.communicate()[0]))
        proc_main.kill()
        return

    # ---後処理
    # top
    top_str = [re.split(" +", str.rstrip(s)) for s in top_grep]
    # import pdb; pdb.set_trace()
    top_str = [s if s[0] != '' else s[1:] for s in top_str]
    df_top = pd.DataFrame(top_str)
    df_top.to_csv('{}_top.csv'.format(prefix), index=False, header=False, encoding='utf-8')

    # ps: スペースでsplit → csv保存
    ps_str = [re.split(" +", str.rstrip(s)) for s in ps_grep]
    ps_str = [s if s[0] != '' else s[1:] for s in ps_str]
    df_ps = pd.DataFrame(ps_str, index=ps_time)
    df_ps = df_ps.iloc[:,:len(ps_columns.split(','))]
    df_ps.columns = ps_columns.split(',')
    df_ps['cpu_top'] = df_top.iloc[:,8].values # topの%cpuを取り込み
    df_ps.to_csv('{}_ps.csv'.format(prefix), encoding='utf-8')

    # console
    with open('{}_console.txt.'.format(prefix), 'w', encoding='utf-8') as f:
        f.write(str(proc_main.communicate()[0]))

    # proc
    with open('{}_proc.txt'.format(prefix), 'w', encoding='utf-8') as f:
        f.write(proc_status_str)
    
    output_cProfile_to_text(profile_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description=\
            textwrap.dedent('''\
                pythonコマンド用の性能測定ツールです。
            '''
        ))

    parser.add_argument('command', nargs='+', 
                        help= textwrap.dedent('''\
                        測定対象のスクリプトと引数。
                        「python」は記載不要。
                        '''))
    parser.add_argument('-p', '--prefix', help='出力ファイルに付けるprefix', default='')
    parser.add_argument('-i', '--interval', help='ps, procの実行間隔(秒)', type=float, default=1.0)

    # ---parse
    args = parser.parse_args()
    command = " ".join(args.command)
    run_test(command, args.prefix, args.interval)