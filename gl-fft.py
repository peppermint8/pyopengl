#!/usr/bin/env python
#! -*- coding: utf-8 -*-
"""

frequency of a wav file in opengl
- do  need to remove freq 58-62 (electric hum)

"""
import sys
import pygame
import random
from pygame.locals import *
import math
import wave
import numpy as np
import scipy
import time

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


def get_clr():
    
    clr = [random.random(),random.random(),random.random(), 1.0]
    return clr



class Thing(object):
    buffer = ""

    shape = "cube"
    clr = [1, 1, 1] # 0 .. 1

    # x, y, z
    p = [0, 0, 0]
    v = [0, 0, 0]
    min_pt = [0, 0, 0]
    max_pt = [10, 10, 10]

    def __init__(self, p, v):
        self.p = p
        self.v = v

    def set_min_max(self, min_pt, max_pt):
        self.min_pt = min_pt
        self.max_pt = max_pt
        self.ctr = [
            (self.max_pt[0] - self.min_pt[0]) // 2, 
            (self.max_pt[1] - self.min_pt[1]) // 2, 
            (self.max_pt[2] - self.min_pt[2]) // 2
        ]


    

class PlayerObject():

    p = 0.4
    xx = 0.0
    yy = 0.0
    zz = 0.0
    aa = 0.0
    stage_min = [0, 0, 0]
    stage_max = [10, 10, 10]
    def __init__(self,x, y, z, a, stage_min, stage_max):
        self.xx = x
        self.yy = y
        self.zz = z
        self.aa = a
        self.stage_min = stage_min
        self.stage_max = stage_max

    def go(self, vv, a0=0):
        go_flag = True
        
        new_x = self.xx + vv * math.sin(math.radians(self.aa + a0))
        new_y = self.yy + vv * math.cos(math.radians(self.aa + a0))

        #print(new_x, new_y)

        if new_x > self.stage_max[0] - self.p:
            go_flag = False
        if new_y > self.stage_max[1] -  self.p:
            go_flag = False
        if new_x < self.stage_min[0] + self.p:
            go_flag = False
        if new_y < self.stage_min[1] + self.p:
            go_flag = False
        

        if go_flag:
            self.xx = new_x
            self.yy = new_y
        
        return go_flag

    def up(self, vv):
        go_flag = True
        new_z = self.zz + vv
        if new_z > self.stage_max[2] - self.p:
            go_flag = False
        if new_z < self.stage_min[2] + self.p:
            go_flag = False

        if go_flag:
            self.zz = new_z
        return go_flag




def draw_borders(stage_min, stage_max):

    glPushMatrix()
    glBegin(GL_LINES) 
    
    # floor
    x0 = stage_min[0]
    x1 = stage_max[0]
    y0 = stage_min[1]
    y1 = stage_max[1]
    z0 = stage_min[2]
    z1 = stage_max[2]
    s = 5

    # floor & ceiling
    glColor3f(0.25, 0.25, 0.25)	
    #for z in [z0, z1]:
    for z in [z0]:

        for x in range(x0, x1+1,s):
            glVertex3f(x, y0, z)
            glVertex3f(x, y1, z)

        for y in range(y0, y1+1, s):
            glVertex3f(x0, y, z)
            glVertex3f(x1, y, z)
    

    glEnd()
    glPopMatrix()



def init_screen():
    pygame.init()
    display = (1800, 1000) # 1920 x 1080
    #screen = pygame.display.set_mode((max_x, max_y))
    screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.mouse.set_visible(False)

    return display

def main(display, wav_file):

    glClearColor(0.0, 0.0, 0.0, 0.0) 
    #glClearColor(1.0, 1.0, 1.0, 0.0) #16161d eigengrau

    glutInit([])

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA) 

    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.5, 0.5, 0.5, 1])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1])


    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, (display[0]/display[1]), 0.1, 550.0)

    glMatrixMode(GL_MODELVIEW)


    start = [1, 1, 2]
    start2 = [1, 7, 2]
    gluLookAt(start[0], start[1], start[2], start2[0], start2[1], start2[2], 0, 0, 1)
    # look at has to be same angle to track  walking

    wav_obj = wave.open(wav_file, 'rb')

    freq = wav_obj.getframerate()
    n_samples = wav_obj.getnframes()    
    #print("freq = {}".format(freq))
    # freq = samples per sec

    #print("n_samples = {}".format(n_samples))
    #print("n_channels = {}".format(wav_obj.getnchannels()))
    ttime = n_samples / freq
    print("{} time: {:.2f} sec".format(wav_file, ttime))

    #sig_window = 0.05 # seconds
    sig_window = 0.1 # seconds
    f_size = int(sig_window * freq)

    signal_wave = wav_obj.readframes(n_samples)
    signal_array = np.frombuffer(signal_wave, dtype=np.int16)
    l_channel = signal_array[0::2]
    #r_channel = signal_array[1::2]


    

    viewMatrix = glGetFloatv(GL_MODELVIEW_MATRIX)
    glLoadIdentity()

    # init mouse movement and center mouse on screen
    m = [display[0] // 2, display[1] // 2]
    mm = [0, 0]
    pygame.mouse.set_pos(m)

    # stage size
    stage_min = (0, 0, 0)
    stage_max = (90, 80, 80)
    

    # create objects
    # set instance variable vs static variable
    o_list = []
    pz = 0
    mx = 25 # x margin
    sx = 3 # space between
    my = 5 # y margin
    sy = 3

    # olist[0][] = row 0
    y_range = 60 # 40
    x_range = 30 # 20

    for x in range(0, y_range):
        tmp_list = []
        for y in range(0, x_range):
            
            px = mx + x * sx
            py = my + y * sy
            p = [px, py, pz]
            v = [0, 0, 0]
    
            o = Thing(p, v)
    
            o.set_min_max(stage_min, stage_max)
            o.clr = (0.41, 0.2, 0.9, 1.0)
            #o.clr = (0.9, 0.2, 0.4, 1.0)
            o.shape = "sphere"
            #o.shape = "cube"
            o.id = f"{x}-{y}"
            o.xx = px
            o.yy = py
            o.zz = pz
            
            tmp_list.append(o)
            #o_list.append(o)
        o_list.append(tmp_list)


    #for o in o_list:
    #    for oo in o:
    #        print(oo.id)
    #    print()
    #sys.exit(44)

    #print(len(o_list))
    # track bubba - camera pos
    bubba = PlayerObject(start[0], start[1], start[2], 0, stage_min, stage_max)

    vv = 0.25 # movement velocity for player
    up_down_angle = 0.0

    # begin playback
    pygame.mixer.init()
    pygame.mixer.music.load(wav_file)
    pygame.mixer.music.play(0, 0.0)
    pygame.mixer.music.set_volume(1.0)    
    #pygame.mixer.music.set_volume(0.0)    

    a = 0
    b = a + f_size
    max_yf = 0
    scalefft = 5_000_000
    paused = False
    done = False
    go_flag = True

    i_bins = x_range
    i_range = 250 #100 #500

    time0 = time.time()

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                    done = True
                if event.key == pygame.K_PAUSE or event.key == pygame.K_p:
                    paused = not paused
                    pygame.mouse.set_pos(m) 

            if not paused: 
                if event.type == pygame.MOUSEMOTION:
                    mm = [event.pos[0] - m[0], event.pos[1] - m[1]]
                pygame.mouse.set_pos(m)    


        time1 = time.time()


        if not paused:
            # get keys
            keypress = pygame.key.get_pressed()

        
            # init model view matrix
            glLoadIdentity()

            # apply the look up and down
            up_down_angle += mm[1]*vv
            glRotatef(up_down_angle, 1.0, 0.0, 0.0)

            # init the view matrix
            glPushMatrix()
            glLoadIdentity()

            if keypress[pygame.K_w]:
                if bubba.go(vv):
                    glTranslatef(0, 0, vv)
                
            if keypress[pygame.K_s]:
                if bubba.go(-vv):
                    glTranslatef(0, 0, -vv)    

            if keypress[pygame.K_d]:
                if bubba.go(vv, 90):
                    glTranslatef(-vv, 0, 0)   

            if keypress[pygame.K_a]:
                if bubba.go(-vv, 90):
                    glTranslatef(vv, 0, 0)

            if keypress[pygame.K_q]:
                if bubba.up(-vv):
                    glTranslatef(0, vv, 0)

            if keypress[pygame.K_e]:
                if bubba.up(vv):
                    glTranslatef(0, -vv, 0)

            if keypress[pygame.K_c]:
                glRotatef(5*vv, 0.0, 1.0, 0.0)
                bubba.aa += 5 * vv

            if keypress[pygame.K_z]:
                glRotatef(-5*vv, 0.0, 1.0, 0.0)
                bubba.aa -= 5 * vv


            # apply the left and right rotation
            glRotatef(mm[0]*vv, 0.0, 1.0, 0.0)
            if mm[0] != 0:

                bubba.aa += mm[0] * vv
                if bubba.aa > 360.0:
                    bubba.aa = bubba.aa - 360.0
                if bubba.aa < 0.0:
                    bubba.aa = bubba.aa + 360.0

            # multiply the current matrix by the get the new view matrix and store the final vie matrix 
            glMultMatrixf(viewMatrix)
            viewMatrix = glGetFloatv(GL_MODELVIEW_MATRIX)

            # apply view matrix
            glPopMatrix()
            glMultMatrixf(viewMatrix)


            glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

            if time1 - time0 > sig_window:
                t = time1 - time0
                a = int(t * freq)
                b = a + f_size
                #print(f"time: {t:.1f} sec, b: {b/freq:.1f}, {a} - {b}")
                if b > n_samples:
                    b = n_samples

            # last row = this row
            for y in range(y_range-1,0,-1):
                cnt = 0
                for oo in o_list[y]:
                    
                    oo.zz = o_list[y-1][cnt].zz
                    oo.xx0 = o_list[y-1][cnt].xx
                    oo.yy0 = o_list[y-1][cnt].yy
                    oo.zz0 = o_list[y-1][cnt].zz
                    cnt += 1



            # fft for left channel
            if b < len(l_channel):
                yf = scipy.fft.rfft(l_channel[a:b])
                yf = np.abs(yf) # r+i to real number
                #yf = yf / max_yf
                # get rid of pesky nan in np.array
                yf[np.isnan(yf)] = 0.0

                # set z position for objects


                i_step = i_range // i_bins
                obin = [] # np.array
                i_cnt = 0
                for i in range(i_bins):

                    iy = np.sum(yf[i_cnt:i_cnt+i_step])/scalefft
                    i_cnt += i_step
                    obin.append(iy)

                    o_list[0][i].zz = iy
            
            # get new zz
            for y in range(y_range-1,0,-1):
                cnt = 0
                for oo in o_list[y]:
                    
                    #oo.zz = o_list[y-1][cnt].zz
                    #oo.xx0 = o_list[y-1][cnt].xx
                    #oo.yy0 = o_list[y-1][cnt].yy
                    oo.zz0 = o_list[y-1][cnt].zz
                    cnt += 1
            

            #draw_borders(stage_min, stage_max)

    
            # draw objects
            for oo in o_list:
                xx0 = yy0 = zz0 = 0
                for o in oo:
                    glPushMatrix()

                    glColor4f(o.clr[0], o.clr[1], o.clr[2], o.clr[3])

                    if o.shape == "sphere":
                        glTranslatef(o.xx, o.yy, o.zz)
                        glutSolidSphere(0.2, 16, 16)
                    if o.shape == "cube":
                        glTranslatef(o.xx, o.yy, o.zz)
                        #glutSolidSphere(0.2, 16, 16)                        
                        glutSolidCube(0.2)

                    glPopMatrix()

                    if xx0 > 0:
                        glPushMatrix()
                        glBegin(GL_LINES) 
                        glVertex3f(o.xx, o.yy, o.zz)
                        glVertex3f(xx0, yy0, zz0)
                        glEnd()
                        glPopMatrix()
                    
                    xx0 = o.xx
                    yy0 = o.yy
                    zz0 = o.zz

                    if hasattr(o, "zz0"):
                        glPushMatrix()
                        glBegin(GL_LINES) 
                        glVertex3f(o.xx, o.yy, o.zz)
                        glVertex3f(o.xx0, o.yy0, o.zz0)
                        glEnd()
                        glPopMatrix()



            draw_text(10, 10, " A: {:.2f}, X: {:.2f}, Y: {:.2f}, Z: {:.2f} t: {:.2f}".format(bubba.aa, bubba.xx, bubba.yy, bubba.zz, time1-time0))

            pygame.display.flip()
            pygame.time.wait(10)

    pygame.quit()


def draw_text(x, y, text):                                                
    text_surface = font.render(text, True, (0, 255, 255, 255), (0, 0, 0, 0))
    text_data = pygame.image.tostring(text_surface, "RGBA", True)
    glWindowPos2d(x, y)
    glDrawPixels(text_surface.get_width(), text_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)


if __name__ == '__main__':

    wav_file = sys.argv[1]

    screen = init_screen()
    font = pygame.font.SysFont('arial', 32)
    main(screen, wav_file)

    sys.exit(0)
