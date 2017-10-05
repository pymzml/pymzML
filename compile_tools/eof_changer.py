#!/usr/bin/env python3
import os, platform

# old mac
def EOF_to_CR(cont):
    cont = cont.replace('\r\n', '\r')
    cont = cont.replace('\n', '\r')
    return cont

# linux mac
def EOF_to_LF(cont):
    cont = cont.replace('\r\n', '\n')
    cont = cont.replace('\r', '\n')
    return cont

# win
def EOF_to_CRLF(cont):
    cont = cont.replace('\n' or '\r', '\r\n')
    return cont

def open_file(file_path):
    f = open(file_path, 'r')
    cont = f.read()
    f.close()
    return cont

def write_file(file_path, cont):
    f = open(file_path, 'w')
    f.write(cont)
    f.close()
    return cont

def detect_os():
    pltf = platform.system()
    # Windows -> platform.system() = Windows
    # Linux   -> platform.system() = Linux
    # Mac     -> platform.system() = Darwin
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
    return EOF_format

def EOF_change_in_file(file_path, EOF_format='OS_dept'):
    if EOF_format == 'OS_dept':
        EOF_format = EOF_format_OS_dept()
    cont = open_file(file_path)
    if EOF_format == 'CRLF':
        cont = EOF_to_CRLF(cont)
    elif EOF_format == 'LF':
        cont = EOF_to_LF(cont)
    elif EOF_format == 'CR':
        cont = EOF_to_CR(cont)
    write_file(file_path, cont)

def EOF_change_in_files(file_pathes, EOF_format='OS_dept'):
    for file_path in file_pathes:
        cont = EOF_change_in_file(file_path, EOF_format)

def EOF_change_in_dir(dir_path, EOF_format='OS_dept'):
    file_pathes = []
    for dir_path,_,file_names in os.walk(dir_path):
        for file_name in file_names:
            file_path = os.path.join(dir_path, file_name)
            file_pathes.append(file_path)
    EOF_change_in_files(file_pathes, EOF_format)

def EOF_change_in_dirs(dir_pathes, EOF_format='OS_dept'):
    for dir_path in dir_pathes:
        EOF_change_in_dir(dir_path, EOF_format)
