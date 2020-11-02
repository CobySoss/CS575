from miditime.miditime import MIDITime
import pygame as pg
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
        c_major = ['C', 'D', 'E', 'F', 'G', 'A', 'B']

        #Find the note that matches your data point
        note = mymidi.scale_to_note(scale_pct, c_major)

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



def play_midi(filename):
    try:
        pg.mixer.init()
        pg.mixer.music.load(filename)
    except pg.error:
        return
    pg.mixer.music.play()


