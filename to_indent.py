'''
マークダウン形式をインデント形式に変換
    入力：クリップボード
    出力：クリップボード
'''

import pyperclip as cl

indent = '    '
text = cl.paste()

# マークダウンをインデントに戻す
text = text.replace(r'* ', indent)
text = text.replace(r'*', indent)
cl.copy(text)
