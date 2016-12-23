Turris light organ
==================
Simple script to blink with Turris leds to music. There is for now only
implementation using midi, but second implementation using wave and FFT is
planned.

midi
----
Requirements:

* Python3
* Python3-pip
* mido (Can be installed using pip)

```
opkg update
opkg install python3-pip
pip3 install mido
```

Now you should be able to run `tlo-midi.py` script. Input must be midi file. If
your midi file has more than one track, you might want to choose different one
using `-c` option.

Tested with following midi file: https://www.youtube.com/watch?v=6zCzeTUOBKg
