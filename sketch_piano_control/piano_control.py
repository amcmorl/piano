import serial
import time
import sys
import struct

'''
target_time = timer_resolution * (timer_counts + 1)
=> timer_counts = target_time / timer_resolution
timer resolution is (for 1024 prescaler) 1 / (16 * 10^6 / 1024)
=> timer_counts = target_time / (6.4e-5 s)
'''

# communication options
dev = ''
if sys.platform == 'linux2':
    dev = '/dev/ttyACM'
elif sys.platform == 'win32':
    dev = 'COM4'
else:
    dev = 'unknown'
    raise ValueError('platform %s not known' % (sys.platform))
baud = 115200
timer_resolution = 1. / (16e6 / 1024) # s

# pin defines
# Drawing Number ses0662
# Sheet Number DHMARDIO
LM = 0b00000010
LI = 0b00000100
RI = 0b00001000
RM = 0b00010000
CT = 0b00100000
T1 = 0b1000000000000000 # (on port D)
T2 = 0b0100000000000000 # ('')

egfile = '../ajcm_test.txt'

def start_serial(port_id=0):
    '''
    check that arduino is talking correctly
    
    we expect to receive 's0'
    '''
    # add number to unknown linux serial port address
    if dev == '/dev/ttyACM':
        dev_str = dev + str(port_id)
    else:
        dev_str = dev
        
    # create serial interface
    ser = serial.Serial(dev_str, baud)
    
    # give arduino time to start
    time.sleep(2)
    
    # check we have 's0' as last elements of the serial in buffer
    if ser.inWaiting() == 0:
        ser.close()
        raise ValueError('Handshake not received. ')
        
    # read everything we've got
    serBuf = ''
    while ser.inWaiting() > 0:
        serBuf += ser.read()
    if not serBuf[-2:] == 's0':
        ser.close()
        raise ValueError('Received %s instead of handshake. ' \
            % serBuf[-2:] + 'Try (re)starting arduino first.')
    return ser

def send_port(bitpat, ser, pad=True):
    '''
    'b' is the handshake code for the bitpat
    '''
    outstr = chr(bitpat >> 8) + chr(bitpat & 0b11111111) \
        + ('abcd' if pad else '')
    ser.write(outstr)

def get_timer_counts(target_time):
    '''
    Parameters
    ----------
    target_time : int
        time (ms)
    '''
    return int(target_time / 1e3 / timer_resolution)

def send_timer_counts(timer_counts, ser):
    if (timer_counts > 2**16 - 1):
        raise ValueError('timer_counts must be < 2**16 - 1')
    packed = struct.pack('<I', timer_counts)
    ser.write(packed)

def send_command(bitpat, target_time, ser):
    send_port(bitpat, ser, pad=False)
    timer_counts = get_timer_counts(target_time)
    send_timer_counts(timer_counts, ser)

def read_file(file_name):
    f = open(file_name, 'r')
    lines = f.readlines()
    entries = [[int(m) for m in l.strip().split('\t')] for l in lines]
    return entries

def fix_bitpat(inpat):
    '''
    convert from bitpat convention used in data files
    to convention used in arduino

    datafiles meaning arduino
    0          none       0
    1          center     1 << 5 == 32
    2          left mid   0b10 == 2
    4          left idx   0b00100 == 4
    8          right idx  0b01000 == 8
    12         both       0b01100 == 12
    16         right mid  0b10000 == 16
    2^14-2^15  trig 1 and 2
    '''
    return (0b1 & inpat) << 5 | (inpat & 0b1100000000011110)
    
def run(file_name, ser=None):
    if ser == None:
        ser = start_serial()
    entries = read_file(file_name)

    # wait for reply
    for trial, bitpat, target_time in entries:
        bitpat = fix_bitpat(bitpat)
        sys.stdout.write("|")
        send_command(bitpat, target_time, ser)
        sys.stdout.flush()
        while ser.inWaiting() == 0:
            time.sleep(0.01) # pause for 10 ms
        rcvd = ser.read(2)
        if rcvd == 's5':
            sys.stdout.write("*")
            sys.stdout.flush()

    time.sleep(0.02)
    # clear the last timeout warning
    # this should leave an 's0' waiting for next time
    ser.read(2)
    ser.close()
