#!/usr/bin/python3

import tkinter as tk
from tkinter import messagebox  

import socket
from socket import AF_INET, SOCK_STREAM, SOCK_DGRAM
import psutil
from psutil._common import bytes2human
from datetime import datetime
import os
import sys

def inserter(value):
    output.delete("0.0", "end")
    output.insert("1.0", value)

def get_info():
    messagebox.showinfo('О программе...', 'Курсовая работа \nМониторинг сетевой активности \n' \
                        'Преподаватель: Рогозин Н.О. \n' \
                        'Студент: Власова Е.В. ИУ7-74Б \n' \
                        '2020 г.')

def show_connections():
    f = open('f.txt', 'w')
    AD = "-"
    AF_INET6 = getattr(socket, 'AF_INET6', object())
    proto_map = {
        (AF_INET, SOCK_STREAM): 'tcp',
        (AF_INET6, SOCK_STREAM): 'tcp6',
        (AF_INET, SOCK_DGRAM): 'udp',
        (AF_INET6, SOCK_DGRAM): 'udp6',
        }

    templ = "%-5s %-30s %-30s %-13s %-6s %s"
    print(templ % (
        "Proto", "Local address", "Remote address", "Status", "PID",
        "Program name"))
    f.write(templ % (
        "Proto", "Local address", "Remote address", "Status", "PID",
        "Program name"))
    proc_names = {}
    for p in psutil.process_iter(['pid', 'name']):
        proc_names[p.info['pid']] = p.info['name']
    for c in psutil.net_connections(kind='inet'):
        f.write('\n')
        laddr = "%s:%s" % (c.laddr)
        raddr = ""
        if c.raddr:
            raddr = "%s:%s" % (c.raddr)
        name = proc_names.get(c.pid, '?') or ''
        print(templ % (
            proto_map[(c.family, c.type)],
            laddr,
            raddr or AD,
            c.status,
            c.pid or AD,
            name[:15],
        ))
        f.write(templ % (
            proto_map[(c.family, c.type)],
            laddr,
            raddr or AD,
            c.status,
            c.pid or AD,
            name[:15],
        ))
    f.close()
    text = open('f.txt', encoding='utf-8').readlines()
    text = ''.join(text)
    inserter(text)

def show_users():
    users = psutil.users()
    f = open('f.txt', 'w')
    for user in users:
        proc_name = psutil.Process(user.pid).name() if user.pid else ""
        print("%-12s %-10s %-10s %-14s %s" % (
            user.name,
            user.terminal or '-',
            datetime.fromtimestamp(user.started).strftime("%Y-%m-%d %H:%M"),
            "(%s)" % user.host if user.host else "",
            proc_name
        ))
        f.write("%-12s %-10s %-10s %-14s %s" % (
            user.name,
            user.terminal or '-',
            datetime.fromtimestamp(user.started).strftime("%Y-%m-%d %H:%M"),
            "(%s)" % user.host if user.host else "",
            proc_name
        ))
    f.close()
    text = open('f.txt', encoding='utf-8').readlines()
    text = ''.join(text)
    inserter(text)

def pprint_ntuple(nt):
    f = open('f.txt', 'a')
    for name in nt._fields:
        value = getattr(nt, name)
        if name != 'percent':
            value = bytes2human(value)
        print('%-10s : %7s' % (name.capitalize(), value))
        f.write('\n')
        f.write('%-10s : %7s' % (name.capitalize(), value))
    f.close()
    text = open('f.txt', encoding='utf-8').readlines()
    text = ''.join(text)
    inserter(text)

def show_disks():
    templ = "%-17s %8s %8s %8s %5s%% %9s  %s"
    print(templ % ("Device", "Total", "Used", "Free", "Use ", "Type",
                   "Mount"))
    for part in psutil.disk_partitions(all=False):
        if os.name == 'nt':
            if 'cdrom' in part.opts or part.fstype == '':
                # skip cd-rom drives with no disk in it; they may raise
                # ENOENT, pop-up a Windows GUI error for a non-ready
                # partition or just hang.
                continue
        usage = psutil.disk_usage(part.mountpoint)
        print(templ % (
            part.device,
            bytes2human(usage.total),
            bytes2human(usage.used),
            bytes2human(usage.free),
            int(usage.percent),
            part.fstype,
            part.mountpoint))

def info_memory():
    f = open('f.txt', 'w')
    f.write('MEMORY\n------')
    f.close()
    print('MEMORY\n------')
    pprint_ntuple(psutil.virtual_memory())
    f = open('f.txt', 'a')
    f.write('\nSWAP\n----')
    f.close()
    print('\n\nSWAP\n----')
    pprint_ntuple(psutil.swap_memory())

window = tk.Tk()
window.geometry('800x600')
mainmenu = tk.Menu(window) 
window.config(menu=mainmenu)

 
domenu = tk.Menu(mainmenu, tearoff=0)
domenu.add_command(label="Активные подключения", command = show_connections)
domenu.add_command(label="Информация о памяти", command = info_memory)
domenu.add_command(label="Сетевая статистика")
domenu.add_command(label="Монтированные диски", command = show_disks)
domenu.add_command(label="Активные пользователи", command = show_users)
domenu.add_separator()
domenu.add_command(label="Выход")

infomenu = tk.Menu(mainmenu, tearoff=0)
infomenu.add_command(label="О программе", command = get_info)
 

mainmenu.add_cascade(label="Действия",
                     menu=domenu)
mainmenu.add_cascade(label="Информация",
                     menu=infomenu)


output = tk.Text(window, bg="white", padx = 4, width=900, height=900)
output.grid(row=8, columnspan=99)

window.mainloop()

