# Python and OpenGL demos

These are a few programs experimenting with OpenGL and python.  Pygame is also used.


Using python 3.10

Installed libraries with mamba (conda): `mamba install -c anaconda pyopengl pygame scipy numpy`

The python OpenGL demos use the w-a-s-d keys (& q+e for up/down) and mouse for looking.

I wanted to load some 3d models into OpenGL but my 14 year old computer is too slow to render them or OpenGL isn't the right engine for it anyways.  OpenGL comes with the 5 platonic solids and a teacup.

## gl-fft.py

gl-fft.py uses scipy's fast fourier transform (fft) library to transform the wave domain to the frequency domain.  It takes a wave file, does the fft on it and puts it into a list.

To convert a mp3 file to a wav file use: `ffmpeg -i sample.mp3 sample.wav`

I'm only using the left-channel for now and ignoring the right channel.  Usually they are the same unless you want a cool stereo effect going from side to side.

More info on scipy & fft:
https://realpython.com/python-scipy-fft/


## Microbes

I wanted to create a simple 3-d asteroids type game.  I threw in espeak (linux util for text-to-speech) but disabled that in case you did not install it.  Its still a work in progress.  I want to add a UFO or 2 that fires at the player and mines or another hazzard.

Use the mouse button to shoot.  

I thought about changing the movement scheme to be more like the original Asteroids. In the old Asteroids, hitting thrust would add velocity to your ship and you would need to turn around and fire thrust to stop moving.  

Microbes was a TRS-80 Color Computer game from the 1980's that was very similar to the orignal Asteroids.  

Microbes is still a work in progress.

## Zone

Playing with connected OpenGL objects (sphere, cone) to point in the right direction when moving and make a tail wiggle.

Learned about arctan2 which is cooler than arctan.

## Solar System

Model of our solar system with things roughly proportonal to each other.  Planets are scaled to each other.  Planet orbits scaled to each other, planet movement scaled to each other.  But the entire scale is off - and there is no sun because it would hide everything else.

I didn't include Pluto because its not a planet.  (Ask Jerry and Morty)
