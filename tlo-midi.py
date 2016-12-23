#!/usr/bin/env python3
# This is simple script playing midi track on turris leds
# Currently tested only with turris omnia

import os
import time
import argparse
import mido
import copy
from colour import Color 

# Parse arguments
parser = argparse.ArgumentParser(description='Turris leds midi track player')
parser.add_argument('-c', nargs=1, type=int, help="Choose channel")
parser.add_argument('-d', nargs=1, type=str, help="Color in format #FFFFFF")
parser.add_argument('-v', action='store_true', help="Print verbose messages")
parser.add_argument('-t', action='store_true',
                    help="If it is test run (print output to console)")
parser.add_argument('FILE', nargs=1, type=str, help="Midi audio file")
args = parser.parse_args()

midi_file = args.FILE[0]
channel = 0
if args.c is not None:
    channel = args.c[0]
test_run = False
if args.t is not None:
    test_run = args.t
color = Color('#FF0000')  # In default use red
if args.d is not None:
    color = Color(args.d[0])

# Load midi file
midi = mido.MidiFile(midi_file)

# Initialize data line (we have 12 leds)
data_line = [0]*12
# Found out cut off values (maximal and minimal note in input midi file to use
# all leds to their fullest)
cut_bottom = None
cut_top = None
for msg in midi:
    if (msg.type == "note_on" or msg.type == "note_off") and \
            msg.channel == channel:
        if cut_bottom is None or msg.note < cut_bottom:
            cut_bottom = msg.note
        if cut_top is None or msg.note > cut_top:
            cut_top = msg.note
if cut_bottom is None or cut_top is None:
    raise Exception("Midi file seems to contain no audio data")


def calc_color(intens):
    # intens is 0..127
    multi = intens/127
    clr = Color(color)
    clr.red = clr.red * multi
    clr.green = clr.green * multi
    clr.blue = clr.blue * multi
    return clr.get_hex_l()[1:]

rainbow_led = (
        'pwr',
        'lan0',
        'lan1',
        'lan2',
        'lan3',
        'lan4',
        'wan',
        'pci1',
        'pci2',
        'pci3',
        'usr1',
        'usr2'
        )


def output_line():
    "Function used for pushing data out"
    if test_run:
        line = ""
        for i in range(0, 12):
            # We divide velocity by 13 to ensure resolution of 0-9
            # (velocity is 1..127)
            line = line + str(int(data_line[i]/13))
        print(line)
    else:
        cmd = "rainbow "
        for i in range(0, 12):
            clr = calc_color(data_line[i])
            cmd = cmd + rainbow_led[i] + " " + clr + " "
        os.system(cmd)


def note_to_line(note):
    """ This function calculates which led is for given note
    Note is number from 0..255
    """
    note = note - cut_bottom
    # Threshold between notes
    threshold = (cut_top - cut_bottom) / 12
    # Now divide note by threshold and shift it by 1 down for indexing
    return int(note / threshold - 1)


def note(note, velocity, time_suspend, off=False):
    if off:
        velocity = 0
    time.sleep(time_suspend)  # Suspend for given delay
    data_line[note_to_line(note)] = velocity


# Now do the work
for msg in midi:
    if (msg.type == "note_on" or msg.type == "note_off") and \
            msg.channel == channel:
        note(msg.note, msg.velocity, msg.time, msg.type == "note_off")
    elif args.v:
        print("Ignoring message: " + str(msg))
    output_line()

# Note: We are not handling beats at all. This just waits for given time when it's
# told to do that, but nothing special is done here with timing. This might be
# enough for basic midi files, but problematic for slow and fast beats.
