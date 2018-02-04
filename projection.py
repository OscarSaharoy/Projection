# Oscar Saharoy 2018

import sys,pygame,numpy

# Config

# Delcaring some numpy functions and constants to simplify code

cos    = lambda x: numpy.cos(x)
sin    = lambda x: numpy.sin(x)
tan    = lambda x: numpy.tan(x)
pi     = numpy.pi
matrix = numpy.matrix


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


def scale(factor):

	# Returns a matrix to scale a point by the given scale factor from the origin.

	scaling  = [[ factor,      0,      0 ],
				[      0, factor,      0 ],
				[      0,      0, factor ]]

	return matrix(scaling)


class Engine(object):

	def __init__(self):

		pygame.init()

		self.surface = pygame.display.set_mode((x_res,y_res)) # initialise window for drawing

		# Set favicon and title.

		pygame.display.set_caption(' Projection')

		icon = pygame.image.load(r'assets/cube.png')
		pygame.display.set_icon(icon)


		# self.pos is position of camera, self.view is the angle of viewing.

		self.pos     = matrix([[ -1500, 300, 0 ]])
		self.view    = matrix([[ 0.0, -0.2 ]])

		# self.cube is a list of points at the corner of a cube

		self.cube    = [( 100.0, 100.0, 100.0),
						( 100.0, 100.0,-100.0),
						( 100.0,-100.0, 100.0),
						( 100.0,-100.0,-100.0),
						(-100.0, 100.0, 100.0),
						(-100.0, 100.0,-100.0),
						(-100.0,-100.0, 100.0),
						(-100.0,-100.0,-100.0)]

		self.rotating = True # Variable to control rotation animation at startup.

		self.mainloop()


	def mainloop(self):

		while True:

			# test for exit request
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					sys.exit()

			self.surface.fill(white) # clear screen

			# game funtions
			self.pp = []
			for point in self.cube:
				self.draw(point)

			self.move()
			self.look()

			if self.rotating:
				self.rotate()

			# update screen and add delay
			pygame.display.flip()
			pygame.time.delay(delay)


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

		ar = self.view[0,0] # rotation angle of camera around y axis, used to calculate direction of movement

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

		self.pos = self.pos + delta # increment position by distance calculated


	def draw(self,point):

		# Project point

		dx  = point[0] - self.pos[0,0] # difference between point and camera x coordinate
		dy  = point[1] - self.pos[0,1] # y coordinate difference
		dz  = point[2] - self.pos[0,2] # z coordinate difference

		t_point   = numpy.matrix([[dx,dy,dz]])
		
		# Rotates point by camera angle of viewing

		rot_point = t_point * rot_y(self.view[0,0]) * rot_z(self.view[0,1])
		
		# Do nothing if point is behind camera

		if rot_point[0,0] <= 0:
			pass
		

		else:
		
			# Calculate extent of scaling to bring point onto the viewing plane, and scale it by that factor

			factor = f_len / rot_point[0,0]

			new_point = rot_point * scale(factor)

			# Add half of screen resolution to bring the point to the centre of the screen
			# Y coordinate becomes negative to account for down on screen being positive y

			fx,fy = [int(new_point[0,2]) + x_res//2, y_res//2 - int(new_point[0,1]) ]


			# Draws lines between all points on cube

			for point in self.pp:
	
				pygame.draw.aaline(self.surface,black,point,(fx,fy))
			
			self.pp += [(fx,fy)]

Engine()
