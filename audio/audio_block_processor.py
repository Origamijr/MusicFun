import pyo
from audio.numpy_buffer import NpBuffer
from audio.numpy_fifo_player import NpFIFOPlayer
from audio.config import SAMPLE_RATE

class AudioBlockProcessor(pyo.PyoObject):
    def __init__(self, input, buf_size=SAMPLE_RATE, overlap=0, mul=1, add=0):
        pyo.PyoObject.__init__(self, mul, add)
        self.input = input
        self.buf_size = buf_size
        self.overlap = overlap

        self.block_generator = NpBuffer(self.input, buf_size=self.buf_size, buffer_count=4, overlap=self.overlap)
        self.block_player = NpFIFOPlayer(buf_size=self.buf_size, overlap=self.overlap, patience=0, buffer_count=4, mul=mul, add=add)
        self.load_block = pyo.TrigFunc(self.block_generator['trig'], self._put_block)

        self._base_objs = self.block_player.getBaseObjects()

    def processBlock(self, buffer):
        """
        Override this function to process a block of audio
        """
        return buffer

    def _put_block(self):
        buffer = self.block_generator.getBuffer()
        if buffer is not None: self.block_player.put(self.processBlock(buffer))

    def play(self, dur=0, delay=0):
        self.block_generator.play(dur=dur, delay=delay)
        self.block_player.play(dur=dur, delay=delay)
        return pyo.PyoObject.play(self, dur, delay)

    def out(self, chnl=0, inc=1, dur=0, delay=0):
        self.block_generator.play(dur=dur, delay=delay)
        self.block_player.play(dur=dur, delay=delay)
        return pyo.PyoObject.out(self, chnl, inc, dur, delay)

    def stop(self, wait=0):
        self.block_generator.stop(wait=wait)
        return pyo.PyoObject.stop(self, wait)