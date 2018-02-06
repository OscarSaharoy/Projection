# Oscar Saharoy 2018

import sys, pygame, numpy

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
fov    = pi/6
f_len  = x_res/tan(fov/2)


# Palette

white  = (255,255,255)
black  = (0,0,0)


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
				[	 		 0, 1,          0 ],
				[ -sin(theta),  0, cos(theta) ]]

	return matrix(rotation)


class Engine(object):

	def __init__(self):

		pygame.init()

		self.surface = pygame.display.set_mode((x_res,y_res)) # initialise window for drawing

		# Set favicon and title.

		pygame.display.set_caption(' Projection')

		icon = pygame.image.load(r'assets/cube.png')
		pygame.display.set_icon(icon)

		# Stores number of ticks and frames since startup

		self.tick   = 0
		self.frames = 0


		# self.pos is position of camera, self.view is the angle of viewing.

		self.pos  = matrix([[ -1500, 300, 0 ]])
		self.view = matrix([[ 0.0, -0.2 ]])

		# self.cube is a list of points at the corner of a cube

		self.cube = matrix([[ 100.0, 100.0, 100.0],
							[ 100.0, 100.0,-100.0],
							[ 100.0,-100.0, 100.0],
							[ 100.0,-100.0,-100.0],
							[-100.0, 100.0, 100.0],
							[-100.0, 100.0,-100.0],
							[-100.0,-100.0, 100.0],
							[-100.0,-100.0,-100.0]])

		#self.pairs = [(0,1),(0,2),(0,4),(1,3),(1,5),(2,3),(2,6),(3,7),(4,5),(4,6),(5,7),(6,7)]

		self.pairs = [ (x,y) for x in range(8) for y in range(x,8) ]

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

			self.surface.fill(white) # clear screen

			# game funtions

			self.project()
			self.move()
			self.look()

			if self.rotating:
				self.rotate()

			# update screen

			pygame.display.flip()

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

		self.pos = matrix([[ -1500 * cos(-ar), 300, -1500 * sin(-ar) ]])

		# Code to keep viewing angle between pi and -pi

		if  self.view[0,0] < -pi:
			self.view[0,0] =  pi

		if  self.view[0,0] >  pi:
			self.view[0,0] = -pi


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

			if  self.view[0,0] < -pi:
				self.view[0,0] =  pi

			if  self.view[0,0] >  pi:
				self.view[0,0] = -pi


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


	def project(self):

		# Translate cube so that the camera is at the origin.

		translated_cube  = self.cube - self.pos

		# Rotate cube by the angle of the camera.

		rotated_cube     = translated_cube * rot_y(self.view[0,0]) * rot_z(self.view[0,1])

		# Calculate scale factor for each point to scale it onto the projection plane.
		# * 3 is necessary so that each coordinate of each point (3 for each) is scaled.

		scale_factors    = array( [ [f_len / point[0,0]] * 3 for point in rotated_cube] )

		# Scale points by sacle factor.

		projected_points = array(rotated_cube) * scale_factors


		# Draw lines between points of cube.

		offset = array([0, -y_res/2, x_res/2])

		for first, second in self.pairs:

			if rotated_cube[first,0] < 5 or rotated_cube[second,0] < 5:

				continue # dont draw line if either point is behind the camera

			# Offset the points into centre of screen, otherwise they would be centered at 0,0 which is the
			# top left corner.

			x1,y1,z1 = projected_points[first]  + offset
			x2,y2,z2 = projected_points[second] + offset

			pygame.draw.aaline(self.surface, black, (z1,-y1), (z2,-y2) )

Engine()
