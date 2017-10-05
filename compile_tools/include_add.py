#!/usr/bin/env python3
import os, platform

def open_file(file_path):
    f = open(file_path, 'r')
    cont = f.read()
    f.close()
    return cont

def open_file_lines(file_path):
    f = open(file_path, 'r')
    cont_lines = f.readlines()
    f.close()
    return cont_lines

def write_file(file_path, cont):
    f = open(file_path, 'w')
    f.write(cont)
    f.close()
    return cont

def detect_os():
    pltf = platform.system()
    return pltf

def EOF_format_OS_dept():
    pltf = detect_os()
    EOF_format = 'unknown'
    if pltf == 'Windows':
        EOF_format = 'CRLF'
    elif pltf == 'Linux':
        EOF_format = 'LF'
    elif pltf == 'Darwin':
        EOF_format = 'LF'
    else:
        EOF_format = 'LF'
    return EOF_format

def EOF_format_select(EOF_format='OS_dept'):
    if EOF_format == 'OS_dept':
        EOF_format = EOF_format_OS_dept()
    if EOF_format == 'CRLF':
        EOF_format_char = '\r\n'
    elif EOF_format == 'LF':
        EOF_format_char = '\n'
    elif EOF_format == 'CR':
        EOF_format_char = '\r'
    return EOF_format_char

def create_add_format(insertions, check_insertions, EOF_format='OS_dept'):
    add_list = []
    add_format = ''

    for num in range(len(insertions)):
        if check_insertions[num] is True:
            add_list.append(insertions[num])
    if len(add_list) == 0:
        return add_format
    EOF_format_char = EOF_format_select(EOF_format)

    for add_item in add_list:
        add_format = add_format + add_item + EOF_format_char
    return add_format

def check_line_word(lines, words):
    EOF_format = None
    if len(lines) >= 1:
        if lines[0].find('\r\n') >= 0:
            EOF_format = 'CRLF'
        elif lines[0].find('\n') >= 0:
            EOF_format = 'LF'
        elif lines[0].find('\r') >= 0:
            EOF_format = 'CR'
    check_words = [True for word in words]
    for line in lines:
        line = line.replace('\n', '').replace('\r', '')
        for num in range(len(words)):
            if line == words[num]:
                check_words[num] = False
                if (True in check_words) is False:
                    return check_words, EOF_format
                break
    return check_words, EOF_format

def add_insertions_into_file(file_path, insertions, EOF_format=None):
    cont_lines = open_file_lines(file_path)
    check_insertions, file_EOF_format = check_line_word(cont_lines, insertions)
    if file_EOF_format is None:
        file_EOF_format = 'OS_dept'
    if EOF_format is None:
        EOF_format = file_EOF_format

    add_lines = create_add_format(insertions, check_insertions, EOF_format)
    if add_lines != '':
        cont = open_file(file_path)
        cont = add_lines + cont
        write_file(file_path, cont)

def add_insertions_into_files(file_pathes, insertions, EOF_format=None):
    for file_path in file_pathes:
        cont = add_insertions_into_file(file_path, insertions, EOF_format)

def add_insertions_into_dir(dir_path, insertions, EOF_format=None):
    file_pathes = []
    for dir_path,_,file_names in os.walk(dir_path):
        for file_name in file_names:
            file_path = os.path.join(dir_path, file_name)
            file_pathes.append(file_path)
    add_insertions_into_files(file_pathes, insertions, EOF_format)

def add_insertions_into_dirs(dir_pathes, insertions, EOF_format=None):
    for dir_path in dir_pathes:
        add_insertions_into_dir(dir_path, insertions, EOF_format)
