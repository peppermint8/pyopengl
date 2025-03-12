#!/usr/bin/env python
#! -*- coding: utf-8 -*-
"""

Create thing with tail that trails in the correct angle

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
    buffer = ""

    shape = "cube"
    mtype = "orbit"
    pad = 0.4 # padding
    rv = 0.0 # rotate velocity
    rr = 0.0 # initial radians
    radius = 1.0
    trail_flag = False
    trail_list = []
    clr = [1, 1, 1] # 0 .. 1
    clrv = [0,0,0]
    new_clr = [1,1,1]

    # x, y, z
    p = [0, 0, 0]
    p0 = [0,0,0]
    v = [0, 0, 0]
    ctr = [0,0,0]
    min_pt = [0, 0, 0]
    max_pt = [10, 10, 10]

    rv = 0.0 # rotate velocity
    angle = 0.0
    a = 0.0 # calculated angle
    az = 0.0 # up-down angle
    af = 0 # tail flutter
    afv = 9 # flutter angle
    rm = [0, 0, 0] # x, y, z rotation ratios


    wire_flag = False

    def __init__(self, p, v):
        self.p = p
        self.v = v
        #self.clr = get_clr()
        self.zplane = self.p[2]
        #self.afv = self.afv * self.v[2]
        self.afv = random.random() * 9
        self.new_clr = get_clr()
        
        self.get_clrv()

    def get_clrv(self):

        self.cv = random.randint(100,200)

        c0 = (self.new_clr[0] - self.clr[0])/self.cv
        c1 = (self.new_clr[1] - self.clr[1])/self.cv
        c2 = (self.new_clr[2] - self.clr[2])/self.cv

        self.clrv = [c0, c1, c2]

    def set_min_max(self, min_pt, max_pt):
        self.min_pt = min_pt
        self.max_pt = max_pt
        self.ctr = [
            (self.max_pt[0] - self.min_pt[0]) // 2, 
            (self.max_pt[1] - self.min_pt[1]) // 2, 
            (self.max_pt[2] - self.min_pt[2]) // 2
        ]


    def color_cycle(self):
        
        # change to new color
        c0 = self.clr[0] + self.clrv[0]
        c1 = self.clr[1] + self.clrv[1]
        c2 = self.clr[2] + self.clrv[2]
        c0 = min(1, c0)
        c0 = max(0, c0)
        c1 = min(1, c1)
        c1 = max(0, c1)
        c2 = min(1, c2)
        c2 = max(0, c2)
        
        self.clr = [c0, c1, c2, 1.0]
        self.cv = self.cv - 1
        if self.cv == 0:
            self.new_clr = get_clr()
            self.get_clrv()


    def move(self):

        self.af = self.af + self.afv
        if self.af > 20 or self.af < -20:
            self.afv = -self.afv

        if self.mtype == "line":
            self.line()
        else:
            self.orbit()

    def line(self):

        for dd in (0,1,2):
            self.p[dd] = self.p[dd] + self.v[dd]
            if self.p[dd] > self.max_pt[dd]:
                self.v[dd] = -self.v[dd]
            if self.p[dd] < self.min_pt[dd]:
                self.v[dd] = -self.v[dd]
    
        #print(self.p, pp0, pp1)
        self.a = math.atan2(-self.v[0], self.v[1])

        self.a = math.degrees(self.a) + self.af 

        
        z0 = math.sqrt(self.v[0] * self.v[0] + self.v[1] * self.v[1])
        self.az = math.atan2(self.v[2], z0)
        self.az = math.degrees(self.az)

        
        #nb = f"{self.v[2]}, {self.az}"
        #if nb != self.buffer:
        #    print(nb)
        #    self.buffer = nb


    def orbit(self):
        if self.rv != 0:

            #self.p0 = deepcopy(self.p)
            p0 = self.p[0]
            p1 = self.p[1]
            p2 = self.p[2]
            #new_cell = deepcopy(cell)
            self.rr = self.rr + self.rv
            # assume x-y rotation
            (x0, y0) = rotate(self.rr, self.radius, (self.ctr[0], self.ctr[1]))

            self.p[0] = x0
            self.p[1] = y0

            # z-up-down
            z0 = self.zplane + math.sin(self.rr) #* 2 

            self.p[2] = z0
            #self.az = math.degrees(self.rr)
            #self.az = math.degrees(math.sin(self.rr))
            z0 = math.sqrt(self.v[0] * self.v[0] + self.v[1] * self.v[1])
            self.az = math.atan2(self.v[2], z0)
            self.az = math.degrees(self.az)
            #self.az = math.degrees(math.atan(self.v[2]))
          
        
            self.a = math.atan2(-1*(self.p[0] - self.ctr[0]), (self.p[1] - self.ctr[1]))
            self.a = math.degrees(self.a) 
            self.a = self.a + self.af

            if self.rv < 0:
                self.a = self.a + 270
            else:
                self.a = self.a + 90
    

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

    glColor3f(1.0, 1.0, 0.25)	
    for x in range(x0, x1, s):

        for z in (z0, z1):
            glVertex3f(x, y0, z)
            glVertex3f(x, y0, z)

            glVertex3f(x, y1, z)
            glVertex3f(x, y1, z)

        
        glVertex3f(x, y0, z0)
        glVertex3f(x, y0, z1)

        glVertex3f(x, y1, z0)
        glVertex3f(x, y1, z1)

    

    glEnd()



def draw_wall2(px_list, off, clr, m=[1.0, 1.0, 1.0]):
    
    glColor4f(clr[0], clr[1], clr[2], 1.0)

    xo = yo = zo = 0

    #xo = random.random() - 0.5
    #yo = random.random() - 0.5
    #zo = random.random() - 0.5
    wire = False

    if wire:
        #glColor4f(1.0, 1.0, 1.0, 1.0)
        glBegin(GL_LINES) 
        for px in px_list:
            glVertex3f(px[0]+off[0]+xo, px[1]+off[1]+yo, px[2]+off[2]+zo)
        glEnd()

    else:

        glBegin(GL_QUADS)
        for px in px_list:

            glVertex3f(px[0]*m[0]+off[0]+xo, px[1]*m[1]+off[1]+yo, px[2]*m[2]+off[2]+zo)
        glEnd()            


    """
    glColor4f(1.0, 0.0, 0.0, 1.0)
    for px in px_list:
        glPushMatrix()
        glTranslatef(px[0]+off[0]+xo, px[1]+off[1]+yo, px[2]+off[2]+zo)
        
        glutSolidSphere(0.25, 16, 16)
        glPopMatrix()
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
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1])


    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, (display[0]/display[1]), 0.1, 550.0)

    glMatrixMode(GL_MODELVIEW)


    start = [1, 1, 2]
    start2 = [1, 7, 2]
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
    stage_max = (50, 50, 20)
    #stage_max = (20, 20, 20)
    

    v = [0, -2, 2]
    p = [1, 1, 0]
    # track bubba - camera pos
    bubba = PlayerObject(start[0], start[1], start[2], 0, stage_min, stage_max)

    o_list = []
    rv = 0.005
    px0 = (stage_max[0] - stage_min[0]) // 2 
    py0 = (stage_max[1] - stage_min[1]) // 2
    pz0 = (stage_max[2] - stage_min[2]) // 2


    p = [px0, py0, pz0]
    v = [0, 0, 0]
    
    o = Thing(p, v)
    o.ctr = (px0, py0, pz0)
    o.set_min_max(stage_min, stage_max)
    o.clr = (0.0, 0.2, 0.9, 1.0)
    o.rv = rv * 2
    o.angle = 5
    o.radius = 0
    o.shape = "dodecahedron"
    o_list.append(o)


    for i in range(25): # 100
        p = [px0+2+i, py0-2+i, pz0+2-i]
        if i >= 3:
            p = [random.randint(0, stage_max[0]), random.randint(0, stage_max[1]), random.randint(0, stage_max[2])]
        v = [random.random()/5, random.random()/5, random.random()/5]
        o = Thing(p, v)
        o.ctr = (px0, py0, pz0)
        o.set_min_max(stage_min, stage_max)
        o.clr = get_clr() #(1.0, 0.0, 0.0, 1.0)
        o.rv = rv *2
        if i == 1:
            o.clr = (0.0, 1.0, 0.0, 1.0)
            #o.rv = o.rv * -1
            # green = backwards rotate
            o.rv = -0.05
        if i == 2:
            o.clr = (1.0, 0.0, 0.0, 1.0)
        if i >= 3:
            o.mtype = "line"
            
            #v = [0.1, 0, 0]
            #v = [0, 0.1, 0]
            #v = [0.1, 0.1, 0]
            #v = [random.random()/2, random.random()/2,0]    
            #v = [random.random()/5, random.random()/5, random.random()/5]    
            v = [0.05, 0.03, 0.1]
            o.v = v
        #if i == 4:
        #    v = [0, 0, 0.1]

        o.radius = 2+i*2
        o.rr = random.random() * math.pi * 2
        #o.angle = 90 // (i+1)
        o.shape = "cone"
        o.id = i
        o_list.append(o)


    vv = 0.25 # movement velocity for player
    up_down_angle = 0.0

    
    paused = False
    run = True
    go_flag = True

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
                if event.key == pygame.K_SPACE:
                    go_flag = not go_flag
                    

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

            if keypress[pygame.K_c]:
                glRotatef(5*vv, 0.0, 1.0, 0.0)
                bubba.aa += 5 * vv

            if keypress[pygame.K_z]:
                glRotatef(-5*vv, 0.0, 1.0, 0.0)
                bubba.aa -= 5 * vv

            if keypress[pygame.K_r]:
                up_down_angle -= vv * 0.25
                glRotatef(up_down_angle, 1.0, 0.0, 0.0)                
                
            if keypress[pygame.K_v]:
                up_down_angle += vv * 0.25
                glRotatef(up_down_angle, 1.0, 0.0, 0.0)                




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

            draw_borders(stage_min, stage_max)
            
            """
            # 10x10 wall
            clr = [0.0, 0.5, 0.25]
            px_list = [[0,0,0], [10,0,0], [10,0,10], [0,0,10], [0,0,0]]
            off = [10, 20, 0]
            draw_wall2(px_list, off, clr)

            off = [10, 10, 0]
            mw = [1.5, 0, 0.5]
            draw_wall2(px_list, off, clr, mw)

            mw = [1.0, 0.2, 0.2]
            px_list = [[0,0,0], [0,10,0], [0, 10, 10], [0,0,10], [0,0,0]]
            off = [30,10,0]
            draw_wall2(px_list, off, clr, mw)

            # floor
            clr = (0.2, 0.2, 0.25)
            px_list = [[0,0,0], [10,0,0], [10,10,3], [0,10,0], [0,0,0]]
            off = [30,30,0]
            
            draw_wall2(px_list, off, clr)

            px_list = [[0,0,0], [10,0,3], [10,10,0], [0,10,0], [0,0,0]]
            off = [30,40,0]
            
            draw_wall2(px_list, off, clr)
            """


            glPopMatrix()




            for o in o_list:

                glPushMatrix()

                if o.shape == "dodecahedron":
                    pass
                    #print(o.clr)
                    #print(o.new_clr)
                    #print(o.clrv)
                    #print("........")

                glColor4f(o.clr[0], o.clr[1], o.clr[2], o.clr[3])
                
                if o.shape == "cone":
                    # base, height
                    
                    if go_flag:
                        o.move()
                        #o.orbit()
                    
                    glTranslatef(o.p[0], o.p[1], o.p[2])

                    #glRotatef(90, 1, 0, 0) 
                    glRotate(o.az, 1, 0, 0)
                    glRotatef(o.a, 0, 1, 0) # rotate
                    




                    if o.id == 3:
                        pass
                        #glColor4f(1.0, 0.0, 1.0, 1.0)
                        #glRotatef(o.az, 1, 0, 0) 
                        #glRotatef(o.a, 0, 1, 0) # rotate                    


                    glutSolidCone(0.5, 2, 32, 12)    
                    glutSolidSphere(0.50, 32, 32)
                    #glutWireSphere(0.46, 32, 32)

                if o.shape == "dodecahedron":

                    if go_flag:
                        o.angle += 1 
                        o.color_cycle()

                    glTranslatef(o.p[0], o.p[1], o.p[2])
                    glRotatef(o.angle, 0,1, 1) 
                    glutSolidDodecahedron()

                    #glScalef(1.05, 1.05, 1.05)
                    #glColor4f(0.0, 1.0, 1.0, 1.0)
                    #glutWireDodecahedron()
                    
                glPopMatrix()

            draw_text(10, 10, " A: {:.2f}, X: {:.2f}, Y: {:.2f}, Z: {:.2f} ".format(bubba.aa, bubba.xx, bubba.yy, bubba.zz ))

            pygame.display.flip()
            pygame.time.wait(10)

    pygame.quit()


def draw_text(x, y, text):                                                
    text_surface = font.render(text, True, (0, 255, 0, 150), (0, 0, 0, 0))
    text_data = pygame.image.tostring(text_surface, "RGBA", True)
    glWindowPos2d(x, y)
    glDrawPixels(text_surface.get_width(), text_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)


if __name__ == '__main__':
   
    screen = init_screen()
    font = pygame.font.SysFont('arial', 32)
    main(screen)

    sys.exit(0)
