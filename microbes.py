#!/usr/bin/env python
#! -*- coding: utf-8 -*-
"""
Something like 3d asteroids 

Use glut for rendering standard objects - use glscale to shrink and grow

x = left-right, y = forward-back, z = up-down

draw crosshairs
collisions with me (or capture - right mouse button for tractor beam?)
zap sound, explode sound

https://mixkit.co/free-sound-effects/

* disabled espeak

to do:
mines
ufos



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
from copy import deepcopy

images = [None, None] 


def calc_v2(mass1, mass2, v1, v2):

    v_new = (mass1 * v1 + mass2 * v2)/(mass1 + mass2)
    return v_new


def get_clr():
    
    clr = [random.random(),random.random(),random.random(), 1.0]
    return clr


def dist3(p1, p2):
    xd = (p1[0] - p2[0]) ** 2
    yd = (p1[1] - p2[1]) ** 2
    zd = (p1[2] - p2[2]) ** 2
    d = math.sqrt(xd + yd + zd)
    
    return d


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
    dist = 1.0
    # x, y, z
    p = [0, 0, 0]
    v = [0, 0, 0]

    min_pt = [0, 0, 0]
    max_pt = [10, 10, 10]

    rv = 0.0 # rotate velocity
    angle = 0.0
    rm = [0, 0, 0] # x, y, z rotation ratios
    shield = 0.0
    scale = 1.0
    wire_flag = False
    hit_flag = False
    value = 0

    def __init__(self, p, v):
        self.p = p
        self.v = v
        #self.clr = get_clr()
        self.alive_flag = True

    def set_min_max(self, min_pt, max_pt):
        self.min_pt = min_pt
        self.max_pt = max_pt

    def move(self):
        if self.alive_flag:
            self.p[0] = self.p[0] + self.v[0]
            self.p[1] = self.p[1] + self.v[1]
            self.p[2] = self.p[2] + self.v[2]

            x_flag = False
            y_flag = False
            z_flag = False

            if self.p[0] > self.max_pt[0] - self.pad or self.p[0] < self.min_pt[0] + self.pad:
                #self.v[0] = self.v[0] * -1
                x_flag = True

            if self.p[1] > self.max_pt[1] - self.pad or self.p[1] < self.min_pt[1] + self.pad:
                #self.v[1] = self.v[1] * -1
                y_flag = True
            
            if self.p[2] > self.max_pt[2] - self.pad or self.p[2] < self.min_pt[2] + self.pad:
                #self.v[2] = self.v[2] * -1
                z_flag = True

            if self.shape == "torpedo" and (x_flag or y_flag or z_flag):
                self.alive_flag = False
                #print(f"torpedo {self.id} hit border")
            else:
                if x_flag:
                    self.v[0] = self.v[0] * -1

                if y_flag:
                    self.v[1] = self.v[1] * -1

                if z_flag:
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
    vx = 0.0
    vy = 0.0
    vz = 0.0

    vi = 0.1
    shield = 100
    stage_min = [0, 0, 0]
    stage_max = [10, 10, 10]
    def __init__(self,x, y, z, a, stage_min, stage_max):
        self.xx = x
        self.yy = y
        self.zz = z
        self.p0 = (self.xx, self.yy, self.zz)
        self.aa = a
        self.stage_min = stage_min
        self.stage_max = stage_max

    #def go2(self, vv, a0=0):
    #    vv = vv + vi

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
            self.p0 = (self.xx, self.yy, self.zz)

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
            self.p0 = (self.xx, self.yy, self.zz)

        return go_flag




def get_xyz(min_px, max_px):

    x = random.random() * (max_px[0] - min_px[0]) + min_px[0]    
    y = random.random() * (max_px[1] - min_px[1]) + min_px[1]    
    z = random.random() * (max_px[2] - min_px[2]) + min_px[2]    
    return x,y,z



def draw_borders(stage_min, stage_max):

    glBegin(GL_LINES) 


    
    # floor
    x0 = stage_min[0]
    x1 = stage_max[0]
    y0 = stage_min[1]
    y1 = stage_max[1]
    z0 = stage_min[2]
    z1 = stage_max[2]


    """
    x0, y1           x1, y1
    
    x0, y0           x1, y0
    """

    s = 5

    # floor & ceiling
    glColor3f(0.25, 0.25, 0.25)	
    for z in [z0, z1]:

        for x in range(x0, x1+1,s):
            glVertex3f(x, y0, z)
            glVertex3f(x, y1, z)

        for y in range(y0, y1+1, s):
            glVertex3f(x0, y, z)
            glVertex3f(x1, y, z)
            
        #glVertex3f(x0, y0, z)
        #glVertex3f(x0, y1, z)


        #glVertex3f(x0, y0, z)
        #glVertex3f(x1, y0, z)

        #glVertex3f(x1, y1, z)
        #glVertex3f(x1, y0, z)

        #glVertex3f(x1, y1, z)
        #glVertex3f(x0, y1, z)

    #glColor3f(0.0, 1.0, 1.0)	
    #for y in [y0, y1]:
    glColor3f(1.0, 0.25, 0.25)	
    for y in range(y0, y1, s):

        
        for z in (z0, z1):
            glVertex3f(x0, y, z)
            glVertex3f(x0, y, z)

            glVertex3f(x1, y, z)
            glVertex3f(x1, y, z)

        
        glVertex3f(x0, y, z0)
        glVertex3f(x0, y, z1)

        glVertex3f(x1, y, z0)
        glVertex3f(x1, y, z1)



    
    glColor3f(0.25, 0.25, 1.0)	
    """
    for z in range(z0, z1, s):
        for x in range(x0, x1, s):
    
            glVertex3f(x, y1, z0)
            glVertex3f(x1, y1, z)
    """
    x = x0

    sx = int(s * (x1 - x0) / (z1 - z0))
    s = 5
    
    for z in range(z0, z1, s):
        glVertex3f(x, y1, z0)
        glVertex3f(x1, y1, z)

        glVertex3f(x, y0, z0)
        glVertex3f(x1, y0, z)

        x += sx
        #glVertex3f(x0, y0, z)
        #glVertex3f(x1, y0, z)


    glEnd()



def new_cell(stage_min, stage_max, id):

    # random x,y,z
    px = random.random() * (stage_max[0] - stage_min[0]) + stage_min[0]
    py = random.random() * (stage_max[1] - stage_min[1]) + stage_min[1]
    pz = random.random() * (stage_max[2] - stage_min[2]) + stage_min[2]

    p = [px, py, pz]
    #cv = random.random() * 0.1 + 0.05
    #cvx = random.random() * 0.1 + 0.05
    #cvy = random.random() * 0.1 + 0.05
    #cvz = random.random() * 0.1 + 0.05
    cvx = (random.random() - 0.5) * 0.1
    cvy = (random.random() - 0.5) * 0.1
    cvz = (random.random() - 0.5) * 0.1
    v = [cvx, cvy, cvz]
    #v = [0,0,0]
    #v = random.choice([[0, cv, 0], [cv, 0, 0], [cv, cv, 0], [0, 0, cv], [cv, 0, cv], [0, cv, cv], [cv, cv, cv]])
    cell = Thing(p, v)
    cell.set_min_max(stage_min, stage_max)
    cell.clr = get_clr() 
    cell.id = id
    # transparent
    if random.random() > 0.95:
        cell.clr[3] = random.random()

    # rotation
    cell.rv = random.random() + 0.1
    cell.rm = random.choice([[1, 0, 0], [0, 1, 0], [1, 1, 1], [1, 1, 0], [0, 1, 1], [1, 0, 1]])
    
    cell.mass = 5.0 #0.5 #random.random()/2 + 0.5
    cell.value = cell.mass * 100

    cell.dist = 0.0
    #"torus", "sphere", "cone", "teapot"
    # 6, 8, 12, 4, 20
    cell.shape = random.choice(["cube", "octahedron", "dodecahedron", "tetrahedron", "icosahedron"])
    #cell.shape = "cube"
    # , "sphere"
    #cell.shape = "octahedron"
    #cell.shape = "cube"
    #cell.shape = "dodecahedron"
    #cell.shape = "tetrahedron"
    #cell.shape = "icosahedron"

    #cell.scale = 0.8
    #cell.shield = 100.0
    cell.shield = 0.0
    if cell.shape == "octahedron":
        cell.dist = 4.0
        # sphere = 1.0
    if cell.shape == "cube":
        cell.dist = 3.0  # mass = 5, dist = 3, mass = 10, dist = 6
        #cell.mass = 10.0
        #cell.dist = 6.0
    if cell.shape == "dodecahedron": # 12
        cell.dist = 8.0
 
    if cell.shape == "tetrahedron": # 4
        cell.dist = 3.5

    if cell.shape == "icosahedron": 
        cell.dist = 4.0

    if cell.shape in ("dodecahedron", "cube", "octahedron", "dodecahedron", "tetrahedron", "icosahedron"):
        #c.scale = 0.5 * random.random()
        #cell.scale = 0.25
        #cell.scale = 0.5
        pass

    elif cell.shape == "teapot":
        #c.teapot_scale = random.random()*0.5 + 0.5
        cell.teapot_scale = 0.5
    elif cell.shape == "cone":
        cell.cone_base = random.random() + 0.5
        cell.cone_height = random.random() + 0.5
        #glutSolidCone(double base, double height, int slices, int stacks)
    elif cell.shape == "torus":
        # inner, outer
        #glutSolidTorus(0.2, 0.8, 9, 14)
        cell.torus_inner = random.random()*0.5
        #c.torus_inner = 0
        cell.torus_outer = cell.torus_inner + random.random()*0.5
    elif cell.shape == "sphere":
        cell.sphere_size = random.random() + 0.5
        #cell.sphere_size = 1.0

    return cell



def clone_cell(cell, id):

    new_cell = deepcopy(cell)

    vv = 1.618

    #if id % 2  == 0:
    #    vv = -vv

    #x = random.choice([vv, -vv])
    #y = random.choice([vv, -vv])
    #z = random.choice([vv, -vv])
    #new_v = [x*cell.v[0], y*cell.v[1], z*cell.v[2]]
    cvx = (random.random() - 0.5) * 0.1
    cvy = (random.random() - 0.5) * 0.1
    cvz = (random.random() - 0.5) * 0.1        
    new_v = [vv*cvx, vv*cvy, vv*cvz]

    new_cell.rv = cell.rv * vv
    new_cell.rm = random.choice([[1, 0, 0], [0, 1, 0], [1, 1, 1], [1, 1, 0], [0, 1, 1], [1, 0, 1]])

    new_cell.v = new_v
    new_cell.mass = cell.mass * 0.618
    # asteroids - value grows as cell size shrinks
    new_cell.value = cell.value * 1.618
    
    new_cell.dist = cell.dist / 2 # to fix
    new_cell.alive_flag = True
    new_cell.id = id

    return new_cell

def speak2(msg):
    p = random.randint(1,100)
    cmd = f'espeak -a 200 -k 20 -p {p} -s 155 "{msg}" &'
    #os.system(cmd)

    """
espeak -a 200 -k 20 -p 80 -s 155 \
    "What the hell are you looking at? I will pull out your pubic hair! Time to die."

g = word gap
a = amplitude
k = 1, 2, 20?
p = pitch
s = words per minute
    """


def init_screen():
    pygame.init()
    display = (1000, 800)
    #screen = pygame.display.set_mode((max_x, max_y))
    screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.mouse.set_visible(False)

    return display


def main(display):

    glClearColor(0.0, 0.0, 0.0, 0.0) #16161d eigengrau
    #glClearColor(0.0, 96.0, 96.0, 0.0) 

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
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.5, 0.5, 0.5, 1])
    #glLightfv(GL_LIGHT0, GL_AMBIENT, [0.25, 0.25, 0.25, 1])
    #glLightfv(GL_LIGHT0, GL_AMBIENT, [0.9, 0.9, 0.9, 1])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1])


    

    start = [1, 1, 2]
    start2 = [1, 7, 2]
    #BUFFER = 0.4 # stage - BUFFER = coordinates

    glMatrixMode(GL_PROJECTION)
    #gluPerspective(45, (display[0]/display[1]), 0.1, 150.0)
    # 300.0 = everything in 150x150x150
    gluPerspective(45, (display[0]/display[1]), 0.1, 300.0)

    glMatrixMode(GL_MODELVIEW)

    gluLookAt(start[0], start[1], start[2], start2[0], start2[1], start2[2], 0, 0, 1)
    # look at has to be same angle to track  walking

    

    viewMatrix = glGetFloatv(GL_MODELVIEW_MATRIX)
    glLoadIdentity()



    # stage size
    stage_min = (0, 0, 0)
    stage_max = (150, 150, 100)
        

    #v = [0, -2, 2]
    #v = [1, 1, 2]
    p = [1, 1, 0]
    # track bubba - camera pos
    bubba = PlayerObject(start[0], start[1], start[2], 0, stage_min, stage_max)

    # create microbes
    m_list = []
    m_cnt = 0
    for m in range(8):
        m_cnt = m
        m_list.append(new_cell(stage_min, stage_max, m_cnt))
    m_cnt = 25

    d_list = [] # detonations
        
    # init mouse movement and center mouse on screen
    m = [display[0] // 2, display[1] // 2]
    mm = [0, 0]
    pygame.mouse.set_pos(m)

    

    up_down_angle = 0.0

    torpedo_sound = pygame.mixer.Sound("sounds/laser.wav")
    hit_sound1 = pygame.mixer.Sound("sounds/explode1.wav")
    hit_sound2 = pygame.mixer.Sound("sounds/explode2.wav")
    
    score = 0
    f = 0



    paused = False
    move_flag = True 
    run = True

    glide_flag = False

    vv = 0.25 # movement velocity for player
    turn_v = 0.25
    if glide_flag:
        vv = 0.0

    friction = 0.01
    vi = 0.02 # velocity increment
    max_v = 0.618
    

    #mouth = pyttsx3.init()
    #voice_list = mouth.getProperty("voices")
    #mouth.setProperty("voice", voice_list[10])
    #speak("What are you waiting for, Christmas?", mouth)
    #speak2("What the hell are you staring at?")
    speak2("Do you have any idea the powers you toy with?")
    
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

                f = f + 1
                if f % 1500 == 0:
                    pass
                    #speak2(f"the score is {score:.0f}")


                if event.type == pygame.MOUSEMOTION:
                    mm = [event.pos[0] - m[0], event.pos[1] - m[1]]
                pygame.mouse.set_pos(m)    
                
                if event.type == pygame.MOUSEBUTTONUP:
                
                    if event.button == 1:

                        #pygame.mixer.Sound.play(shot_sound_3)
                        # add to sound_list
                        #m_list.append(new_cell(stage_min, stage_max))
                        p = [bubba.xx+0.5, bubba.yy, bubba.zz]
                        v = [0,0,0] 
                        vtorpedo = 3
                        v[0] = math.sin(math.radians(bubba.aa)) * math.cos(math.radians(up_down_angle)) * vtorpedo
                        v[1] = math.cos(math.radians(bubba.aa)) * math.cos(math.radians(up_down_angle)) * vtorpedo
                        v[2] = -math.sin(math.radians(up_down_angle)) * vtorpedo

                        torpedo = Thing(p, v)
                        torpedo.set_min_max(stage_min, stage_max)
                        # 6d14c4 = purple
                        #torpedo.clr = (0.784, 0.0784, 0.768, 1.0)
                        torpedo.clr = (0.3412, 0.0314, 0.3803, 1.0)
                        torpedo.shape = "torpedo"

                        torpedo.sphere_size = 0.25
                        torpedo.mass = 0.5
                        torpedo.id = m_cnt
                        m_cnt += 1

                        m_list.append(torpedo)

                        pygame.mixer.Sound.play(torpedo_sound)


        if not paused:
            # get keys
            keypress = pygame.key.get_pressed()

        
            # init model view matrix
            glLoadIdentity()

            # apply the look up and down
            up_down_angle += mm[1]*turn_v
            glRotatef(up_down_angle, 1.0, 0.0, 0.0)

            # init the view matrix
            glPushMatrix()
            glLoadIdentity()

            if glide_flag:
                # forward velocity [w, s]
                # side velocity left-right = [a, d]
                print(f"vv: {vv:.2f}")
                if vv > 0 and bubba.go(vv):
                    glTranslatef(0, 0, vv)
                    vv = vv - friction
                elif vv < 0 and bubba.go(-vv):
                    #glTranslatef(0, 0, -vv)    
                    glTranslatef(0, 0, vv)    
                    vv = vv + friction

                if keypress[pygame.K_w]:
                    #vv = max(vv + vi, max_v)
                    vv = vv + vi
                    vv = max(vv, max_v)

                if keypress[pygame.K_s]:
                    #vv = min(vv - vi, -0.618)
                    vv = vv - vi
                    vv = min(vv, -max_v)
                if keypress[pygame.K_s]:
                    vv = min(vv - vi, -0.618)
                    vv = vv - vi

                if keypress[pygame.K_d]:
                    vv = min(vv - vi, -0.618)
                    vv = vv - vi


                if keypress[pygame.K_a]:
                    if bubba.go(-vv, 90):
                        glTranslatef(vv, 0, 0)

                if keypress[pygame.K_q]:
                    if bubba.up(-vv):
                        glTranslatef(0, vv, 0)


            else:

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


            if keypress[pygame.K_m]:
                move_flag = not move_flag

            if keypress[pygame.K_x]:
                pass
                # stop movement



            #glTranslate(bubba.vx, bubba.vy, bubba.vz)
                

            # apply the left and right rotation
            glRotatef(mm[0]*turn_v, 0.0, 1.0, 0.0)
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


            draw_borders(stage_min, stage_max)

            # player collisions
            for c in m_list:
                if not c.alive_flag:
                    continue
                if c.shape == "torpedo":
                    continue

                d = dist3(c.p, bubba.p0)
                status = ""
                if d < c.dist + 4.0:
                    status = "hit"
                    bubba.shield = bubba.shield - 1.0
                #print(f"bubba to {c.id}: {d:0.2f} - {c.dist}  {status}")

            # collisions & stuff
            mnew_list = []
            for c1 in m_list:
                if not c1.alive_flag:
                    continue

                for c2 in m_list:
                    if not c2.alive_flag: 
                        continue
                    if c1.id == c2.id:
                        continue
                    
                    
                    d = dist3(c1.p, c2.p)
                    #d = 100
                    if d < c1.dist + c2.dist:
                        #print("c1 - c2 collision")
                        #print("boom - {}, {}, d = {:.2f}".format(c1.id, c2.id, d))
                        

                        if c1.shape == "torpedo":
                            c1.alive_flag = False
                            c1.timer = 50
                            d_list.append(c1)
                            
                            #print(f"dist to bubba: {d1:.2f}")
                            c2.alive_flag = False
                            score = score + c2.value
                            if c2.mass > 1.0:
                                
                                for _ in range(2):
                                    m_cnt += 1
                                    cell = clone_cell(c2, m_cnt)
                                    mnew_list.append(cell)
                                
                                d1 = dist3(c2.p, bubba.p0)
                                hit_sound1.set_volume(max(1-d1 / 200.0, 0))
                                pygame.mixer.Sound.play(hit_sound1)


                        elif c2.shape == "torpedo":
                            c2.alive_flag = False
                            c2.timer = 50
                            d_list.append(c2)
                            #print(bubba.p0)
                            

                            #print(f"dist to bubba: {d1:.2f}")
                            c1.alive_flag = False
                            score = score + c1.value
                            if c1.mass > 1.0:

                                for _ in range(2):
                                    m_cnt += 1
                                    cell = clone_cell(c1, m_cnt)
                                    mnew_list.append(cell)

                                d1 = dist3(c1.p, bubba.p0)    
                                hit_sound1.set_volume(max(1-d1 / 200.0, 0))
                                pygame.mixer.Sound.play(hit_sound1)
                                #d2 = dist3(c1, bubba)
                                #print(d2)
                        else:
                            #print(f"c1: {c1.mass}, {c1.v[0]:.2f}, {c1.v[1]:.2f}, {c1.v[2]:.2f}")
                            #print(f"c2: {c2.mass}, {c2.v[0]:.2f}, {c2.v[1]:.2f}, {c2.v[2]:.2f}")
                            c1.v[0] = calc_v2(c1.mass, c2.mass, c1.v[0], c2.v[0])
                            c1.hit_flag = True
                            c2.hit_flag = True

                    #glBegin(GL_LINES) 
                    #glVertex3f(c1.p[0], c1.p[1], c1.p[2])
                    #glVertex3f(c2.p[0], c2.p[1], c2.p[2])
                    #glEnd()
            

            for cell in mnew_list:
                #print(f"adding {cell.id}")
                m_list.append(cell)

            

            # render cells/microbes and phages
            for c in m_list:

                if not c.alive_flag:
                     
                    if c.shape == "torpedo":
                        c.timer = 50
                        d_list.append(c)
                        #print(f"added {c.id} to demo list")
                        d1 = dist3(c.p, bubba.p0)
                        hit_sound2.set_volume(max(1-d1 / 200.0, 0))
                        pygame.mixer.Sound.play(hit_sound2)

                    m_list.remove(c)
                    continue                 

                if move_flag:
                    c.move()


                glPushMatrix()
                glTranslatef(c.p[0], c.p[1], c.p[2])
                
                c.angle += c.rv
                
                # angle, x, y, z - x,y,z relative to each other
                glRotatef(c.angle, c.rm[0], c.rm[1], c.rm[2]) # works - rotate more around x than others


                if c.shape == "torus":
                    #glutSolidTorus(double innerRadius, double outerRadius, int nSides, int rings)
                    if c.wire_flag:
                        glutWireTorus(c.torus_inner, c.torus_outer, 9, 14)
                    else:
                        glutSolidTorus(c.torus_inner, c.torus_outer, 9, 14)
                elif c.shape == "cube":
                    if c.shield > 0.0:
                        glColor4f(0.0, c.shield / 100.0, 0.0, 1.0)
                        glutWireCube(c.mass * 1.25)

                    #glScalef(c.mass, c.mass, c.mass)
                    glColor4f(c.clr[0], c.clr[1], c.clr[2], c.clr[3])
                    glutSolidCube(c.mass)
                    glColor4f(1.0, 1.0, 1.0, 1.0)
                    glutWireCube(c.mass*1.05)

                elif c.shape == "cone":
                    #glutSolidCone(double base, double height, int slices, int stacks)
                    if c.wire_flag:
                        glutWireCone(c.cone_base, c.cone_height, 10, 5)
                    else:
                        glutSolidCone(c.cone_base, c.cone_height, 10, 5)

                elif c.shape == "teapot":

                    if c.wire_flag:
                        glutWireTeapot(c.teapot_scale) # on its side
                    else:
                        glutSolidTeapot(c.teapot_scale) # on its side
                elif c.shape == "octahedron":
                    if c.shield > 0.0:
                        glColor4f(0.0, c.shield / 100.0, 0.0, 1.0)
                        glScalef(c.scale*1.5, c.scale*1.5, c.scale*1.5)
                        glutWireOctahedron()

                    glScalef(c.mass, c.mass, c.mass)
                    glColor4f(c.clr[0], c.clr[1], c.clr[2], c.clr[3])
                    glutSolidOctahedron()

                    glColor4f(1.0, 1.0, 1.0, 1.0)
                    glutWireOctahedron()

                    # dist = 4


                elif c.shape == "dodecahedron":
                    if c.shield > 0.0:
                        glColor4f(0.0, c.shield / 100.0, 0.0, 1.0)
                        glScalef(c.scale*1.5, c.scale*1.5, c.scale*1.5)
                        glutWireDodecahedron()
                    

                    glScalef(c.mass, c.mass, c.mass)
                    glColor4f(c.clr[0], c.clr[1], c.clr[2], c.clr[3])
                    glutSolidDodecahedron()
                    glColor4f(1.0, 1.0, 1.0, 1.0)
                    glutWireDodecahedron()
                    #glScalef(1.0, 1.0, 1.0)
                    

                elif c.shape == "tetrahedron":
                    if c.shield > 0.0:
                        glColor4f(0.0, c.shield / 100.0, 0.0, 1.0)
                        glScalef(c.scale*1.5, c.scale*1.5, c.scale*1.5)
                        glutWireTetrahedron()

                    glScalef(c.mass, c.mass, c.mass)
                    glColor4f(c.clr[0], c.clr[1], c.clr[2], c.clr[3])
                    glutSolidTetrahedron()

                    glColor4f(1.0, 1.0, 1.0, 1.0)
                    glutWireTetrahedron()

                elif c.shape == "icosahedron":
                    if c.shield > 0.0:
                        glColor4f(0.0, c.shield / 100.0, 0.0, 1.0)
                        glScalef(c.scale*1.5, c.scale*1.5, c.scale*1.5)
                        glutWireIcosahedron()

                    glScalef(c.mass, c.mass, c.mass)
                    glColor4f(c.clr[0], c.clr[1], c.clr[2], c.clr[3])
                    glutSolidIcosahedron()

                    glColor4f(1.0, 1.0, 1.0, 1.0)
                    #glScalef(c.mass*1.1, c.mass*1.1, c.mass*1.1)
                    glutWireIcosahedron()
                
                elif c.shape == "torpedo":
                    glColor4f(c.clr[0], c.clr[1], c.clr[2], c.clr[3])
                    glutSolidSphere(c.sphere_size, 16, 16)   
                    #glutSolidCone(1.0, 3.0, 10, 5)

                elif c.shape == "sphere":
                    # solid sphere
                    
                    glColor4f(1.0, 1.0, 1.0, 1.0)
                    glutSolidSphere(c.sphere_size, 32, 32)

                    # yellow-ish glow (transparent)                    
                    glColor4f(0.5, 0.5, 0.0, 0.15)
                    glutSolidSphere(c.sphere_size*1.8, 32, 32)   



                #glScalef(1.0, 1.0, 1.0)
                #glColor4f(0.5, 0.5, 0.5, 1.0)
                #glutWireSphere(1.0, 8, 8)

                glPopMatrix() # or stack overflow

                #glPushMatrix()
                #glTranslatef(c.p[0] + c.dist, c.p[1], c.p[2])
                #glutSolidSphere(1.0, 16, 16)
                #glPopMatrix()

            # detonations
            for d in d_list:


                d.timer = d.timer - 1
                if d.timer <= 0:
                    d_list.remove(d)
                else:
                    # F5AA00 = orange
                    # rgb(242, 140, 40) = F28C28
                    glPushMatrix()
                    glTranslatef(d.p[0], d.p[1], d.p[2])                    
                    glColor4f(0.949, 0.549, 0.157, 1.0 - d.timer/50)
                    #s1 = 50 * math.sin(math.pi / d.timer / 50)
                    s1 = (50 - d.timer) / 10
                    #glScalef(d.timer * 0.5, d.timer * 0.5, d.timer * 0.5)
                    glScalef(s1, s1, s1)
                    glutSolidSphere(0.5, 32, 32)   

                    glPopMatrix()

            #draw_text(10,10, " A: {:.2f}, X: {:.2f}, Y: {:.2f}, Z: {:.2f}, P: {:.2f} ".format(bubba.aa, bubba.xx, bubba.yy, bubba.zz, up_down_angle))
            draw_text(10, 10, f" Score: ${score:7.0f}  Shield: {bubba.shield}%, {f}")
            draw_hud()

            pygame.display.flip()
            pygame.time.wait(10)

    pygame.quit()


def draw_hud():
    # lots of stuff to add HUD options
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0.0, 1000, 700, 0.0, -1.0, 10.0)
    glMatrixMode(GL_MODELVIEW)
    #//glPushMatrix();        ----Not sure if I need this
    glLoadIdentity()
    glDisable(GL_CULL_FACE)

    glClear(GL_DEPTH_BUFFER_BIT);    

    glColor3f(1.0, 1.0, 1.0)
    glBegin(GL_LINE_STRIP)
    #glBegin(GL_QUADS)
    glVertex2f(475, 325)
    glVertex2f(550, 375)
    glEnd()
    glBegin(GL_LINE_STRIP)
    glVertex2f(475, 375)
    glVertex2f(550, 325)    

    glEnd()


    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_text(x, y, text):                                                
    text_surface = font.render(text, True, (255, 255, 155, 100), (0, 0, 0, 0))
    text_data = pygame.image.tostring(text_surface, "RGBA", True)
    glWindowPos2d(x, y)
    glDrawPixels(text_surface.get_width(), text_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)

    

if __name__ == '__main__':
    #o1 = Thing([1,1,1], [0,0,0])
    #o2 = Thing([2,2,2], [0,0,0])

    #print(dist3(o1, o2))

    screen = init_screen()
    font = pygame.font.SysFont('arial', 32)
    main(screen)

    sys.exit(0)
