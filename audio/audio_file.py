import pyo
import numpy as np
import librosa
from audio.config import SAMPLE_RATE

class AudioFile(pyo.PyoObject):
    def __init__(self, path):
        self.data, _ = librosa.load(path, sr=SAMPLE_RATE)
        self.table = pyo.DataTable(self.data.shape[0])
        self.player = pyo.TableRead(self.table, freq=self.table.getRate())
        self.table.replace(list(self.data))

    def segment_data(self, buf_size=SAMPLE_RATE, overlap=0):
        assert overlap < buf_size / 2
        arr = np.asfarray(self.table.getTable())
        indices_wav = np.arange(buf_size-overlap, arr.shape[0], buf_size-overlap)
        arr = np.split(arr, indices_or_sections=indices_wav, axis=0)
        if arr[-1].shape[0] > overlap:
            arr[-1] = np.resize(arr[-1], buf_size-overlap)
            arr.append(np.zeros(buf_size-overlap))
        else:
            arr[-1] = np.resize(arr[-1], buf_size-overlap)
        arr = np.stack(arr, axis=0)
        arr_s = np.zeros(arr.shape)
        arr_s[:-1] = arr[1:]
        arr = np.concatenate((arr, arr_s), axis=1)
        return arr[:-1,:(buf_size)]

if __name__ == "__main__":
    s = pyo.Server(sr=SAMPLE_RATE, nchnls=2).boot().start()
    af = AudioFile("C:/Users/origa/Desktop/python_stuff/MusicFun/audio/samples/Hype.wav")
    data = af.segment_data(buf_size=100, overlap=10)