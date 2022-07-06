import struct
import wave
import numpy as np

if __name__== '__main__':
    fileIn = ['vocals_drvMIX_0.8_0.2.wav', 'drums_drvMIX_2.0_0.5.wav'] # File name
    fileOut = 'out.wav'

    wfIn = []
    channels = []
    format = []
    Fs = []
    nFrames = []

    for f in range(len(fileIn)):
        print(fileIn[f])
        wfIn.append( wave.open(fileIn[f],'rb') )
        channels.append ( wfIn[f].getnchannels() )
        format.append( wfIn[f].getsampwidth() )
        Fs.append( wfIn[f].getframerate() )    
        nFrames.append( wfIn[f].getnframes() )

        print("Number of channels: ", channels[f])
        print("Format (bytes): ", format[f])
        print("Sampling frequency (Hz): ", Fs[f])
        print("Number of frames: ", nFrames[f])

    wfOut = wave.open(fileOut,'wb')
    wfOut.setparams( (channels[0], format[0], Fs[0], nFrames[0], 'NONE', 'not compressed') )

    for i in range(nFrames[0]):
        if i % 10000 == 0:
            print(i, "/", nFrames[0])
        for f in range(len(fileIn)):
            if f == 0:
                buff = wfIn[f].readframes(1)
                indata0 = np.frombuffer(buff, dtype='int16')
                indata =  np.array(indata0, dtype='float')
            else:
                buff = wfIn[f].readframes(1)
                indata0 = np.frombuffer(buff, dtype='int16')
                indata = indata + np.array(indata0, dtype='float')
        
        indata = ( indata / float( len(fileIn) ) ).astype('int16').tolist()
        outdata = struct.pack("h" * len(indata), *indata)
        wfOut.writeframes(outdata)

    for f in range(len(fileIn)):
        wfIn[f].close()

    wfOut.close()
