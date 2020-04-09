'''
インデント形式をマークダウンに変換
    入力：クリップボード
    出力：クリップボード
'''

import pyperclip as cl
indent = '    '

text = cl.paste()

# インデントのみの行をサーチ
text_tmp = text.replace(indent, '')
text_tmp = text.splitlines()

blank_ids = []
for n, s in enumerate(text_tmp):
    if s is '':
        blank_ids.append(n)


# マークダウンに変換
text = text.splitlines(keepends=True)
text = [indent + ' ' + s if not n in blank_ids else s.replace(indent, '') for n, s in enumerate(text)]
text = ''.join(text)

text_md = text.replace(indent, '*')

cl.copy(text_md)
