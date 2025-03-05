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







def init_screen():
    pygame.init()
    display = (1000, 800)
    #screen = pygame.display.set_mode((max_x, max_y))
    screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.mouse.set_visible(False)

    return display


def main(display):

    # initialize 
    glClearColor(0.0, 0.0, 0.0, 0.0) # background color

    glutInit([]) # for rendering the sphere


    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_COLOR_MATERIAL) # enable coloring
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)


    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [5.0, 5.0, 10.0, 1]) # turn on the light


    glMatrixMode(GL_PROJECTION)
    gluPerspective(45, (display[0]/display[1]), 0.1, 550.0)

    glMatrixMode(GL_MODELVIEW)


    # camera starting point & direction we are looking
    start = [1, 1, 2]
    start2 = [1, 7, 2]
    gluLookAt(start[0], start[1], start[2], start2[0], start2[1], start2[2], 0, 0, 1)
    # look at has to be same angle to track movement


    viewMatrix = glGetFloatv(GL_MODELVIEW_MATRIX)
    #glLoadIdentity()

    # init mouse movement and center mouse on screen
    m = [display[0] // 2, display[1] // 2]
    mm = [0, 0]
    pygame.mouse.set_pos(m)

    # stage size
    stage_min = (0, 0, 0)
    stage_max = (10, 10, 10)
    
    

    # track bubba - camera pos
    bubba = PlayerObject(start[0], start[1], start[2], 0, stage_min, stage_max)


    vv = 0.1 # movement velocity for player
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


            # movement W, S, A, D, Q, E
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



            # lets draw a floor, line and sphere

            glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

            glPushMatrix()

            # draw floor
            
            glColor3f(1.0, 0.0, 0.0)	
            glBegin(GL_QUADS)
            glVertex3f(stage_min[0], stage_min[1], stage_min[2]) # A 0,0,0
            glVertex3f(stage_max[0], stage_min[1], stage_min[2]) # B 10,0,0
            glVertex3f(stage_max[0], stage_max[1], stage_min[2]) # C 10,10,0
            glVertex3f(stage_min[0], stage_max[1], stage_min[2]) # D 0,10,0
            glEnd()
            

            # draw line, requires 2 glVertex3f commands
            glColor3f(1.0, 1.0, 1.0)	
            glBegin(GL_LINES) 

            glVertex3f(stage_min[0], stage_min[1], stage_min[2]) # A 0,0,0
            glVertex3f(5, 5, 5) 

            glEnd()


            
            # create green sphere in the middle

            glColor3f(0, 1.0, 0) # green

            glTranslatef(5.0, 5.0, 5.0) # location of sphere
            glutSolidSphere(0.150, 32, 32) # or wire sphere
                    


            glPopMatrix() # finished recalculating the view



            # flip screen
            pygame.display.flip()
            pygame.time.wait(10)

    pygame.quit()



if __name__ == '__main__':
   
    screen = init_screen()
    main(screen)

    sys.exit(0)
