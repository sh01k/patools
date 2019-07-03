import sys
import time
import pyaudio
import wave
import numpy as np

class paplay:
    def __init__(self,fname,start_channel=1,Fs=0,dev_id=-1):
        self.chunk = 512 #length of chunk for pyaudio
        self.format = pyaudio.paInt16 #format

        self.out_fname = fname # output filename
        self.start_channel = start_channel # number of input channels
        self.Fs = Fs #sampling frequency
        self.dev_id = dev_id #index of audio device

        self.wf_out = wave.open(self.out_fname, 'rb')

        # Sampling frequency
        if self.Fs<=0:
            self.Fs = int(self.wf_out.getframerate())

        # Number of channels
        self.n_out_channel = int(self.wf_out.getnchannels())
        self.nchannel = self.n_out_channel + self.start_channel - 1

        # Number of frames
        self.nframe = self.wf_out.getnframes()

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

        print("- Sampling frequency [Hz]: %d" % self.Fs)
        print("- Number of output channels: %d" % self.n_out_channel)

        # Audio device information
        self.pa = pyaudio.PyAudio() #initialize pyaudio
        if self.dev_id>=0:
            out_dev_info = self.pa.get_device_info_by_index(self.dev_id)
        else: #default audio device
            out_dev_info = self.pa.get_default_output_device_info()

        print("- Device (Output): %s, SampleRate: %dHz, MaxOutputChannels: %d" % (out_dev_info['name'],int(out_dev_info['defaultSampleRate']),int(out_dev_info['maxOutputChannels'])))

        # Check audio device support
        if self.pa.is_format_supported(rate=self.Fs, output_device=out_dev_info['index'], output_channels=self.n_out_channel, output_format=self.format) == False:
            print("Error: audio driver does not support current setting")
            return None

        self.ifrm = 0
        self.pa_indata = []
        self.playbuff = np.zeros((self.nchannel,self.chunk), dtype=self.format_np)

        # Open stream
        if self.dev_id<0:
            self.stream = self.pa.open(format=self.format,
                                       channels=self.nchannel,
                                       rate=self.Fs,
                                       input=False,
                                       output=True,
                                       frames_per_buffer=self.chunk,
                                       stream_callback=self.callback)
        else:
            self.stream = self.pa.open(format=self.format,
                                       channels=self.nchannel,
                                       rate=self.Fs,
                                       input=False,
                                       output=True,
                                       input_device_index=self.dev_id,
                                       output_device_index=self.dev_id,
                                       frames_per_buffer=self.chunk,
                                       stream_callback=self.callback)

    def usage(self):
        print("[Usage]")
        print("  > paplay(fname,start_channel,Fs,dev_id)")
        print("  - fname: play filename\n - start_channel: start output channel\n Fs: sampling frequency\n - dev_id: index of audio device")
        return 0

    def start(self):
        self.ifrm = 0
        self.stream.start_stream()
        while self.ifrm<int(np.ceil(self.nframe/self.chunk)):
            pass
        self.stream.stop_stream()

        self.wf_out.close()

        return 0

    def terminate(self):
        self.stream.close()
        self.pa.terminate()

    def callback(self, in_data, frame_count, time_info, status):
        self.playbuff[self.start_channel-1:self.nchannel,:] = np.frombuffer(self.wf_out.readframes(self.chunk), dtype=self.format_np)
        pa_outdata = (self.playbuff.T).reshape((self.chunk*self.nchannel,1))
        self.ifrm = self.ifrm+1
        return (pa_outdata, pyaudio.paContinue)

if __name__== '__main__':
    pap = paplay("tsp_out.wav",2)
    pap.start()
    pap.terminate()
