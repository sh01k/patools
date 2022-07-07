import struct
import wave
import sys
import numpy as np

if __name__== '__main__':
    fileIn = ['vocals_drvMIX_diff_0.8_0.2.wav', 'drums_drvMIX_diff_2.0_-0.1.wav', 'bass_drvMIX_diff_1.3_0.7.wav', 'other_drvMIX_diff_0.7_-0.7.wav'] # File name
    fileOut = 'mixture_drvMIX_diff.wav'
    scaleList = [1.0, 3.0, 2.0, 1.2]
    scale = 1.0

    wfIn = []
    channels = []
    format = []
    Fs = []
    nFrames = []

    for f in range(len(fileIn)):
        print("File name: ", fileIn[f])
        wfIn.append( wave.open(fileIn[f],'rb') )
        channels.append ( wfIn[f].getnchannels() )
        format.append( wfIn[f].getsampwidth() )
        Fs.append( wfIn[f].getframerate() )    
        nFrames.append( wfIn[f].getnframes() )

        print("Number of channels: ", channels[f])
        print("Format (bytes): ", format[f])
        print("Sampling frequency (Hz): ", Fs[f])
        print("Number of frames: ", nFrames[f])
        print("==============================")

    wfOut = wave.open(fileOut,'wb')
    wfOut.setparams( (channels[0], format[0], Fs[0], nFrames[0], 'NONE', 'not compressed') )

    ampmax = 0.0
    for i in range(nFrames[0]):
        if i % 10000 == 0:
            print(i, "/", nFrames[0])
        for f in range(len(fileIn)):
            if f == 0:
                buff = wfIn[f].readframes(1)
                indata0 = np.frombuffer(buff, dtype='int16')
                indata =  np.array(indata0, dtype='float') * scaleList[f]
            else:
                buff = wfIn[f].readframes(1)
                indata0 = np.frombuffer(buff, dtype='int16')
                indata = indata + np.array(indata0, dtype='float') * scaleList[f]
        
        #indata = ( indata / float( len(fileIn) ) ).astype('int16').tolist()
        if np.amax(indata * scale) > ampmax:
            ampmax = np.amax(indata * scale)
        indata = ( indata * scale ).astype('int16').tolist()
        outdata = struct.pack("h" * len(indata), *indata)
        wfOut.writeframes(outdata)

    print('Max amplitude: ', ampmax)

    for f in range(len(fileIn)):
        wfIn[f].close()

    wfOut.close()
