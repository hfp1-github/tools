#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=\
    '''
    サンプルコマンド
    渡された引数をprint
    '''
    )

parser.add_argument('str1')
parser.add_argument('str2')
parser.add_argument('-s', '--str3', default='hoge')

args = parser.parse_args()

for _, arg in args._get_kwargs():
    print(arg)

print(args[0])