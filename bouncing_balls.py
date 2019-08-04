
""" Acknowledgments to Dr Tom Cai, The University of Sydney who provided week 8's
    lab solution which was a guide to this program"""
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from PIL.Image import open
import numpy
import time
import random

# is an i.d number for the window object
window = 0
add_ball = False
textures = []
balls = []
# room dimensions
half_w = 2.0
half_h = 1.0
half_d = 2.0


class Ball:
    """ class for ball objects to shoot into playroom"""

    global textures
    global half_w, half_h, half_d
    ball_rad = 0.15

    def draw_ball(self):
        """ draws a ball on current frame """

        glBindTexture(GL_TEXTURE_2D, textures[self.texture_idx])
        # use automatically function generated coordinate systems for sphere texture mapping
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_TEXTURE_GEN_S)
        glEnable(GL_TEXTURE_GEN_T)
        glTexGeni(GL_S, GL_TEXTURE_GEN_MODE, GL_SPHERE_MAP)
        glTexGeni(GL_T, GL_TEXTURE_GEN_MODE, GL_SPHERE_MAP)
        glutSolidSphere(Ball.ball_rad, 10, 10)
        glDisable(GL_TEXTURE_GEN_S)
        glDisable(GL_TEXTURE_GEN_T)
        glDisable(GL_TEXTURE_2D)

    def __init__(self):
        """ initialise a ball object """

        # initiate random start velocities
        self.Vx = random.uniform(1.0, 5.0)
        self.Vy = random.uniform(1.0, 5.0)
        self.Vz = random.uniform(-1.0, -5.0)
        # initiate random start position and direction (x, y)
        self.x = random.uniform(-0.1, 0.1)
        if self.x <= 0.0:
            self.Vx = -self.Vx
        self.y = random.uniform(-0.1, 0.1)
        if self.y <= 0.0:
            self.Vy = -self.Vy
        self.z = 1.85

        # choose a random texture from pool
        self.texture_idx = random.randrange(0, len(textures))

        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        Ball.draw_ball(self)
        glPopMatrix()
        self.t_start = time.time()
        self.t_curr = 0.0
        self.t_elapse = 0.0
        self.acc_y = 0.0

    def move_ball(self):
        """ moves an object ball according to kinematic laws and playroom constraints.
            Returns Boolean False for object destruction when out of viewing range"""

        self.t_curr = time.time()
        self.t_elapse = self.t_curr - self.t_start
        self.t_start = self.t_curr
        self.acc_y = -9.8*self.t_elapse
        # motion in x plane
        # left wall boundary
        if self.x <= (-half_w + Ball.ball_rad):
            self.Vx = -self.Vx
            self.x = -half_w + Ball.ball_rad + self.Vx*self.t_elapse
        # right wall boundary
        elif self.x >= (half_w - Ball.ball_rad):
            self.Vx = -self.Vx
            self.x = half_w - Ball.ball_rad + self.Vx*self.t_elapse
        else:
            self.x += self.Vx*self.t_elapse
        # motion in y plane
        # floor boundary
        if self.y <= (-half_h + Ball.ball_rad):
            self.Vy = -self.Vy
            self.y = -half_h + Ball.ball_rad + self.Vy*self.t_elapse + 0.5*self.acc_y*(self.t_elapse**2)
        # ceiling boundary
        elif self.y >= (half_h - Ball.ball_rad):
            self.Vy = -self.Vy
            self.y = half_h - Ball.ball_rad + self.Vy*self.t_elapse + 0.5*self.acc_y*(self.t_elapse**2)
        else:
            self.Vy -= 9.8*self.t_elapse
            self.y += self.Vy*self.t_elapse + 0.5*self.acc_y*(self.t_elapse**2)
        # motion in z plane
        # notify ball not needed past viewing point
        if self.z > (half_d - Ball.ball_rad):
            return False
        # back wall boundary
        elif self.z <= (-half_d + Ball.ball_rad):
            self.Vz = -self.Vz
            self.z = -half_d + Ball.ball_rad + self.Vz*self.t_elapse
        else:
            self.z += self.Vz*self.t_elapse

        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        Ball.draw_ball(self)
        glPopMatrix()


def add_texture_to_pool(img, texture_index):
    """ converts param image to texture and adds to texture pool """

    global textures
    # remove Alpha channel if required (for .png files)
    if img.mode != "RGB":
        img = img.convert("RGB")
    # method of image data extraction taken from http://www.magikcode.com/?p=122
    img_data = numpy.array(list(img.getdata()), numpy.int8)
    glBindTexture(GL_TEXTURE_2D, textures[texture_index])
    # set pixel storage mode
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    # modes for s and t coordinate wrapping
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    # set filter functions
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    # set texture mode for texture environment (no lighting effects needed)
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
    # unpack texture
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img.size[0], img.size[1], 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
    img.close()


def load_textures():
    """ loads images and calls add_texture_to_pool() to create the pool. """

    global textures
    num_of_textures = 6
    count = 0
    textures = glGenTextures(num_of_textures)
    print("Loading Textures.\n-----------------")
    filename = "texture0.jpg"
    try:
        img = open(filename)
        add_texture_to_pool(img, count)
        count += 1
        print("%d of %d textures loaded\n........." % (count, num_of_textures))
    except IOError:
        print("Error opening " + filename)
    filename = "texture1.jpg"
    try:
        img = open(filename)
        add_texture_to_pool(img, count)
        count += 1
        print("%d of %d textures loaded\n........." % (count, num_of_textures))
    except IOError:
        print("Error opening " + filename)
    filename = "texture2.png"
    try:
        img = open(filename)
        add_texture_to_pool(img, count)
        count += 1
        print("%d of %d textures loaded\n........." % (count, num_of_textures))
    except IOError:
        print("Error opening " + filename)
    filename = "texture3.jpg"
    try:
        img = open(filename)
        add_texture_to_pool(img, count)
        count += 1
        print("%d of %d textures loaded\n........." % (count, num_of_textures))
    except IOError:
        print("Error opening " + filename)
    filename = "texture4.jpg"
    try:
        img = open(filename)
        add_texture_to_pool(img, count)
        count += 1
        print("%d of %d textures loaded\n........." % (count, num_of_textures))
    except IOError:
        print("Error opening " + filename)
    filename = "texture5.jpg"
    try:
        img = open(filename)
        add_texture_to_pool(img, count)
        count += 1
        print("%d of %d textures loaded\n........." % (count, num_of_textures))
    except IOError:
        print("Error opening " + filename)


def init_scene(width, height):
    # specify background colour of window after clearing of colour buffers RGBA
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClearDepth(1.0)
    # pixel drawn only if incoming depth value is less than stored depth value (for overlapping faces)
    glDepthFunc(GL_LESS)
    # enable depth test specified above
    glEnable(GL_DEPTH_TEST)
    glPolygonMode(GL_FRONT, GL_LINE)
    glPolygonMode(GL_BACK, GL_LINE)
    glShadeModel(GL_SMOOTH)
    # allows visualisation of variations in z coordinate with respect to viewing point
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    # 45 degree field view, aspect ratio, display range 0.1 to 100
    gluPerspective(45.0, float(width) / float(height), 0.1, 100.0)
    # define in terms of world coordinates view used also
    glMatrixMode(GL_MODELVIEW)


def resize_scene(width, height):
    """ Note this function was taken directly from lab wk 8 solution provided
        by Dr Tom Cai, The University of Sydney"""

    if height == 0:
        height = 1
    # change x-y coordinates to window x-y coordinates
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(width) / float(height), 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)


def draw_room():
    """ creates playroom according to global dimensions"""

    global half_w, half_d, half_h
    # multiply translation matrix by current matrix and store result as current matrix
    # i.e push whole coordinate system forward by 5
    glTranslatef(0.0, 0.0, -5.0)
    # begin defining shape (specified as quadrilateral. Defined by every 4 vertex points)
    glBegin(GL_QUADS)
    # ceiling
    glColor3f(0.75, 0.75, 0.75)
    glVertex3f(half_w, half_h, -half_d)
    glVertex3f(-half_w, half_h, -half_d)
    glVertex3f(-half_w, half_h, half_d)
    glVertex3f(half_w, half_h, half_d)
    # floor
    glColor3f(0.75, 0.75, 0.75)
    glVertex3f(half_w, -half_h, half_d)
    glVertex3f(-half_w, -half_h, half_d)
    glVertex3f(-half_w, -half_h, -half_d)
    glVertex3f(half_w, -half_h, -half_d)
    # Back wall
    glColor3f(0.25, 0.25, 0.25)
    glVertex3f(half_w, -half_h, -half_d)
    glVertex3f(-half_w, -half_h, -half_d)
    glVertex3f(-half_w, half_h, -half_d)
    glVertex3f(half_w, half_h, -half_d)
    # left wall
    glColor3f(0.5, 0.5, 0.5)
    glVertex3f(-half_w, half_h, half_d)
    glVertex3f(-half_w, half_h, -half_d)
    glVertex3f(-half_w, -half_h, -half_d)
    glVertex3f(-half_w, -half_h, half_d)
    # right wall
    glColor3f(0.5, 0.5, 0.5)
    glVertex3f(half_w, half_h, -half_d)
    glVertex3f(half_w, half_h, half_d)
    glVertex3f(half_w, -half_h, half_d)
    glVertex3f(half_w, -half_h, -half_d)

    glEnd()



def draw_scene():
    """ main glut display function that loops"""

    global add_ball, balls
    # clear buffers for new frame
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    draw_room()

    for ball in balls:
        if ball.move_ball() is False:
            balls.remove(ball)
            del ball
    if add_ball:
        balls.append(Ball())
        add_ball = False
    glutSwapBuffers()
    glutPostRedisplay()


def key_press(*args):
    """ provides escape sequence"""

    # if ANSI escape sequence ESC is pressed (b prefix for python3 conversion)
    if args[0] == b"\x1b":
        print("\nExiting.")
        exit()


def mouse_click(button, state, x, y):
    """ signals requirement for new ball based on user interaction"""

    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        global add_ball
        add_ball = True


def main():
    global window
    glutInit()
    # RGBA mode, double buffered, window with depth buffer
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(1200, 600)
    # set window position (where it opens)
    glutInitWindowPosition(0, 0)
    window = glutCreateWindow(b"Play Room")
    glutDisplayFunc(draw_scene)
    glutIdleFunc(draw_scene)
    glutReshapeFunc(resize_scene)
    glutKeyboardFunc(key_press)
    glutMouseFunc(mouse_click)
    init_scene(1200, 600)
    load_textures()
    print("Begin: Shoot balls with mouse click or Press ESC to exit. ")
    # enter glut event processing
    glutMainLoop()


main()
