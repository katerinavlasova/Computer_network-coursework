#!/usr/bin/python3

import tkinter as tk
from tkinter import messagebox  
import datetime
import time
import sys

try:
    import curses
except ImportError:
    sys.exit('platform not supported')
import socket
from socket import AF_INET, SOCK_STREAM, SOCK_DGRAM
import psutil
from psutil._common import bytes2human
from psutil._compat import get_terminal_size
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

def show_disks():
    f = open('f.txt', 'w')
    templ = "%-17s %8s %8s %8s %5s%% %9s  %s"
    print(templ % ("Device", "Total", "Used", "Free", "Use ", "Type",
                   "Mount"))
    f.write(templ % ("Device", "Total", "Used", "Free", "Use ", "Type",
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
        f.write('\n')
        f.write(templ % (
            part.device,
            bytes2human(usage.total),
            bytes2human(usage.used),
            bytes2human(usage.free),
            int(usage.percent),
            part.fstype,
            part.mountpoint))
    f.close()
    text = open('f.txt', encoding='utf-8').readlines()
    text = ''.join(text)
    inserter(text)

def show_netinterface():
    af_map = {
    socket.AF_INET: 'IPv4',
    socket.AF_INET6: 'IPv6',
    psutil.AF_LINK: 'MAC',
    }

    duplex_map = {
    psutil.NIC_DUPLEX_FULL: "full",
    psutil.NIC_DUPLEX_HALF: "half",
    psutil.NIC_DUPLEX_UNKNOWN: "?",
    }
    
    f = open('f.txt', 'w')
    stats = psutil.net_if_stats()
    io_counters = psutil.net_io_counters(pernic=True)
    for nic, addrs in psutil.net_if_addrs().items():
        print("%s:" % (nic))
        f.write("%s:" % (nic))
        f.write('\n')
        if nic in stats:
            st = stats[nic]
            print("    stats          : ", end='')
            f.write("    stats          : ")
            print("speed=%sMB, duplex=%s, mtu=%s, up=%s" % (
                st.speed, duplex_map[st.duplex], st.mtu,
                "yes" if st.isup else "no"))
            f.write("speed=%sMB, duplex=%s, mtu=%s, up=%s" % (
                st.speed, duplex_map[st.duplex], st.mtu,
                "yes" if st.isup else "no"))
            f.write('\n')
        if nic in io_counters:
            io = io_counters[nic]
            print("    incoming       : ", end='')
            f.write("    incoming       : ")
            print("bytes=%s, pkts=%s, errs=%s, drops=%s" % (
                bytes2human(io.bytes_recv), io.packets_recv, io.errin,
                io.dropin))
            f.write("bytes=%s, pkts=%s, errs=%s, drops=%s" % (
                bytes2human(io.bytes_recv), io.packets_recv, io.errin,
                io.dropin))
            f.write('\n')
            print("    outgoing       : ", end='')
            f.write("    outgoing       : ")
            print("bytes=%s, pkts=%s, errs=%s, drops=%s" % (
                bytes2human(io.bytes_sent), io.packets_sent, io.errout,
                io.dropout))
            f.write("bytes=%s, pkts=%s, errs=%s, drops=%s" % (
                bytes2human(io.bytes_sent), io.packets_sent, io.errout,
                io.dropout))
            f.write('\n')
        for addr in addrs:
            print("    %-4s" % af_map.get(addr.family, addr.family), end="")
            f.write("    %-4s" % af_map.get(addr.family, addr.family))
            print(" address   : %s" % addr.address)
            f.write(" address   : %s" % addr.address)
            f.write('\n')
            if addr.broadcast:
                print("         broadcast : %s" % addr.broadcast)
                f.write("         broadcast : %s" % addr.broadcast)
                f.write('\n')
            if addr.netmask:
                print("         netmask   : %s" % addr.netmask)
                f.write("         netmask   : %s" % addr.netmask)
                f.write('\n')
            if addr.ptp:
                print("      p2p       : %s" % addr.ptp)
                f.write("      p2p       : %s" % addr.ptp)
                f.write('\n')
        print("")
        f.write("\n")
    f.close()
    text = open('f.txt', encoding='utf-8').readlines()
    text = ''.join(text)
    inserter(text)


def convert_bytes(n):
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.1f%s' % (value, s)
    return "%sB" % n

def procsmem():
    f = open('f.txt', 'w')
    ad_pids = []
    procs = []
    for p in psutil.process_iter():
        with p.oneshot():
            try:
                mem = p.memory_full_info()
                info = p.as_dict(["cmdline", "username"])
            except psutil.AccessDenied:
                ad_pids.append(p.pid)
            except psutil.NoSuchProcess:
                pass
            else:
                p._uss = mem.uss
                p._rss = mem.rss
                if not p._uss:
                    continue
                p._pss = getattr(mem, "pss", "")
                p._swap = getattr(mem, "swap", "")
                p._info = info
                procs.append(p)

    procs.sort(key=lambda p: p._uss)
    templ = "%-7s %-7s %7s %7s %7s %7s %7s"
    print(templ % ("PID", "User", "USS", "PSS", "Swap", "RSS", "Cmdline"))
    f.write(templ % ("PID", "User", "USS", "PSS", "Swap", "RSS", "Cmdline"))
    print("=" * 78)
    f.write('\n')
    f.write("=" * 78)
    for p in procs[:86]:
        cmd = " ".join(p._info["cmdline"])[:50] if p._info["cmdline"] else ""
        line = templ % (
            p.pid,
            p._info["username"][:7] if p._info["username"] else "",
            convert_bytes(p._uss),
            convert_bytes(p._pss) if p._pss != "" else "",
            convert_bytes(p._swap) if p._swap != "" else "",
            convert_bytes(p._rss),
            cmd,
        )
        print(line)
        f.write('\n')
        f.write(line)
    f.close()
    text = open('f.txt', encoding='utf-8').readlines()
    text = ''.join(text)
    inserter(text)

def ps():
    f = open('f.txt', 'w')
    today_day = datetime.today().date()
    templ = "%-10s %5s %5s %7s %7s %5s %6s %6s %6s  %s"
    attrs = ['pid', 'memory_percent', 'name', 'cmdline', 'cpu_times',
             'create_time', 'memory_info', 'status', 'nice', 'username']
    print(templ % ("USER", "PID", "%MEM", "VSZ", "RSS", "NICE",
                   "STATUS", "START", "TIME", "CMDLINE"))
    f.write(templ % ("USER", "PID", "%MEM", "VSZ", "RSS", "NICE",
                   "STATUS", "START", "TIME", "CMDLINE"))
    for p in psutil.process_iter(attrs, ad_value=None):
        if p.info['create_time']:
            ctime = datetime.fromtimestamp(p.info['create_time'])
            if ctime.date() == today_day:
                ctime = ctime.strftime("%H:%M")
            else:
                ctime = ctime.strftime("%b%d")
        else:
            ctime = ''
        if p.info['cpu_times']:
            cputime = time.strftime("%M:%S",
                                    time.localtime(sum(p.info['cpu_times'])))
        else:
            cputime = ''

        user = p.info['username']
        if not user and psutil.POSIX:
            try:
                user = p.uids()[0]
            except psutil.Error:
                pass
        if user and psutil.WINDOWS and '\\' in user:
            user = user.split('\\')[1]
        if not user:
            user = ''
        user = user[:9]
        vms = bytes2human(p.info['memory_info'].vms) if \
            p.info['memory_info'] is not None else ''
        rss = bytes2human(p.info['memory_info'].rss) if \
            p.info['memory_info'] is not None else ''
        memp = round(p.info['memory_percent'], 1) if \
            p.info['memory_percent'] is not None else ''
        nice = int(p.info['nice']) if p.info['nice'] else ''
        if p.info['cmdline']:
            cmdline = ' '.join(p.info['cmdline'])
        else:
            cmdline = p.info['name']
        status = p.info['status'][:5] if p.info['status'] else ''

        line = templ % (
            user,
            p.info['pid'],
            memp,
            vms,
            rss,
            nice,
            status,
            ctime,
            cputime,
            cmdline)
        print(line[:get_terminal_size()[0]])
        f.write('\n')
        f.write(line[:get_terminal_size()[0]])
    f.close()
    text = open('f.txt', encoding='utf-8').readlines()
    text = ''.join(text)
    inserter(text)

def quit_program():
	window.destroy()

window = tk.Tk()
window.geometry('800x600')
mainmenu = tk.Menu(window) 
window.config(menu=mainmenu)

 
domenu = tk.Menu(mainmenu, tearoff=0)
domenu.add_command(label="Активные подключения", command = show_connections)
#domenu.add_command(label="Информация о памяти", command = info_memory)
domenu.add_command(label="Сетевые интерфейсы", command = show_netinterface)
#domenu.add_command(label="Монтированные диски", command = show_disks)
#domenu.add_command(label="Активные пользователи", command = show_users)
#domenu.add_command(label="procsmem", command = procsmem)
#domenu.add_command(label="ps", command = ps)
domenu.add_separator()
domenu.add_command(label="Выход", command = quit_program)


memmenu = tk.Menu(mainmenu, tearoff=0)
memmenu.add_command(label="Монтированные диски", command = show_disks)
memmenu.add_command(label="Информация о памяти", command = info_memory)

procmenu = tk.Menu(mainmenu, tearoff=0)
procmenu.add_command(label="Память процессов", command = procsmem)
procmenu.add_command(label="Состояние процессов", command = ps)

usersmenu = tk.Menu(mainmenu, tearoff=0)
usersmenu.add_command(label="Активные пользователи", command = show_users)

infomenu = tk.Menu(mainmenu, tearoff=0)
infomenu.add_command(label="О программе", command = get_info)
 

mainmenu.add_cascade(label="Сеть",
                     menu=domenu)
mainmenu.add_cascade(label="Процессы",
                     menu=procmenu)
mainmenu.add_cascade(label="Память",
                     menu=memmenu)
mainmenu.add_cascade(label="Пользователи",
                     menu=usersmenu)
mainmenu.add_cascade(label="Информация",
                     menu=infomenu)


output = tk.Text(window, bg="white", padx = 4, width=900, height=900)
#output.grid(row=8, columnspan=99)
output.pack(side=tk.LEFT)
scroll = tk.Scrollbar(command = output.yview)
scroll.pack(side=tk.RIGHT, fill=tk.Y)
output.config(yscrollcommand = scroll.set)
window.mainloop()

