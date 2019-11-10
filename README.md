# MusicFun

Just some audio/midi experiments in python with a pretty wx/OpenGL gui.

To setup, run 

```bash
pip install -r requirements.txt
```

To run, run

```bash
python main.py
```

## Current Functionality

* Able to launch a wxPython window with a bound pyOpnGL canvas
* Scene graph graphics framework for ease of use with visibility culling to improve performance
* Midi file loading, rendering, and playback

## Next Steps

* Add the ability to annotate the midi file. Expose this annotation to allow for the primitive display of midi analysis
* Add an interface for audio (either input from mic/audio file). Possible displays include:
    * One dimensional meters indicating Amplitude, Estimated Pitch, etc
    * Two dimensional realtime DFT/MFCC/etc
    * Three dimensional time-series of DFT/MFCC/etc
* Integrate some analysis algorithms. Ones I have in mind are:
    * Chord detection HMM
    * Factor Oracle/VMO/Somax(if allowed)
    * Crazy neural net stuff idk how to do yet (primary reason I'm doing this in python)
        * Music/sound classification
        * Generation utilizing rnn/lstm/cnn
        * Latent space exploration using VAE (similar to magenta)