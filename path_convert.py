import pyperclip as cl

path = cl.paste()
path_convert = path.replace('\\', '/')
cl.copy(path_convert)
