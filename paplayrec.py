import sys
import time
import pyaudio
import wave
import numpy as np

class paplayrec:
    def __init__(self,play_fname,rec_fname,nchannel=1,Fs=0,duration=0,dev_id=-1):
        self.chunk = 512 #length of chunk for pyaudio
        self.format = pyaudio.paInt16 #format

        self.out_fname = play_fname # output filename
        self.in_fname = rec_fname # input filename
        self.nchannel = nchannel # number of input channels
        self.Fs = Fs #sampling frequency
        self.duration = duration # duration
        self.dev_id = dev_id #index of audio device

        self.wf_out = wave.open(self.out_fname, 'rb')
        self.wf_in = wave.open(self.in_fname, 'wb')

        # Sampling frequency
        if self.Fs<=0:
            self.Fs = int(self.wf_out.getframerate())

        # Number of channels
        self.n_out_channel = int(self.wf_out.getnchannels())
        if self.nchannel<self.n_out_channel:
            print("Invalid of number of channel")
            self.usage()
            return

        if self.duration<=0:
            self.nframe = int(self.wf_out.getnframes())
            self.nframe_out = self.nframe
            self.duration = self.nframe/self.Fs
        else:
            self.nframe = int(self.duration*self.Fs)
            self.nframe_out = int(self.wf_out.getnframes())

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
        print("- Number of channels: %d" % self.nchannel)
        print("- Duration [s]: %f" % self.duration)

        # Audio device information
        self.pa = pyaudio.PyAudio() #initialize pyaudio
        if self.dev_id>=0:
            in_dev_info = self.pa.get_device_info_by_index(self.dev_id)
            out_dev_info = in_dev_info
        else: #default audio device
            in_dev_info = self.pa.get_default_input_device_info()
            out_dev_info = self.pa.get_default_output_device_info()

        print("- Device (Input): %s, SampleRate: %dHz, MaxInputChannels: %d" % (in_dev_info['name'],int(in_dev_info['defaultSampleRate']),int(in_dev_info['maxInputChannels'])))
        print("- Device (Output): %s, SampleRate: %dHz, MaxOutputChannels: %d" % (out_dev_info['name'],int(out_dev_info['defaultSampleRate']),int(out_dev_info['maxOutputChannels'])))

        # Check audio device support
        if self.pa.is_format_supported(self.Fs, in_dev_info['index'], self.nchannel, self.format, out_dev_info['index'], self.nchannel, self.format) == False:
            print("Error: audio driver does not support current setting")
            return None

        self.ifrm = 0
        self.pa_indata = []

        # Open stream
        if self.dev_id<0:
            self.stream = self.pa.open(format=self.format,
                                       channels=self.nchannel,
                                       rate=self.Fs,
                                       input=True,
                                       output=True,
                                       frames_per_buffer=self.chunk,
                                       stream_callback=self.callback)
        else:
            self.stream = self.pa.open(format=self.format,
                                       channels=self.nchannel,
                                       rate=self.Fs,
                                       input=True,
                                       output=True,
                                       input_device_index=self.dev_id,
                                       output_device_index=self.dev_id,
                                       frames_per_buffer=self.chunk,
                                       stream_callback=self.callback)

    def usage(self):
        print("[Usage]")
        print("  > playrec(play_fname,rec_fname,nchannel,Fs,duration,dev_id)")
        print("  - play_fname: play filename\n - rec_fname: rec filename\n - nchannel: number of channels\n Fs: sampling frequency\n duration: duration of playrec\n - dev_id: index of audio device")
        return 0

    def start(self,out_start_channel=1):
        out_start_channel = out_start_channel-1
        out_end_channel = out_start_channel + self.n_out_channel
        if out_start_channel + self.n_out_channel > self.nchannel:
            print("Invalid of start output channel")
            self.usage()
            return

        playbuff = np.zeros((self.nchannel,self.nframe), dtype=self.format_np)
        playbuff[out_start_channel:out_end_channel,0:self.nframe_out] = np.frombuffer(self.wf_out.readframes(self.nframe_out), dtype=self.format_np)
        self.playdata = (playbuff.T).reshape((self.nframe*self.nchannel,1))

        self.pa_indata = []

        self.ifrm = 0
        self.stream.start_stream()
        while self.ifrm<int(np.ceil(self.nframe/self.chunk)):
            pass
        self.stream.stop_stream()

        self.wf_in.setparams((self.nchannel, self.pa.get_sample_size(self.format), self.Fs, self.nframe, 'NONE', 'not compressed'))
        self.wf_in.writeframesraw(b''.join(self.pa_indata))
        self.wf_in.close()
        self.wf_out.close()

        return 0

    def terminate(self):
        self.stream.close()
        self.pa.terminate()

    def callback(self, in_data, frame_count, time_info, status):
        self.pa_indata.append(in_data)
        pa_outdata = self.playdata[self.ifrm*self.nchannel*self.chunk:(self.ifrm+1)*self.nchannel*self.chunk]
        self.ifrm = self.ifrm+1
        return (pa_outdata, pyaudio.paContinue)

if __name__== '__main__':
    papr = paplayrec("tsp_out.wav","rec.wav",nchannel=2,duration=4)
    papr.start(2)
    papr.terminate()
