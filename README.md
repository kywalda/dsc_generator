# dsc_generator
Digital Selective Call VHF Marine

this is a fork of gm4slv dsc gen https://github.com/gm4slv/PythonProjects/tree/master/dsc_gen

This version is compatible with python3 and can generate dsc messages for VHF.
You can put the mic of your VHF transmitter CH70 to the speaker of your computer to send the generated messages to air.
Or you can make a virtual audio line in your computer to send the audio to a sdr or an dsc decoder like ATISrx-v05.py from https://www.qsl.net/pa2ohh/13atisrx.htm.

For this python scripts to run you need some external modules:

pip3 install tk numpy pyaudio
