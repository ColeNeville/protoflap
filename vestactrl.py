#!/usr/bin/env python
# -*- coding: utf-8 -*-

import serial
import serial.rs485
import sys
import time
import packet
import string

ser = None

def read_and_print(sport, print_it=False):
    s = sport.read(6)
    barr = bytearray(s)
    ll = (barr[5]<<8) + barr[4]
    s2 = sport.read(ll+4)
    barr += bytearray(s2)
    #if print_it:
        #print('Rx:'),
        #for b in barr:
            #print(" %02x" % b),
        #print('')
    return barr

def color_handling(s):
    b = bytearray(s)
    for idx in range(len(b)):
        if chr(b[idx]) == '`':
            b[idx+1] = int(chr(b[idx+1]))

    s=b.translate(None,'`')
    return s

def send_packet(s):
    ser.rts = False # Set high... logic is inverted
    ser.write([s[0]])
    for c in s[1:]:
        if c == 0xfe or c == 0xff:
            #print('escape')
            ser.write([0xfe])
        ser.write([c])
    time.sleep(.005) # Delay
    ser.rts = True # Set low... logic is inverted

def test (string, print_it):

    time.sleep(.5)
    s = color_handling(string)
    # 6 rows instead of 7 now
    val = ' '*(6-len(s))+s
    send_packet(packet.set_targets(0x0001, val, print_it))
    read_and_print(ser, print_it)

    send_packet(packet.arm(0x0001, print_it))
    read_and_print(ser, print_it)

    send_packet(packet.go(0x0001, print_it))
    read_and_print(ser, print_it)

    time.sleep(12)
    # 6 rows insteaad of 7 now
    for i in range(6):
        send_packet(packet.reg_read(0x0001, packet.REG_REV_COUNT_0+i, print_it))
        res = read_and_print(ser, print_it)
        count = (res[9]<<8)+res[8]
        #print('%d,' % count),
    #print('%s,' % string)
# 22 col instead of 23 now
all_columns = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]
#all_columns = [1, 2, 3, 4, 5, 6, 7, 8]

def init_all_columns():
    for c in all_columns:
        send_packet(packet.reg_write(c, packet.REG_INDEX_ADJUST, 20))
        read_and_print(ser)
        send_packet(packet.reg_write(c, packet.REG_ROTATE_NOP, 0))
        read_and_print(ser)
        send_packet(packet.reg_write(c, packet.REG_ONE_REV_MIN, 0))
        read_and_print(ser)
        #send_packet(packet.reg_write(c, packet.REG_FREQ_D, 5))
        #read_and_print(ser)
        #send_packet(packet.reg_write(c, packet.REG_FREQ_N, 2))
        #read_and_print(ser)

def print_board(rows,print_it=True):
    if print_it:
        print('#'*24)
        for l in rows: 
            # 22 col insteaed of 23 now
            print '#' + ('%-22s' % l) + '#'
        print('#'*24)
        for l in rows:
            print " ".join("{:02x}".format(ord(c)) for c in l)


def setup_digits(strings, left_to_right_swap = False, real_hw=True):
    #print('string sent in app: %s') % strings
    #print('string length: %d') % len(strings)
    print_it = True
    # digits raw major
    # 22 col instead of 23 and 6 rows instead of  now
    #drm = ['\x00'*22, '\x00'*22, '\x00'*22, '\x00'*22, '\x00'*22, '\x00'*22]
    drm = [' '*22, ' '*22, ' '*22, ' '*22, ' '*22, ' '*22]
    # 6 rows instead of 7 now
    offset = (6-len(strings))/2
    max_len = 0
    for idx in range(len(strings)):
        s = strings[idx]
        # 22 col instaed of 23 now
        s = color_handling(s)[:22]
        if left_to_right_swap:
            s = s[::-1]
        if len(s) > max_len:
            max_len = len(s)
        # 22 col insteaad of 23 now
        drm[offset+idx] = ('%-22s' % s)
    #print_board(drm)
    #print('Length of DRM: %d') % len(drm)
    for idx in range(len(drm)):
        #print('IDX: %d') % idx
        initial_length = len(drm[idx])
        whitespace_number = drm[idx].count(' ')
        final_length = initial_length - whitespace_number
        left_side = (22-final_length)/2
        #print('left side: %d') % left_side
        right_side = 22 - left_side - final_length
        #print('right side: %d') % right_side
        # 22 col instead of 23 now
        drm[idx] = drm[idx].replace(' ', '')
        drm[idx] = ('%-22s' % (('\x00'*(left_side)) + drm[idx] + ('\x00'*(right_side))))[:22]
    #print 'Rows: %d' % len(drm)
    #print 'Max Len: %d' % max_len
    #print_board(drm)
    # 6 row instead of 7 now
    while len(drm) < 6:
        # 22 col insteaad of 23 now
        drm.append('%-22s' % '\x00')
    # digits column major
    dcm = []
    # 6 row instead of 7 now
    tups = zip(drm[0], drm[1], drm[2], drm[3], drm[4], drm[5])
    #tups = zip(drm[0])
    for t in tups:
       dcm.append(''.join(t))
    #print('tups: %s') % tups
    if real_hw:
        for idx in range(len(all_columns)):
            #print 'idx: %d' % idx
            #print '>>>> [%d] %s' % (idx+1, dcm[idx][::-1])
##############################################################################################
            send_packet(packet.set_targets(idx+1, dcm[idx][::-1], print_it))
            read_and_print(ser, print_it)
            send_packet(packet.arm(idx+1, print_it))
            read_and_print(ser, print_it)

        send_packet(packet.go(0x0001, print_it))
        read_and_print(ser, print_it)
        #print('skipping stuff...')
##############################################################################################
    #else:
        #print tups

def emc_blanks():
    setup_digits(['`7`7`7`7`7`7`7`7`7`7`7`7`7`7`7`7`7`7`7`7`7`7', '`7`7`7`7`7`7`7`7`7`7`7`7`7`7`7`7`7`7`7`7`7`7', '`7`7`7`7`7`7`7`7`7`7`7`7`7`7`7`7`7`7`7`7`7`7', '`7`7`7`7`7`7`7`7`7`7`7`7`7`7`7`7`7`7`7`7`7`7', '`7`7`7`7`7`7`7`7`7`7`7`7`7`7`7`7`7`7`7`7`7`7', '`7`7`7`7`7`7`7`7`7`7`7`7`7`7`7`7`7`7`7`7`7`7'], left_to_right_swap=True)

def blanks():
    #for c in all_columns:
    #    send_packet(packet.reg_write(c, packet.REG_FREQ_D, 8))
    #    read_and_print(ser)
    #    send_packet(packet.reg_write(c, packet.REG_FREQ_N, 2))
    #    read_and_print(ser)
    setup_digits(['`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0', '`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0', '`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0', '`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0', '`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0', '`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0'], left_to_right_swap=True)
    #setup_digits(['', '', '', '', '', ''], left_to_right_swap=True)

def test_long_blanks():
    #for c in all_columns:
    #    send_packet(packet.reg_write(c, packet.REG_FREQ_D, 8))
    #    read_and_print(ser)
    #    send_packet(packet.reg_write(c, packet.REG_FREQ_N, 2))
    #    read_and_print(ser)
    setup_digits(['`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0', '`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0', '`0`0`0`0`0`0`0`0`0TEST`0`0`0`0`0`0`0`0`0', '`0`0`0`0`0LONG`0MESSAGE`0`0`0`0`0', '`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0', '`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0'], left_to_right_swap=False)
    #setup_digits(['', '', '', '', '', ''], left_to_right_swap=True)

def test_rapid_blanks():
    #for c in all_columns:
    #    send_packet(packet.reg_write(c, packet.REG_FREQ_D, 8))
    #    read_and_print(ser)
    #    send_packet(packet.reg_write(c, packet.REG_FREQ_N, 2))
    #    read_and_print(ser)
    setup_digits(['`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0', '`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0', '`0`0`0`0`0`0`0`0`0TSET`0`0`0`0`0`0`0`0`0', '`0`0`0NOISSECCUS`0DIPAR`0`0`0', '`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0', '`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0'], left_to_right_swap=True)
    #setup_digits(['', '', '', '', '', ''], left_to_right_swap=True)

def test_check_blanks():
    #for c in all_columns:
    #    send_packet(packet.reg_write(c, packet.REG_FREQ_D, 8))
    #    read_and_print(ser)
    #    send_packet(packet.reg_write(c, packet.REG_FREQ_N, 2))
    #    read_and_print(ser)
    setup_digits(['`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0', '`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0', '`0`0`0`0`0`0`0`0`0TSET`0`0`0`0`0`0`0`0`0', '`0`0`0`0`0`0KCEHC`0PALF`0`0`0`0`0`0', '`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0', '`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0'], left_to_right_swap=True)
    #setup_digits(['', '', '', '', '', ''], left_to_right_swap=True)

def test_power_blanks():
    setup_digits(['`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0', '`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0', '`0`0`0`0`0`0`0`0`0TSET`0`0`0`0`0`0`0`0`0', '`0`0`0`0`0`0WARD`0REWOP`0`0`0`0`0`0', '`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0', '`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0`0'], left_to_right_swap=True)

def board_init_uart(): 
    global ser
    #tty = '/dev/ttyUSB0'
    tty = '/dev/ttyAMA0'
    ser = serial.Serial(tty, 38400) 

#def main(ser, args):
#    init_all_columns()
#
#    blanks()
#    time.sleep(15)
#    setup_digits(['vestaboard', 'welcome to', 't', 'e', 's', 't', '#'], left_to_right_swap=True)
#    time.sleep(15)
#    setup_digits(['colors   `1`2`3', '`4`5`6  samples', '', '', '', '', ''], left_to_right_swap=True)
#    time.sleep(15)
#    setup_digits(['`0`1`2`3`4`5`6`5`4`3`2`1', '`6`5`4`3`2`1`0`1`2`3`4`5', '', '', '', '', ''], left_to_right_swap=True)
#    time.sleep(15)
#    blanks()
#
#if __name__ == '__main__':
#    tty = '/dev/ttyUSB0'
#    with serial.Serial(tty, 38400) as ser:
#        main(ser, sys.argv[1:])
