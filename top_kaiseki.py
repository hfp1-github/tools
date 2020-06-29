"""
入力するファイルの作り方
top -b -d 0.5 >> top.log
grep -e "top\s-\s" -e python3$ >> top_conv.log
"""

import pandas as pd
import numpy as np
import re

sum_pids = [2293, 2294]

if __name__ == "__main__":
    re_time = re.compile(r'top - (\d{2}:\d{2}:\d{2})')

    filename = "top_conv.log"
    time_all = []
    data_all = []
    index_all = []
    index_count = -1
    with open(filename) as f:
        for line in f:
            time_match = re_time.match(line)
            if time_match is not None:
                t = time_match.group(1)
                index_count += 1
            else:
                time_all.append(t)
                index_all.append(index_count)
                data_all.append(line)
    
    r_space = re.compile(r" +")
    data_all = [r_space.sub(" ", str.strip(s)).split(' ') for s in data_all]

    # DataFrame作成
    # 全カラム
    columns = ['PID', 'USER', 'PR', 'NI', 'VIRT', 'RES', 'SHR', 'S', '%CPU', '%MEM', 'TIME+', 'COMMAND']
    df = pd.DataFrame(data_all, index=index_all, columns=columns)

    # 必要なカラムのみ取り出し
    columns = ['PID', 'USER', 'VIRT', 'RES', 'SHR', 'S', '%CPU', '%MEM', 'TIME+']
    df = df[columns]

    # 時刻追加
    df.insert(0, 'time', time_all)

    # gbyteを変換、terabyteの表示形式調整
    mem_columns = ['VIRT', 'RES', 'SHR']
    for col in mem_columns:
        gb_mask = df[col].str.endswith('g')
        tb_mask = df[col].str.endswith('t')
        df[col][gb_mask] = df['RES'][gb_mask].str.rstrip('g').astype(float)*(1024**2)
        df[col][tb_mask] = df['RES'][tb_mask].str.rstrip('t').astype(float)*(1024**3)

    # 型変換
    # dtype_dict = {'PID': int, 'USER': str, 'PR': str, 'NI': int, 'VIRT': int, 'RES': int, 'SHR': int, 'S': str, '%CPU': float, '%MEM': float, 'TIME+': str, 'COMMAND': str}
    dtype_dict = {'PID': int, 'VIRT': int, 'RES': int, 'SHR': int}
    df = df.astype(dtype_dict)

    # pid毎に分割
    pid_unique = df['PID'].unique()
    df_each_pid = {_pid: df[df['PID'] == _pid] for _pid in pid_unique}
    
    # 保存
    save_names = ['top_log_pid_{}.csv'.format(_pid) for _pid in pid_unique]
    [df_each_pid[key].to_csv(save_name) for key, save_name in zip(df_each_pid, save_names)]

    # 合計
    # インデックスと時刻管理用DataFrame
    df_all_time = pd.DataFrame(data=np.array([index_all, time_all]).T, columns=['index', 'time'])
    df_all_time = df_all_time[~df_all_time.duplicated('index')]
    df_all_time['index'] = df_all_time['index'].astype(int)

    # 累積用バッファ
    sum_columns = ['RES', 'SHR', '%CPU', '%MEM']
    df_sum = pd.DataFrame(index=df_all_time['index'], columns=mem_columns).fillna(0)

    for _pid in sum_pids:
        df_sum = df_sum.add(df_each_pid[_pid][mem_columns], fill_value=0)

    df_sum.index = df_all_time['time']

    # 保存
    df_sum.to_csv('top_log_sum.csv')

