# Oscar Saharoy 2018

import numpy, time
from math import *

class Cube(object):
    

    def __init__(self):

        self.w, self.h   = 60,30

        self.vbuffer     = [[' ' for _ in range(self.w)] for _ in range(self.h)] # 2d list of characters to print on screen

        self.cube_coords = [[-1,-1,-1],
                            [ 1,-1,-1],
                            [ 1, 1,-1],
                            [-1, 1,-1],                            
                            [-1,-1, 1],
                            [ 1,-1, 1],
                            [ 1, 1, 1],
                            [-1, 1, 1]]                     # coords of corners of the cube

        self.cube        =  numpy.matrix(self.cube_coords)  # making cube into matrix
        
        self.camangle    =  [ 0, 0.01]                      # angle of camera looking at cube
        self.angle       =  0                               # extent of cube's rotation

        self.anglestep   =  - pi*2 / 200                    # rotation of cube per timestep

        
        while True:

            self.rotate()
            self.project()
            self.display()

            time.sleep(0.03)
            


    # matrices which rotate a point about the given axis

    def rotx(self, a):

        return numpy.matrix([[ 1,      0,       0],
                             [ 0, cos(a), -sin(a)],
                             [ 0, sin(a),  cos(a)]])

    def roty(self, a):

        return numpy.matrix([[  cos(a), 0, sin(a)],
                             [       0, 1,      0],
                             [ -sin(a), 0, cos(a)]])

    def rotz(self, a):

        return numpy.matrix([[ cos(a), -sin(a), 0],
                             [ sin(a),  cos(a), 0],
                             [      0,       0, 1]])
    

    def display(self):

        # draws vbuffer to screen

        print('\n'.join([''.join(line) for line in self.vbuffer]))

        self.vbuffer = [[' ' for _ in range(self.w)] for _ in range(self.h)] # clears vbuffer


    def rotate(self):

        # rotate the cube by the angle step and add this value onto self.angle to record it

        self.cube  = self.cube * self.roty(self.anglestep) * self.rotx(self.anglestep*sin(self.angle)) # sin(self.angle) term adds randomness to rotation

        self.angle = (self.angle + self.anglestep) % (2 * pi)


    def project(self):

        # maps the cube to the screen using oblique projection

        rotated_cube = self.cube * self.roty(-self.camangle[0]) \
                                 * self.rotx(-self.camangle[1]) # rotate cube to camera perspective

        corners      = [] # onscreen coords of corners

        zdistances   = [] # store zdepth

        for i in range(8):

            # for each corner, normalize the x and y coordinates to the size of the screen

            point = rotated_cube[i]

            x,y,z = point[0,0], point[0,1], point[0,2]

            x,y   = (x+2)/4, (y+2)/4
            x,y   = x*self.w, self.h-y*self.h

            corners    += [[x,y]]

            zdistances += [z] # add z coordinate to zdepth list

        closest_index = min(range(8), key= lambda i: zdistances[i]) # find the closest corner to the camera


        # calculating positions of and drawing cubes faces to screen

        # indexes of corners of each face
        
        faces = [[4,5,6,7], # +z
                 [1,2,6,5], # +x
                 [0,1,2,3], # -z
                 [0,3,7,4], # -x
                 [2,3,7,6], # +y
                 [0,1,5,4]] # -y

        # depending on which corner is closest to the camera, the 3 faces touching it are drawn

        shown = [[0,1,4],
                 [3,0,4],
                 [3,0,5],
                 [0,1,5],
                 [1,2,4],
                 [2,3,4],
                 [2,3,5],
                 [1,2,5]][closest_index]

        # different fill characters provide a different shade to each face

        shade =  ['&','{','=','}','.','@']
        

        for face_index in shown:

            face_corners  = faces[face_index]
            face_shade    = shade[face_index]

            corner_coords = [corners[x] for x in face_corners]

            # calculating the bounding lines of each face on the drawing plane

            upper_lines = [] # stores upper bounding lines
            lower_lines = [] # stores lower bounding lines

            # corner_coords_wrap sticks the first 2 corners onto the end of the list

            corner_coords_wrap = corner_coords + corner_coords[0:2]

            # make_line function provides a local scope within which to define the lambda functions
            # representing the bounding lines
    
            def make_line(c1,c2):

                if c1[0] == c2[0]:

                    m = 1000 # high gradient assigned to avoid division by 0 error

                else:

                    m = (c2[1]-c1[1])/(c2[0]-c1[0]) # gradient = rise/run

                return lambda x: m * (x-c1[0]) + c1[1] 
            
            
            for i, corner in enumerate(corner_coords_wrap[:-2]):

                c1,c2,c3 = corner_coords_wrap[i:i+3] # picks out 3 corners               

                line = make_line(c1,c2) # create a line passing through c1 and c2

                # if c3 is above the line, add the line to lower lines, else add it to upper lines

                if line(c3[0]) < c3[1]:

                    lower_lines += [line]

                else:

                    upper_lines += [line]

                    
            # loop through each space in the vbuffer list to see if it is inside the bounding lines

            for y in range(self.h):

                for x in range(self.w):
                    

                    if min(y, upper_lines[0](x), upper_lines[1](x)) != y:

                        continue # if both upper lines arent above y, continue

                    if max(y, lower_lines[0](x), lower_lines[1](x)) != y:

                        continue # if both lower lines arent below y, continue
                    

                    self.vbuffer[y][x] = face_shade # set character in vbuffer to fill character
            
Cube()
