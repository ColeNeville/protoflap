
import crc
import serial
import time

OP_SET_TARGETS = 0x01
OP_ARM = 0x02
OP_GO = 0x03
OP_PING = 0x04
OP_REG_WRITE = 0x05
OP_REG_READ = 0x06


REG_INDEX_ADJUST = 0
REG_ROTATE_NOP = 1
REG_ONE_REV_MIN = 2
REG_REV_COUNT_0 = 3
REG_REV_COUNT_1 = 4
REG_REV_COUNT_2 = 5
REG_REV_COUNT_3 = 6
REG_REV_COUNT_4 = 7
REG_REV_COUNT_5 = 8
REG_REV_COUNT_6 = 9
REG_FREQ_D      = 10 
REG_FREQ_N      = 11
REG_CRC_ERRORS  = 12
REG_ZERO_NOISE  = 13


def build(address, flags, payload, print_it=True):
    packet_len = 1+2+1+2+len(payload)+4
    b = bytearray(packet_len)
    b[0] = 0xff
    b[1] = address & 0xff
    b[2] = address >> 8
    b[3] = flags
    b[4] = len(payload) & 0xff
    b[5] = len(payload) >> 8
    b[6:6+len(payload)] = payload
    b[6+len(payload)+0] = 0xff
    b[6+len(payload)+1] = 0xff
    b[6+len(payload)+2] = 0xff
    b[6+len(payload)+3] = 0xff
    crc32 = crc.CRC32(b, packet_len - 4);
    b[6+len(payload)+0] = (crc32 >> (0*8)) & 0xff
    b[6+len(payload)+1] = (crc32 >> (1*8)) & 0xff
    b[6+len(payload)+2] = (crc32 >> (2*8)) & 0xff
    b[6+len(payload)+3] = (crc32 >> (3*8)) & 0xff
    #if print_it:
        #print('Tx: %s' % (('xxxx','STGT', 'ARM ', 'GO  ', 'PING', 'REGW', 'REGR')[b[6]]) ),
        #for bb in b:
            #print(" %02x" % bb),
        #print('')

    return b

def ping(address, print_it=True):
    return build(address, 0, [0x04, 0x00, 0x00], print_it)

def set_targets(address, targets, print_it=True):
    payload = bytearray(8)
    payload[0] = OP_SET_TARGETS
    for i in range(len(payload)-1):
        if i < len(targets):
            payload[i+1] = targets[i]
        else:
            payload[i+1] = ' '
    return build(address, 0, payload, print_it)

def arm(address, print_it=True):
    return build(address, 0, [OP_ARM], print_it)

def go(address, print_it=True):
    return build(address, 0, [OP_GO], print_it)

def reg_write(address, reg, val, print_it=True):
    return build(address, 0, [OP_REG_WRITE, reg & 0xff, ((val>>8)&0xff), val & 0xff], print_it)
def reg_read(address, reg, print_it=True):
    return build(address, 0, [OP_REG_READ, reg & 0xff], print_it)

def send(sport, s):
    sport.rts = False # Set high... logic is inverted
    sport.write([s[0]])
    for c in s[1:]:
        if c == 0xfe or c == 0xff:
            sport.write([0xfe])
        sport.write([c])
    time.sleep(.01) # Delay
    sport.rts = True # Set low... logic is inverted
