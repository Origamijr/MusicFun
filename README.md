# MusicFun

Just some audio/midi experiments in python with a pretty wx/OpenGL gui.

On hold atm. Will resume when my research horseshoes back to music

## Dependencies

### Core
* wxPython - Handles windows and basic gui elements
    * https://wxpython.org/pages/downloads/index.html
* pyOpenGL - Graphics library that allows me to freely draw and animate stuff
    * http://pyopengl.sourceforge.net/
* mido - Reads midi files (If I ever get good at file io, I'll replace this since this is all it's doing)
    * https://mido.readthedocs.io/en/latest/
* pyo - Real-time audio and DSP handling
    * http://ajaxsoundstudio.com/pyodoc/index.html
* numpy - you know... numpy (it should already be installed as a sub-package)

### Auxiliary
* pyGLM - Makes matrix handling easier (might replace soon)
    * https://pypi.org/project/PyGLM/
* librosa - Inplements key audio analysis functions. Not used yet, but might be relying on it in the future. Will try to make an optional dependency
    * https://librosa.github.io/librosa/index.html

## Installation

To setup, run 

```bash
pip install -r requirements.txt
```

I was experimenting with pipenv a bit, so there is also a Pipfile for that.

Note that this project was built on Windows, so compatibility with other operating systems might require a bit more steps.

There is a known problem with pyGLM and OSX computers. I will try to migrate away from pyGLM slowly.

## Running

To run, run

```bash
python main.py
```

in the base directory

## Current Functionality

* Able to launch a wxPython window with a bound pyOpnGL canvas
* Scene graph graphics framework for ease of use with visibility culling to improve performance
* Midi file loading, rendering, and playback
* Real-time waveform/spectrogram display from mic

## Next Steps

* Add the ability to annotate the midi file. Expose this annotation to allow for the primitive display of midi analysis
* Add more interfaces for audio (either input from mic/audio file). Possible displays include:
    * One dimensional meters indicating Amplitude, Estimated Pitch, etc
    * Two dimensional realtime DFT/MFCC/etc
    * Three dimensional time-series of DFT/MFCC/etc
* Integrate some analysis algorithms. Ones I have in mind are:
    * Chord detection HMM
    * Self-Similarity matrix
    * Factor Oracle/VMO/Somax(if allowed)
    * Crazy neural net stuff idk how to do yet (primary reason I'm doing this in python)
        * Music/sound classification
        * Generation utilizing rnn/lstm/cnn
        * Latent space exploration using VAE (similar to magenta)
