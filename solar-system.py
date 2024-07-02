#!/usr/bin/env python
#! -*- coding: utf-8 -*-
"""
Solar system
- size relative to each other
- distance from sun correct
- orbit speed relative to each other

Use glut for rendering standard objects - use glscale to shrink and grow

x = left-right, y = forward-back, z = up-down


"""
import sys
import pygame
import random
from pygame.locals import *
import math
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import functools

images = [None, None] 

def get_clr():
    
    clr = [random.random(),random.random(),random.random(), 1.0]
    return clr


@functools.cache
def rotate(r, size, cxy):
    #r0 = r - CZ
    
    x = math.cos(r) * size - math.sin(r) * size + cxy[0]
    y = math.sin(r) * size + math.cos(r) * size + cxy[1]

    #x = int(x)
    #y = int(y)
    return (x,y)

class Thing(object):

    shape = "cube"
    pad = 0.4 # padding
    rv = 0.0 # rotate velocity
    rr = 0.0 # initial radians
    radius = 1.0
    trail_flag = False
    trail_list = []
    clr = [1, 1, 1] # 0 .. 1

    # x, y, z
    p = [0, 0, 0]
    v = [0, 0, 0]

    min_pt = [0, 0, 0]
    max_pt = [10, 10, 10]

    rv = 0.0 # rotate velocity
    angle = 0.0
    rm = [0, 0, 0] # x, y, z rotation ratios


    wire_flag = False

    def __init__(self, p, v):
        self.p = p
        self.v = v
        #self.clr = get_clr()

    def set_min_max(self, min_pt, max_pt):
        self.min_pt = min_pt
        self.max_pt = max_pt

    def move(self):

        self.p[0] = self.p[0] + self.v[0]
        self.p[1] = self.p[1] + self.v[1]
        self.p[2] = self.p[2] + self.v[2]

        if self.p[0] > self.max_pt[0] - self.pad or self.p[0] < self.min_pt[0] + self.pad:
            self.v[0] = self.v[0] * -1

        if self.p[1] > self.max_pt[1] - self.pad or self.p[1] < self.min_pt[1] + self.pad:
            self.v[1] = self.v[1] * -1
        
        if self.p[2] > self.max_pt[2] - self.pad or self.p[2] < self.min_pt[2] + self.pad:
            self.v[2] = self.v[2] * -1

    def rotate_thing(self):
        if self.rv > 0:
            self.rr = self.rr + self.rv
            # assume x-y rotation
            (x0, y0) = rotate(self.rr, self.radius, (self.ctr[0], self.ctr[1]))

            #x0 = self.p[0]
            #y0 = self.p[1]
            #z0 = self.p[2]
            if self.trail_flag:
                self.trail_list.append((x0, y0))
                if len(self.trail_list) > 500:
                    self.trail_list = self.trail_list[1:]
            self.p[0] = x0
            self.p[1] = y0

            #self.p[0] = self.p[0] + self.rv



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





def get_xyz(min_px, max_px):

    x = random.random() * (max_px[0] - min_px[0]) + min_px[0]    
    y = random.random() * (max_px[1] - min_px[1]) + min_px[1]    
    z = random.random() * (max_px[2] - min_px[2]) + min_px[2]    
    return x,y,z



def draw_borders(stage_min, stage_max):
    
    glColor3f(1.0, 1.0, 1.0)	
    glBegin(GL_LINES) 

    glVertex3f(stage_min[0], 0.0, stage_max[2])
    glVertex3f(stage_max[0], 0.0, stage_max[2]) 
    glVertex3f(0, stage_min[1], stage_max[2])
    glVertex3f(0, stage_max[1], stage_max[2])

    glVertex3f(stage_max[0], stage_min[1], stage_max[2])
    glVertex3f(stage_max[0], stage_max[1], stage_max[2])

    glVertex3f(stage_min[0], stage_max[1], stage_max[2])
    glVertex3f(stage_max[0], stage_max[1], stage_max[2])

    # vertical corners
    glVertex3f(stage_min[0], stage_min[1], stage_min[2])
    glVertex3f(stage_min[0], stage_min[1], stage_max[2])

    glVertex3f(stage_max[0], stage_min[1], stage_min[2])
    glVertex3f(stage_max[0], stage_min[1], stage_max[2])


    glVertex3f(stage_min[0], stage_max[1], stage_min[2])
    glVertex3f(stage_min[0], stage_max[1], stage_max[2])

    glVertex3f(stage_max[0], stage_max[1], stage_min[2])
    glVertex3f(stage_max[0], stage_max[1], stage_max[2])

    #glVertex3f(stage_min[0], stage_min[1], stage_min[2])
    #glVertex3f(stage_max[0], stage_min[1], stage_min[2])
    #glVertex3f(stage_max[0], stage_max[1], stage_min[2])
    #glVertex3f(stage_min[0], stage_max[1], stage_min[2])

    glEnd()


def draw_floor(stage_min, stage_max):            
    # floor
    glColor4f(0.15, 0.15, 0.15, 1.0)
    glBegin(GL_QUADS)
    glVertex3f(stage_min[0], stage_min[1], stage_min[2])
    glVertex3f(stage_max[0], stage_min[1], stage_min[2])
    glVertex3f(stage_max[0], stage_max[1], stage_min[2])
    glVertex3f(stage_min[0], stage_max[1], stage_min[2])
    glEnd()

def draw_ceiling(stage_min, stage_max):
    glColor4f(0.25, 0.25, 0.75, 1.0)
    glBegin(GL_QUADS)
    glVertex3f(stage_min[0], stage_min[1], stage_max[2])
    glVertex3f(stage_max[0], stage_min[1], stage_max[2])
    glVertex3f(stage_max[0], stage_max[1], stage_max[2])
    glVertex3f(stage_min[0], stage_max[1], stage_max[2])
    glEnd()

def init_screen():
    pygame.init()
    display = (1000, 800)
    #screen = pygame.display.set_mode((max_x, max_y))
    screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.mouse.set_visible(False)

    return display

def main(display):

    glClearColor(0.0, 0.0, 0.0, 0.0) #16161d eigengrau


    

    glutInit([])
    #glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA) 

    

    glEnable(GL_LIGHT0)
    #glLightfv(GL_LIGHT0, GL_AMBIENT, [0.5, 0.5, 0.5, 1])
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.9, 0.9, 0.9, 1])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 0.0, 1.0, 1])


    

    start = [1, 1, 2]
    start2 = [1, 7, 2]
    #BUFFER = 0.4 # stage - BUFFER = coordinates

    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, (display[0]/display[1]), 0.1, 550.0)

    glMatrixMode(GL_MODELVIEW)

    gluLookAt(start[0], start[1], start[2], start2[0], start2[1], start2[2], 0, 0, 1)
    # look at has to be same angle to track  walking

    

    viewMatrix = glGetFloatv(GL_MODELVIEW_MATRIX)
    glLoadIdentity()

    # init mouse movement and center mouse on screen
    m = [display[0] // 2, display[1] // 2]
    mm = [0, 0]
    pygame.mouse.set_pos(m)

    # stage size
    stage_min = (0, 0, 0)
    stage_max = (500, 500, 30)
    

    v = [0, -2, 2]
    #v = [1, 1, 2]
    p = [1, 1, 0]
    # track bubba - camera pos
    bubba = PlayerObject(start[0], start[1], start[2], 0, stage_min, stage_max)


    rv = 0.005
    EARTH_SIZE = 1.0
    EARTH_R = 6371.0 
    EARTH_ORBIT = 10.0

    c_list = []


    # sun
    px0 = (stage_max[0] - stage_min[0]) // 2 
    py0 = (stage_max[1] - stage_min[1]) // 2
    pz0 = (stage_max[2] - stage_min[2]) // 2
    p = [px0, py0, pz0]

    v = [0, 0, 0]
    c = Thing(p, v)
    c.id = "sun"
    c.set_min_max(stage_min, stage_max)
    c.sphere_size = 1.0
    c.clr = (1.0, 1.0, 0.0, 1.0)


    c_list.append(c)

    # earth
    px = px0 + EARTH_ORBIT
    py = py0
    pz = pz0
    pe = [px, py, pz]

    v = [0, 0, 0]
    c = Thing(pe, v)
    c.ctr = (px0, py0, pz0)
    c.rv = rv
    c.radius = EARTH_ORBIT
    c.id = "earth"
    c.set_min_max(stage_min, stage_max)
    c.sphere_size = EARTH_SIZE
    c.clr = (0.0, 1.0, 1.0, 1.0)
    #c.trail_flag = True

    c_list.append(c)

    # moon
    # 384399 km 
    # earth = 149,260,271km = 1 AU
    # 27.321681 d
    # 1737.4
    # 0.00025754
    px = px0 + EARTH_ORBIT
    py = py0 + 10
    pz = pz0
    p = [px, py, pz]

    v = [0, 0, 0]
    c = Thing(p, v)
    c.ctr = pe
    c.rv = rv * 365.25 / 27.321681
    c.radius = 1.5 #EARTH_ORBIT * 0.00025754
    c.id = "moon"
    c.set_min_max(stage_min, stage_max)
    c.sphere_size = EARTH_SIZE * 1737.4 / EARTH_R
    c.clr = (0.33, 0.33, 0.33, 1.0)

    c_list.append(c)


    # mercury
    # 115.88 days
    # diameter 4880 km
    # .38798 AU major axis
    # 57,910,000 km
    px = px0 + 10 * 0.38798
    py = py0
    pz = pz0
    p = [px, py, pz]

    v = [0, 0, 0]
    c = Thing(p, v)
    c.ctr = (px0, py0, pz0)
    c.rv = rv * 365.25 / 87.9691
    c.radius = EARTH_ORBIT * 0.38798
    c.id = "mercury"
    c.set_min_max(stage_min, stage_max)
    c.sphere_size = EARTH_SIZE * 2440 / EARTH_R
    c.clr = (0.0, 0.5, 0.5, 1.0)

    c_list.append(c)



    # venus
    # .723332 AU major axs
    # 224.701 days
    # radius 6,051.8
    px = px0 + 10 * 0.38798
    py = py0
    pz = pz0
    p = [px, py, pz]
        
    v = [0, 0, 0]
    c = Thing(p, v)
    c.ctr = (px0, py0, pz0)
    c.rv = rv * 365.25 / 224.701
    c.radius = EARTH_ORBIT* 0.723332
    c.id = "venus"
    c.set_min_max(stage_min, stage_max)
    c.sphere_size = EARTH_SIZE * 6051.8 / EARTH_R
    c.clr = (1.0, 0.0, 0.5, 1.0)

    c_list.append(c)



    # mars
    # 1.52368055 AU
    # 779.94  days
    # 3389.5 km radius
    px = px0 + EARTH_ORBIT * 1.52368
    py = py0
    pz = pz0
    pm = [px, py, pz]
    
    v = [0, 0, 0]
    c = Thing(pm, v)
    c.ctr = (px0, py0, pz0)
    c.rv = rv * 365.25 / 696.98
    c.radius = EARTH_ORBIT * 1.52368055
    c.id = "mars"
    c.set_min_max(stage_min, stage_max)
    c.sphere_size = EARTH_SIZE * 3389.5 / EARTH_R
    c.clr = (0.8, 0.0, 0.0, 1.0)

    c_list.append(c)

    # phobos
    # 9376 km
    # 0.318910 d orbit
    # radius 11.08km

    px = px0 + EARTH_ORBIT * 1.52368
    py = py0
    pz = pz0
    p = [px, py, pz]
    
    v = [0, 0, 0]
    c = Thing(p, v)
    c.ctr = pm 
    #c.rv = rv * 365.25 / 0.318910
    c.rv = rv * 365.25 / 31.891 # 100x slower
    c.radius = 1.1 #9376 / EARTH_R
    c.id = "phobos"
    c.set_min_max(stage_min, stage_max)
    c.sphere_size = 0.1 # 11km
    c.clr = (0.25, 0.25, 0.25, 1.0)

    c_list.append(c)

    # deimos
    # 32463.2 km - 3.46x more
    # 1.263 d orbit
    # 6.27 km radius
    px = px0 + EARTH_ORBIT * 1.52368
    py = py0
    pz = pz0
    p = [px, py, pz]
    
    v = [0, 0, 0]
    c = Thing(p, v)
    c.ctr = pm 
    #c.rv = rv * 365.25 / 1.263 # too fast to see nicely
    c.rv = rv * 365.25 / 12.63 # 10x slower
    c.radius = 1.1 * 3.46 #32463.2 / EARTH_R
    c.id = "deimos"
    c.set_min_max(stage_min, stage_max)
    c.sphere_size = 0.05 # 11km
    c.clr = (0.5, 0.5, 0.5, 1.0)

    c_list.append(c)

    # jupiter
    # 5.4570 AU
    # 398.88d (or 11.862 yr)
    # radius = 69911
    px = px0 + EARTH_ORBIT * 1.52368
    py = py0
    pz = pz0
    p = [px, py, pz]
    
    v = [0, 0, 0]
    c = Thing(p, v)
    c.ctr = (px0, py0, pz0)
    c.rv = rv * 365.25 / 4332.59
    c.radius = EARTH_ORBIT * 5.457
    c.id = "jupiter"
    c.set_min_max(stage_min, stage_max)
    c.sphere_size = EARTH_SIZE * 69911 / EARTH_R
    c.clr = (0.8, 0.6, 0.4, 1.0)

    c_list.append(c)


    # saturn
    # 5.4570 AU
    # 398.88d (or 11.862 yr)
    # radius = 69911
    px = px0 + EARTH_ORBIT * 1.52368
    py = py0
    pz = pz0
    p = [px, py, pz]

    v = [0, 0, 0]
    c = Thing(p, v)
    c.ctr = (px0, py0, pz0)
    c.rv = rv * 365.25 / 10755.7
    c.radius = EARTH_ORBIT * 9.5826
    c.id = "saturn"
    c.set_min_max(stage_min, stage_max)
    c.sphere_size = EARTH_SIZE * 58232 / EARTH_R
    c.clr = (0.0, 0.7, 0.7, 1.0)

    c_list.append(c)


    # uranus
    px = px0 + EARTH_ORBIT * 1.52368
    py = py0
    pz = pz0
    p = [px, py, pz]

    v = [0, 0, 0]
    c = Thing(p, v)
    c.ctr = (px0, py0, pz0)
    c.rv = rv * 365.25 / 30688.5
    c.radius = EARTH_ORBIT * 19.19126
    c.id = "uranus"
    c.set_min_max(stage_min, stage_max)
    c.sphere_size = EARTH_SIZE * 25362 / EARTH_R
    c.clr = (0.9, 0.9, 0.9, 1.0)

    c_list.append(c)    

    # neptune
    # 30.07 AU
    # 367.49 days
    # r = 24764
    px = px0 + EARTH_ORBIT * 1.52368
    py = py0
    pz = pz0
    p = [px, py, pz]

    v = [0, 0, 0]
    c = Thing(p, v)
    c.ctr = (px0, py0, pz0)
    c.rv = rv * 365.25 / 60159
    c.radius = EARTH_ORBIT * 30.07
    c.id = "neptune"
    c.set_min_max(stage_min, stage_max)
    c.sphere_size = EARTH_SIZE * 24764 / EARTH_R
    c.clr = (0.0, 0.3, 1.0, 1.0)

    c_list.append(c)    



    vv = 0.25 # movement velocity for player
    up_down_angle = 0.0

    light_flag = True
    paused = False
    run = True

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                    run = False
                if event.key == pygame.K_PAUSE or event.key == pygame.K_p:
                    paused = not paused
                    pygame.mouse.set_pos(m) 
            if not paused: 
                if event.type == pygame.MOUSEMOTION:
                    mm = [event.pos[0] - m[0], event.pos[1] - m[1]]
                pygame.mouse.set_pos(m)    

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

            if keypress[pygame.K_l]:
                light_flag = not light_flag


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

            glPushMatrix()

            draw_floor(stage_min, stage_max)
            #draw_ceiling(stage_min, stage_max)
            draw_borders(stage_min, stage_max)


            
            glPopMatrix()



            # get center of earth & mars to rotate moons
            pe = (0,0,0) # positon earth
            pm = (0,0,0) # position mars
            for c in c_list:
                if c.id == "earth":
                    pe = (c.p[0], c.p[1], c.p[2])
                if c.id == "mars":
                    pm = (c.p[0], c.p[1], c.p[2])
            for c in c_list:
                if c.id == "moon":
                    c.ctr = pe
                if c.id in ("phobos","deimos"):
                    c.ctr = pm



            # for list of objects, have them do something ...
            for c in c_list:

                c.rotate_thing()

                glPushMatrix()
                glTranslatef(c.p[0], c.p[1], c.p[2])
                
                c.angle += c.rv
                
                # planet color
                glColor4f(c.clr[0], c.clr[1], c.clr[2], c.clr[3])
                
                
                if c.id == "saturn":
                    # inner, outer, nsides, rings
                    glutSolidSphere(c.sphere_size, 32, 32)
                    glScalef(1.0, 1.0, 0.1)
                    glutSolidTorus(c.sphere_size*1.1, c.sphere_size * 1.25, 9, 15)
                else:
                    glutSolidSphere(c.sphere_size, 32, 32)
                glPopMatrix()


                glColor3f(0.1, 0.3, 0.9) 
                glBegin(GL_LINES) 
                glVertex3f(c.p[0], c.p[1], c.p[2])
                if c.id == "moon":
                    glVertex3f(pe[0], pe[1], pe[2])    
                elif c.id in ("phobos","deimos"):
                    glVertex3f(pm[0], pm[1], pm[2])    
                else:
                    glVertex3f(px0, py0, pz0)    
                
                glEnd()

                if c.trail_flag:
                    glColor3f(1.0, 0.5, 0.25) #, 1.0)
                    glBegin(GL_LINES) 
                    glVertex3f(c.p[0], c.p[1], c.p[2])
                    for t in c.trail_list:
                        glVertex3f(t[0], t[1], c.p[2])

                    glEnd()


            draw_text(10,10, " A: {:.2f}, X: {:.2f}, Y: {:.2f}, Z: {:.2f} ".format(bubba.aa, bubba.xx, bubba.yy, bubba.zz ))

            pygame.display.flip()
            pygame.time.wait(10)

    pygame.quit()


def draw_text(x, y, text):                                                
    text_surface = font.render(text, True, (255, 255, 255, 100), (0, 100, 0, 0))
    text_data = pygame.image.tostring(text_surface, "RGBA", True)
    glWindowPos2d(x, y)
    glDrawPixels(text_surface.get_width(), text_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)


if __name__ == '__main__':

    
    screen = init_screen()
    font = pygame.font.SysFont('arial', 32)
    main(screen)

    sys.exit(0)
