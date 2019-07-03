# Oscar Saharoy 2018

import sys, pygame, numpy, os
from pygame import gfxdraw

# Config

# Delcaring some numpy functions and constants to simplify code

cos    = lambda x: numpy.cos(x)
sin    = lambda x: numpy.sin(x)
tan    = lambda x: numpy.tan(x)
pi     = numpy.pi
matrix = numpy.matrix
array  = numpy.array


x_res  = 500 # Width of screen
y_res  = 500 # Height of screen

delay  = 16 # time between frames
fov    = pi/2
f_len  = x_res/tan(fov/2)


# Palette

white  = (255,255,255,255)
black  = (0,0,0,255)
leaf   = (30,255,30,255)
leaf1  = (25,205,25,255)
leaf2  = (20,170,20,255)
leaf3  = (15,130,15,255)
leaf4  = (12,100,12,255)


def rot_z(theta):

    # Returns a matrix to rotate a point by angle theta around z axis.

    rotation = [[ cos(theta), -sin(theta), 0 ],
                [ sin(theta),  cos(theta), 0 ],
                [          0,           0, 1 ]]

    return matrix(rotation)


def rot_x(theta):

    # Returns a matrix to rotate a point by angle theta around x axis.

    rotation = [[ 1,           0,           0 ],
                [ 0,  cos(theta), -sin(theta) ],
                [ 0,  sin(theta),  cos(theta) ]]

    return matrix(rotation)


def rot_y(theta):

    # Returns a matrix to rotate a point by angle theta around y axis.

    rotation = [[  cos(theta),  0, sin(theta) ],
                [            0, 1,          0 ],
                [ -sin(theta),  0, cos(theta) ]]

    return matrix(rotation)


def normalise(theta):

    # Code to keep theta between pi and -pi

    if  theta < -pi:
        theta += pi*2

    if  theta >  pi:
        theta -= pi*2

    return theta


class Face(object):

    # class to store faces of the cube

    def __init__(self, corners, fill=white):

        self.corners = corners
        self.fill    = fill

        self.matrix  = matrix(self.corners)


class Engine(object):

    def __init__(self):

        pygame.init()

        #pygame.display.gl_set_attribute(GL_DEPTH_SIZE, 16)

        self.surface = pygame.display.set_mode((x_res,y_res), pygame.DOUBLEBUF) # initialise window for drawing
        self.surface.convert_alpha()

        # Set favicon and title.

        pygame.display.set_caption(' Projection')

        # Set current directory
        dirname   = os.path.dirname(__file__)
        icon_path = os.path.join(dirname, r'assets/cube.png')

        # setting favicon
        icon = pygame.image.load(icon_path)
        pygame.display.set_icon(icon)

        # Stores number of ticks and frames since startup

        self.tick   = 0
        self.frames = 0


        # self.pos is position of camera, self.view is the angle of viewing.

        self.pos  = matrix([[ -1500, 300, 0 ]])
        self.view = matrix([[ 0.0, -0.2 ]])

        # self.cube is a list of faces of a cube

        self.cube  = [Face([ ( 100, 100, 100), ( 100, 100,-100), ( 100,-100,-100), ( 100,-100, 100) ], fill=leaf1), # front
 
                      Face([ (-100, 100, 100), (-100, 100,-100), (-100,-100,-100), (-100,-100, 100) ], fill=leaf3), # back
  
                      Face([ ( 100, 100,-100), (-100, 100,-100), (-100,-100,-100), ( 100,-100,-100) ], fill=leaf2), # left
 
                      Face([ (-100, 100, 100), ( 100, 100, 100), ( 100,-100, 100), (-100,-100, 100) ], fill=leaf2), # right

                      Face([ (-100, 100, 100), ( 100, 100, 100), ( 100, 100,-100), (-100, 100,-100) ], fill=leaf ), # top

                      Face([ (-100,-100, 100), ( 100,-100, 100), ( 100,-100,-100), (-100,-100,-100) ], fill=leaf4)] # bottom


        self.rotating = True # Variable to control rotation animation at startup.

        self.mainloop()


    def mainloop(self):

        while True:

            # Set number of ticks and frames

            self.tick    = pygame.time.get_ticks()
            self.frames += 1

            # test for exit request
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

            # game funtions

            if self.rotating:
                self.rotate()

            self.move()
            self.look()
            self.draw()

            # timing control:

            elapsed = pygame.time.get_ticks() - self.tick

            # If rendering last frame took lees time than delay, wait the remaining time
            # before next frame

            if elapsed < delay:

                pygame.time.delay(delay - elapsed)


    def rotate(self):

        # Rotation animation moves camera around the cube, looking at it.

        self.view[0,0] -= 0.01 # decrement angle of viewing

        ar       = self.view[0,0]

        # The x and y coordinates are 1500 times the coordinates of the unit circle where theta = ar.

        self.pos = matrix([[ -800 * cos(-ar), 150, -800 * sin(-ar) ]])

        # Code to keep viewing angle between pi and -pi

        self.view[0,0] = normalise(self.view[0,0])


    def look(self):

        # Controls camera movement

        pressed  = pygame.mouse.get_pressed()[0]
        movement = pygame.mouse.get_rel()

        if pressed: # only runs if mouse 1 is clicked

            self.rotating = False # Stops rotation animation

            # Increments viewing angles by 1/600th of mouse movement

            dr   = movement[0]/600.0
            de   = movement[1]/600.0

            self.view[0,0] += dr
            self.view[0,1] += de

            # Code to keep rotation angle between pi and -pi

            self.view[0,0] = normalise(self.view[0,0])

            # Code to keep elevation angle between pi/2 and -pi/2

            if  self.view[0,1] < -pi/2:
                self.view[0,1] = -pi/2

            if  self.view[0,1] > pi/2:
                self.view[0,1] = pi/2


    def move(self):

        # Controls movement

        pressed  = pygame.key.get_pressed() # list of keys, true if pressed else false for each key

        delta    = 0

        ar       = self.view[0,0] # rotation angle of camera around y axis, used to calculate direction of movement

        # Controls are WASD, Space and Shift

        if pressed[pygame.K_w]:
            delta += 10 * rot_y(-ar)

        if pressed[pygame.K_s]:
            delta += 10 * rot_y(-ar - pi)

        if pressed[pygame.K_SPACE]:
            delta += 10 * rot_z(-pi/2)

        if pressed[pygame.K_LSHIFT]:
            delta += 10 * rot_z(pi/2)

        if pressed[pygame.K_d]:
            delta += 10 * rot_y(-ar + pi/2)

        if pressed[pygame.K_a]:
            delta += 10 * rot_y(-ar - pi/2)

        self.pos = (self.pos + delta)[0] # increment position by distance calculated


    def draw(self):

        self.surface.fill(white) # clear screen

        projected_faces = []

        for face in self.cube:

            # translate face by camera coordinates

            translated_face  = face.matrix - self.pos

            # rotate by angle of viewing
    
            rotated_face     = translated_face * rot_y(self.view[0,0]) * rot_z(self.view[0,1])

            # calculate and multiply by scale factor needed to bring point onto projection plane
    
            scale_factors    = array( [ [f_len / point[0,0]] * 3 for point in rotated_face] )
    
            projected_points = array(rotated_face) * scale_factors

            # offset points into centre of screen - would be centred at 0,0 on screen otherwise

            offset           = array([[0, -y_res/2, x_res/2] for point in rotated_face])

            screen_points    = projected_points + offset

            # calculate x depth of face

            x_depth          = sum((array(rotated_face) * array(rotated_face)).sum(axis=1))

            # add face coords to list of faces with the x depth and fill colour

            projected_faces += [ [screen_points, x_depth, face.fill] ]

        # order faces by distance from camera

        projected_faces = sorted(projected_faces, key= lambda x: x[1], reverse=True)

        # draw faces

        for screen_points, x_depth, fill in projected_faces:

            # each point is added to the 'points' list before it is drawn

            points = []

            for x,y,z in screen_points:

                points += [(z,-y)]

            # draws the aapolygon then filled_polygon for smooth eadges and filled faces

            pygame.gfxdraw.aapolygon(self.surface, points, fill )
            pygame.gfxdraw.filled_polygon(self.surface, points, fill )

        # update screen

        pygame.display.flip()


Engine()
