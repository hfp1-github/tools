import subprocess
import diff_exporter
import os

output_setting = ' > test/console.txt 2>&1'
target_dir = 'test'

with open('commands.txt', 'r') as f:
    commands = f.readlines()

shells = []
savedirs = []
for line in commands:
    buf = tuple(str.split(line, '##'))
    savedirs.append(buf[0])
    shells.append(buf[1][:-1] + output_setting)

diff_exporter.create_check_point(target_dir)

for savedir, shell in zip(savedirs, shells):
    print(shell)
    subprocess.call(shell, shell=True)
    os.makedirs(savedir, exist_ok=True)
    diff_exporter.output_diff(target_dir, savedir)
