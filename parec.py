import sys
import time
import pyaudio
import wave
import numpy as np
import scipy.io as sio
import matplotlib.pyplot as plt

class rec:
    def __init__(self,nchannel=1,Fs=44100):
        self.chunk = 512 #length of chunk for pyaudio
        self.format = pyaudio.paInt16 #format
        self.Fs = Fs #sampling frequency
        self.nchannel = nchannel #number of input channels

        # Format
        if self.format == pyaudio.paInt16:
            self.format_np = np.int16
        elif self.format == pyaudio.paInt32:
            self.format_np = np.int32
        elif self.format == pyaudio.paInt8:
            self.format_np = np.int8
        elif self.format == pyaudio.paUInt8:
            self.format_np = np.uint8
        elif self.format == pyaudio.paFloat32:
            self.format_np = np.float32
        else:
            print("Invalid format")
            self.usage()
            return

    def start(self, filename, duration):
        self.wf = wave.open(filename, 'wb')
        self.pa = pyaudio.PyAudio()
        self.stream = self.pa.open(format=self.format,
                              channels=self.nchannel,
                              rate=self.Fs,
                              input=True,
                              frames_per_buffer=self.chunk,
                              stream_callback=self.callback)

        self.pa_indata = []
        self.stream.start_stream()
        print("Recording...\n")
        time.sleep(duration)

        self.stream.stop_stream()
        self.stream.close()
        self.pa.terminate()

        self.wf.setparams((self.nchannel, self.pa.get_sample_size(self.format), self.Fs, int(duration*self.Fs), 'NONE', 'not compressed'))
        self.wf.writeframesraw(b''.join(self.pa_indata))
        self.wf.close()

        return 0

    def callback(self, in_data, frame_count, time_info, status):
        self.pa_indata.append(in_data)
        return(None, pyaudio.paContinue)

if __name__== '__main__':
    rec = rec(2)
    rec.start("rec_test.wav",10)
