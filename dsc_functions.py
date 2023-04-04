# modified by Arne Groh
# for Python 3 and VHF
# Apr 2023
#
#
# forced from
#
# DSC Symbol Generator / CpFSK Modulator
# Wire2waves Ltd
# Nov 2014
# with CW ID for use on Amateur Radio bands

version = "v1.0"

# Imports
import numpy
import pyaudio
import struct
import time
from math import *

# quick and dirty CW Ident
# words per minute
wpm = 20
# dot period
cwdit = 1.2 / wpm
# dash period
cwdah = cwdit * 3

w_amp = (2**15) - 1

# define the output audio stream for the main data
p = pyaudio.PyAudio()
cpfsk_stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, output=1)

# make a second stream for the Tune carrier & cw ident
pt = pyaudio.PyAudio()
tunestream = pt.open(format=pyaudio.paInt16, channels=1, rate=44100, output=1)

pc = pyaudio.PyAudio()
cwstream = pc.open(format=pyaudio.paInt16, channels=1, rate=44100, output=1)

# convert text to DSC symbol value using dictionaries
fmt_symbol_dict = { "area" : "102", "group" : "114", "all ships" : "116",  "sel" : "120", "dis" : "112"}
cat_symbol_dict = { "rtn" : "100", "saf" : "108", "urg" : "110", "dis" : "112", "auto" : "123" }
tc1_symbol_dict = { 
"f3e" : "100", 
"f3edup" : "101", 
"poll" : "103", 
"unable" : "104", 
"end" : "105", 
"data" : "106", 
"j3e" : "109",
"disack" : "110",
"disrel" : "112",
"fec" : "113", 
"arq" : "115", 
"test" : "118", 
"pos" : "121", 
"noinf" : "126"
}
tc2_symbol_dict = {
"no reason" : "100", 
"congestion" : "101", 
"busy" : "102", 
"queue" : "103", 
"barred" : "104", 
"no oper" : "105", 
"temp unav" : "106", 
"disabled" : "107", 
"unable channel" : "108", 
"unable mode" : "109", 
"conflict" : "110", 
"medical" : "111", 
"payphone" : "112", 
"fax" : "113", 
"noinf" : "126"
}
msg1_symbol_dict = {
"fire, explosion" : "100", 
"flooding" : "101", 
"collision" : "102", 
"grounding" : "103", 
"listing, in danger of capsizing" : "104", 
"sinking" : "105", 
"disabled and adrift" : "106", 
"undesignated distress" : "107", 
"abandoning ship" : "108", 
"piracy/armed robbery attack" : "109", 
"person overboard" : "110", 
"emergency position-indicating radiobeacon (EPIRB) emission" : "112"
}
eos_symbol_dict = { "req" : "117", "ack" : "122", "eos" : "127" }


# list containing Phasing Symbols in DX/RX order. 
# elements [12] and [14] aren't used - the real DSC data is interleaved instead, but
# they are included to keep the list referencing simple

phasing_symbol = [ 125, 111, 125, 110, 125, 109, 125, 108, 125, 107, 125, 106, 125, 105, 125, 104 ]

# Instead of doing bit-twiddling to convert each symbol
# value to its 10-bit parity protected word, which involves padding to full 7-bits, counting zeros,
# reversing the bit order, shifting bits and "ORing" in the parity bits
# we just use a dictionary containing the conversion between symbol value and its 10-bit parity protected word
#
parity_table = { 
0 : "0000000111", 1 : "1000000110", 2 : "0100000110", 3 : "1100000101", 
4 : "0010000110", 5 : "1010000101", 6 : "0110000101", 7 : "1110000100",
8 : "0001000110", 9 : "1001000101", 10 : "0101000101", 11 : "1101000100", 
12 : "0011000101", 13 : "1011000100", 14 : "0111000100", 15 : "1111000011", 
16 : "0000100110", 17 : "1000100101", 18 : "0100100101", 19 : "1100100100", 
20 : "0010100101", 21 : "1010100100", 22 : "0110100100", 23 : "1110100011", 
24 : "0001100101", 25 : "1001100100", 26 : "0101100100", 27 : "1101100011", 
28 : "0011100100", 29 : "1011100011", 30 : "0111100011", 31 : "1111100010", 
32 : "0000010110", 33 : "1000010101", 34 : "0100010101", 35 : "1100010100", 
36 : "0010010101", 37 : "1010010100", 38 : "0110010100", 39 : "1110010011", 
40 : "0001010101", 41 : "1001010100", 42 : "0101010100", 43 : "1101010011", 
44 : "0011010100", 45 : "1011010011", 46 : "0111010011", 47 : "1111010010", 
48 : "0000110101", 49 : "1000110100", 50 : "0100110100", 51 : "1100110011", 
52 : "0010110100", 53 : "1010110011", 54 : "0110110011", 55 : "1110110010", 
56 : "0001110100", 57 : "1001110011", 58 : "0101110011", 59 : "1101110010", 
60 : "0011110011", 61 : "1011110010", 62 : "0111110010", 63 : "1111110001", 
64 : "0000001110", 65 : "1000001101", 66 : "0100001101", 67 : "1100001100", 
68 : "0010001101", 69 : "1010001100", 70 : "0110001100", 71 : "1110001011", 
72 : "0001001101", 73 : "1001001100", 74 : "0101001100", 75 : "1101001011", 
76 : "0011001100", 77 : "1011001011", 78 : "0111001011", 79 : "1111001010", 
80 : "0000101101", 81 : "1000101100", 82 : "0100101100", 83 : "1100101011", 
84 : "0010101100", 85 : "1010101011", 86 : "0110101011", 87 : "1110101010", 
88 : "0001101100", 89 : "1001101011", 90 : "0101101011", 91 : "1101101010", 
92 : "0011101011", 93 : "1011101010", 94 : "0111101010", 95 : "1111101001", 
96 : "0000011101", 97 : "1000011100", 98 : "0100011100", 99 : "1100011011", 
100 : "0010011100", 101 : "1010011011", 102 : "0110011011", 103 : "1110011010", 
104 : "0001011100", 105 : "1001011011", 106 : "0101011011", 107 : "1101011010", 
108 : "0011011011", 109 : "1011011010", 110 : "0111011010", 111 : "1111011001", 
112 : "0000111100", 113 : "1000111011", 114 : "0100111011", 115 : "1100111010", 
116 : "0010111011", 117 : "1010111010", 118 : "0110111010", 119 : "1110111001", 
120 : "0001111011", 121 : "1001111010", 122 : "0101111010", 123 : "1101111001", 
124 : "0011111010", 125 : "1011111001", 126 : "0111111001", 127 : "1111111000" 
}

cw_table = {
"A" : ".-",
"B" : "-...",
"C" : "-.-.",
"D" : "-..",
"E" : ".",
"F" : "..-.",
"G" : "--.",
"H" : "....",
"I" : "..",
"J" : ".---",
"K" : "-.-",
"L" : ".-..",
"M" : "--",
"N" : "-.",
"O" : "---",
"P" : ".--.",
"Q" : "--.-",
"R" : ".-.",
"S" : "...",
"T" : "-",
"U" : "..-",
"V" : "...-",
"W" : ".--",
"X" : "-..-",
"Y" : "--.-",
"Z" : "--..",
"1" : ".----",
"2" : "..---",
"3" : "...--",
"4" : "....-",
"5" : ".....",
"6" : "-....",
"7" : "--...",
"8" : "---..",
"9" : "----.",
"0" : "-----",
" " : "",
"/" : "-..-.",
"?" : "..--..",
"+" : ".-.-."
}
#####################

area_table = { "ne" : "0", "nw" : "1", "se" : "2", "sw" : "3" }
#####################
# function definitions
#

##############
# audio generation magic....
#

## update - CPFSK now in use for data
# 

## sine() and tune() are for single tone carrier to assist ATU tuning
# also included in this version are dot & dash tones for CW ID
# setting the "cspace" and "lspace" amplitudes to non-zero
# will produce FSK-style CW, as used in Beacons etc,

def sine(frequency, length, rate):
    length = int(length * rate)
    factor = float(frequency) * (pi * 2) / rate
    return numpy.sin(numpy.arange(length) * factor)#
#
# Generate a carrier to allow Auto-ATU to re-tune when changing frequency
# reduced amplitude, 3 seconds at FSK centre frequency
#
def tune_carrier(pwr):
    frequency = 1700
    length = 3
    rate = 44100
    chunks = []
    chunks.append(sine(frequency, length, rate))
    chunk = numpy.concatenate(chunks) * (w_amp * pwr)
    tunestream.write(chunk.astype(numpy.int16).tostring())

def dash(pwr):
    frequency=1800
    length=cwdah 
    rate=44100
    chunks = []
    chunks.append(sine(frequency, length, rate))
    chunk = numpy.concatenate(chunks) *  (w_amp * pwr)
    cwstream.write(chunk.astype(numpy.int16).tostring())    
    
def dot(pwr):
    frequency=1800
    length=cwdit
    rate=44100
    chunks = []
    chunks.append(sine(frequency, length, rate))
    chunk = numpy.concatenate(chunks) *  (w_amp * pwr)
    cwstream.write(chunk.astype(numpy.int16).tostring())  

def cspace(pwr):
    frequency=1600
    length=cwdit
    rate=44100
    chunks = []
    chunks.append(sine(frequency, length, rate))
    chunk = numpy.concatenate(chunks) *  (w_amp * pwr)
    cwstream.write(chunk.astype(numpy.int16).tostring())     

def lspace(pwr):
    frequency=1600
    length=cwdah
    rate=44100
    chunks = []
    chunks.append(sine(frequency, length, rate))
    chunk = numpy.concatenate(chunks) *  (w_amp * pwr)
    cwstream.write(chunk.astype(numpy.int16).tostring())      
#
#  end of Audio Magic....  
################################

def make_call(cw_table, call):
    callsign = ""
    for i in call:
        callsign += cw_table[i]
        callsign += "s"        
    return callsign
        
def cwid(call, pwr):
    callsign = make_call(cw_table, call)
    for i in callsign:
        if i == "-":
            dash(pwr)
            cspace(pwr)
        elif i == ".":
            dot(pwr)
            cspace(pwr)
        elif i == "s":
            lspace(pwr)
            
###########


# split a 9-digit MMSI into 5 2-digit symbols - add a trailing "0" to the fifth symbol
# resulting MMSI symbols are returned as a list
def mmsi_symbol(mmsi):
    mmsi_list = [int(mmsi[i:i+2]) for i in range(0, len(mmsi), 2)]
    # replace the last symbol with a trailing 0
    mmsi_list[4] = (mmsi_list[4] * 10)
    return mmsi_list
    
def area_symbol(area):
    area_list = [int(area[i:i+2]) for i in range(0, len(area), 2)]
    return area_list
    
def freq_symbol(dfreq):
    freq_list = [int(dfreq[i:i+2]) for i in range(0, len(dfreq), 2)] 
    return freq_list
    
# calculate the ECC by XORing the relevant message symbols
# we must loop through the MMSI and data symbol lists to 
# include each symbol in the overall calculation
def get_ecc(f_s, a_s, c_s, s_s, tc1_s, tc2_s, d_s, e_s):
    
    # if "All Ships", we ignore the a_mmsi word, it won't be transmitted, don't include it in the ECC
    if f_s != 116:
        a_ecc = 0
        for i in a_s:
            a_ecc = int(i) ^ a_ecc
    else:
        a_ecc = 0
        
    s_ecc = 0
    for i in s_s:
        s_ecc = int(i) ^ s_ecc
    
    d_ecc = 0
    for i in d_s:
        d_ecc = int(i) ^ d_ecc
   
    ecc = f_s ^ a_ecc ^ c_s ^ s_ecc ^ tc1_s ^ tc2_s ^ d_ecc ^ e_s
    return ecc

#       fmt_symbol, cat_symbol, s_symbol, tc1_symbol, a_symbol, dis_symbol, pos_symbol, utc_symbol, sub_symbol,eos_symbol
def get_dis_ack_ecc(f_s, c_s, s_s, tc1_s, a_s, d_s, p_s, u_s, su_s, e_s):
    
    # if "All Ships", we ignore the a_mmsi word, it won't be transmitted, don't include it in the ECC
    p_ecc = 0
    for i in p_s:
        p_ecc = int(i) ^ p_ecc

    u_ecc = 0
    for i in u_s:
        u_ecc = int(i) ^ u_ecc


    a_ecc = 0
    for i in a_s:
        a_ecc = int(i) ^ a_ecc
            
    s_ecc = 0
    for i in s_s:
        s_ecc = int(i) ^ s_ecc
    
    ecc = f_s ^ c_s ^ s_ecc ^ tc1_s ^ a_ecc ^ d_s ^ p_ecc ^ u_ecc ^ su_s ^ e_s
    return ecc

#       fmt_symbol, na_symbol, cat_symbol, s_symbol, tc1_symbol, a_symbol, dis_symbol, pos_symbol, utc_symbol, sub_symbol, eos_symbol
def get_dis_relay_ecc(f_s, na_s, c_s, s_s, tc1_s, a_s, d_s, p_s, u_s, su_s, e_s):
    na_ecc = 0
    for i in na_s:
        na_ecc = int(i) ^ na_ecc
    
    p_ecc = 0
    for i in p_s:
        p_ecc = int(i) ^ p_ecc

    u_ecc = 0
    for i in u_s:
        u_ecc = int(i) ^ u_ecc


    a_ecc = 0
    for i in a_s:
        a_ecc = int(i) ^ a_ecc
            
    s_ecc = 0
    for i in s_s:
        s_ecc = int(i) ^ s_ecc
    
    ecc = f_s ^ na_ecc ^ c_s ^ s_ecc ^ tc1_s ^ a_ecc ^ d_s ^ p_ecc ^ u_ecc ^ su_s ^ e_s
    return ecc

# build the basic DSC Call:
# "fmt fmt mmsi cat mmsi tc1 tc2 data eos ecc eos eos"
def make_dsc_call(f_s, a_s, c_s, s_s, tc1_s, tc2_s, d_s, eos_s, ecc_s):

    dsc_call = []
    
    dsc_call.append(f_s)
    dsc_call.append(f_s)
    
    # if "All Ships", we ignore the a_mmsi word.
    if f_s != 116: 
        for i in a_s:
            dsc_call.append(i)
    
    dsc_call.append(c_s)

    for i in s_s:
        dsc_call.append(i)
    
    dsc_call.append(tc1_s)
    dsc_call.append(tc2_s)

    for i in d_s:
        dsc_call.append(i)

    dsc_call.append(eos_s)
    dsc_call.append(ecc_s)
    dsc_call.append(eos_s)
    dsc_call.append(eos_s)
    
    return dsc_call

# build the Dis Ack DSC Call:
# "fmt fmt cat s_mmsi tc1 a_mmsi dis pos utc sub eos ecc eos eos"
def make_dsc_dis_ack_call(f_s, c_s, s_s, tc1_s, a_s, d_s, p_s, u_s, su_s, eos_s, ecc_s):

    dsc_call = []
    
    dsc_call.append(f_s)
    dsc_call.append(f_s)
    
    dsc_call.append(c_s)

    for i in s_s:
        dsc_call.append(i)
    
    dsc_call.append(tc1_s)

    for i in a_s:
        dsc_call.append(i)
    
    dsc_call.append(d_s)

    for i in p_s:
        dsc_call.append(i)

    for i in u_s:
        dsc_call.append(i)

    dsc_call.append(su_s)

    dsc_call.append(eos_s)
    dsc_call.append(ecc_s)
    dsc_call.append(eos_s)
    dsc_call.append(eos_s)
    
    return dsc_call

# build the Dis Relay DSC Call:
# "fmt fmt na cat s_mmsi tc1 a_mmsi dis pos utc sub eos ecc eos eos"
def make_dsc_dis_relay_call(f_s, na_s, c_s, s_s, tc1_s, a_s, d_s, p_s, u_s, su_s, eos_s, ecc_s):

    dsc_call = []
    
    dsc_call.append(f_s)
    dsc_call.append(f_s)

    for i in na_s:
        dsc_call.append(i)

    dsc_call.append(c_s)        

    for i in s_s:
        dsc_call.append(i)
    
    dsc_call.append(tc1_s)

    for i in a_s:
        dsc_call.append(i)
    
    dsc_call.append(d_s)

    for i in p_s:
        dsc_call.append(i)

    for i in u_s:
        dsc_call.append(i)

    dsc_call.append(su_s)

    dsc_call.append(eos_s)
    dsc_call.append(ecc_s)
    dsc_call.append(eos_s)
    dsc_call.append(eos_s)
    
    return dsc_call


# interleave the dsc symbols at the same time convert between symbol value and
# 10-bit parity word by looking in the parity_table dictionary.
# there is probably a way of doing this by looping, but we just
# do it by brute force...

def interleave(parity_table, phasing, dsc_list):
    
    symbol_count = len(dsc_list)
    
    dsc_dxrx = []
    for p in range(0,12):
        dsc_dxrx.append(parity_table[phasing[p]]) #dxrx
    
    dsc_dxrx.append(parity_table[dsc_list[0]])  #dx
    dsc_dxrx.append(parity_table[phasing[13]])  #rx
    dsc_dxrx.append(parity_table[dsc_list[1]])  #dx
    dsc_dxrx.append(parity_table[phasing[15]])  #rx
    dsc_dxrx.append(parity_table[dsc_list[2]])  #dx
    
    for i in range(0,symbol_count-3):
        dsc_dxrx.append(parity_table[dsc_list[i]]) #rx
        dsc_dxrx.append(parity_table[dsc_list[i+3]]) #dx
        
    dsc_dxrx.append(parity_table[dsc_list[-3]]) #rx ecc
   
    return dsc_dxrx

    
# take the interleaved dxrx list (ones and noughts)
# add a 200-bit dotting period of alternating 1/0
# return a string of ones & noughts representing the complete message


def make_bitstream(dsc_dxrx):
    dsc_bitstream= "10"  * 100 # dotting
    for i in dsc_dxrx:
        dsc_bitstream += i
    return dsc_bitstream

   
# take the CPFSK-modulated sample values, pack them into a list, and convert to a string 
# to feed PyAudio  
def modulate(fmsg, fcarrier, f0, f1, fsample, baud, amp):
    
    if amp > 1.0:
       amp = 1.0
       
    dsc_amp =  (w_amp * amp)
    
    mlen = len(fmsg)

    mtime = mlen/baud  

    nsamp = int(round(fsample*mtime))

    deltat = 1.0/fsample

    ph=0
    
    y = [0] * nsamp
    
    for i in range(nsamp): # i = sample number
        thisbit = int(floor((i/float(nsamp))* mlen)) 
        
        # "thisbit" is the index number of the data bit being modulated,
        # the same data-bit is used for "the number of samples which occupy 1 bit period"
        
        if fmsg[thisbit]:
            f = f1 
        else:
            f = f0 
            
        # if this bit is a 1 > f = mark, else f = space
        
        ph +=  2*pi*(fcarrier + f)*deltat 
        
        # phase advances during sample period according the actual mark or space freq
        # when the bit changes between 1 and 0, the phase advance in deltat is small, and
        # continuity in phase is achieved. The signal then starts to advance
        # in phase according to the new frequency.
        
        # reset phase to zero every 360 degrees
        if ph> 2*pi: 
            ph = ph -2*pi
      
        y[i]=dsc_amp*(sin(ph)) # y is an 8-bit value
        # y[i] is the current sample's amplitude - the "sin of current accumulated phase"
    
    wave_list = []
    for v in y:
        w = numpy.int16(v)
        x = w.tostring()
        wave_list.append(x)
    wavestring = b''.join(wave_list)
    
    return wavestring
   
 
    
# do everything needed build the dsc message....
def build_call(fmt_symbol, a_symbol, cat_symbol, s_symbol, tc1_symbol, tc2_symbol, data_symbol, eos_symbol):
    
    # calculate the ECC from the relevant message symbols
    ecc_symbol = get_ecc(fmt_symbol, a_symbol, cat_symbol, s_symbol, tc1_symbol, tc2_symbol, data_symbol, eos_symbol)
    
    # build the basic DSC message   
    dsc_call = make_dsc_call(fmt_symbol, a_symbol, cat_symbol, s_symbol, tc1_symbol, tc2_symbol, data_symbol, eos_symbol, ecc_symbol)
    
    return dsc_call

def build_dis_ack_call(fmt_symbol, cat_symbol, s_symbol, tc1_symbol, a_symbol, dis_symbol, pos_symbol, utc_symbol, sub_symbol, eos_symbol):
    
    # calculate the ECC from the relevant message symbols
    ecc_symbol = get_dis_ack_ecc(fmt_symbol, cat_symbol, s_symbol, tc1_symbol, a_symbol, dis_symbol, pos_symbol, utc_symbol, sub_symbol, eos_symbol)
    
    # build the basic DSC message   
    dsc_call = make_dsc_dis_ack_call(fmt_symbol, cat_symbol, s_symbol, tc1_symbol, a_symbol, dis_symbol, pos_symbol, utc_symbol, sub_symbol, eos_symbol, ecc_symbol)
    
    return dsc_call

def build_dis_relay_call(fmt_symbol, na_symbol, cat_symbol, s_symbol, tc1_symbol, a_symbol, dis_symbol, pos_symbol, utc_symbol, sub_symbol, eos_symbol):
    
    # calculate the ECC from the relevant message symbols
    ecc_symbol = get_dis_relay_ecc(fmt_symbol, na_symbol, cat_symbol, s_symbol, tc1_symbol, a_symbol, dis_symbol, pos_symbol, utc_symbol, sub_symbol, eos_symbol)
    
    # build the basic DSC message   
    dsc_call = make_dsc_dis_relay_call(fmt_symbol, na_symbol, cat_symbol, s_symbol, tc1_symbol, a_symbol, dis_symbol, pos_symbol, utc_symbol, sub_symbol, eos_symbol, ecc_symbol)
    
    return dsc_call


# interleave, make bitstream as a string, convert to list, for the CPFSK modulator function, calculate the samples
# and send them as a string to the soundcard....
def transmit_dsc(dsc_call, pwr):
    
    # interleave the message and phasing DX and RX symbols together, and also convert to 10-bit parity words
    dsc_dxrx = interleave(parity_table, phasing_symbol, dsc_call) 
   
    # create a string with the ones and noughts representing the full message
    dsc_bitstream = make_bitstream(dsc_dxrx)
    
    # convert the string into a list, to feed the CPFSK modulator
    bitstream_list = [int(dsc_bitstream[i:i+1]) for i in range(0, len(dsc_bitstream), 1)]
    
    # get a list of sample values from the CPFSK modulator
    #
    # args = (source of message_bits(a list), f-centre, space_dev, mark_dev, sample_rate, baud_rate, amplitude)
    # returns a string of 8-bit signed values to feed PyAudio
    
    #wave = modulate(bitstream_list, 1700, +85, -85, 44100, 100.0, pwr)
    wave = modulate(bitstream_list, 1700, +400, -400, 44100, 1200.0, pwr)
    
    # make some noise...
    
    cpfsk_stream.write(wave)
    
    return


           
