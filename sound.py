from miditime.miditime import MIDITime
from midiutil.MidiFile3 import MIDIFile
from covid_data import get_midi_notes
import miditime
import pygame as pg
import pygame.midi
import math

def get_midi_scalars(month_scalars):
    max_contribution_to_total_cases = max(month_scalars)
    midi_scalars = []
    i = 0
    while i < len(month_scalars):
        midi_scalars.append(month_scalars[i]/max_contribution_to_total_cases)
        i = i + 1
    return midi_scalars

def build_midi(filename, month, midi_scalar):
    # Instantiate the class with a tempo (120bpm is the default) and an output file destination.
    mymidi = MIDITime(120, filename)
    def mag_to_pitch_tuned(magnitude):
        # Where does this data point sit in the domain of your data? (I.E. the min magnitude is 3, the max in 5.6). In this case the optional 'True' means the scale is reversed, so the highest value will return the lowest percentage.
        scale_pct = mymidi.linear_scale_pct(0, 1.0, magnitude)

        # Another option: Linear scale, reverse order
        # scale_pct = mymidi.linear_scale_pct(3, 5.7, magnitude, True)

        # Another option: Logarithmic scale, reverse order
        # scale_pct = mymidi.log_scale_pct(3, 5.7, magnitude, True)

        # Pick a range of notes. This allows you to play in a key.
        c_wholeTone = ['C', 'D', 'E', 'Gb', 'Ab', 'B']

        #Find the note that matches your data point
        note = mymidi.scale_to_note(scale_pct, c_wholeTone)

        #Translate that note to a MIDI pitch
        midi_pitch = mymidi.note_to_midi_pitch(note)
        return midi_pitch

    # Create a list of notes. Each note is a list: [time, pitch, velocity, duration]
    midinotes = [
        [0, mag_to_pitch_tuned(midi_scalar), 127, 3],  #At 0 beats (the start), Middle C with velocity 127, for 3 beats
    ]

    # Add a track with those notes
    mymidi.add_track(midinotes)
    # Output the .mid file
    mymidi.save_midi()

def build_midi_test(filename, midi_notes):
    # Instantiate the class with a tempo (120bpm is the default) and an output file destination.
    f = MIDIFile(1)
    f.addTempo(0, 0, 360)
    f.addProgramChange(0,0,0, 83)
    i = 0
    while i < len(midi_notes):
        f.addNote(0, midi_notes[i][2], midi_notes[i][1], midi_notes[i][0], midi_notes[i][4], midi_notes[i][3])
        i = i + 1
    with open("1.midi", 'wb') as outf:
        f.writeFile(outf)


def play_midi(filename):
    try:
        pg.mixer.init()
        pg.mixer.music.load(filename)
    except pg.error:
        return
    pg.mixer.music.play()


#build_midi_test("1.midi", get_midi_notes())
#play_midi("1.midi")
#i = 0
