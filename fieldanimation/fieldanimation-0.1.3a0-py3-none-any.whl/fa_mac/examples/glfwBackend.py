from abc import ABCMeta, abstractmethod
import numpy as np
import glfw
glfw.ERROR_REPORTING = True
import OpenGL.GL as gl

actionMap = {glfw.PRESS: 'press',
             glfw.RELEASE: 'release',
             glfw.REPEAT: 'repeat'}

#------------------------------------------------------------------------------
def glInfo():
    """ Return OpenGL information dict
        WARNING: OpenGL context MUST be initialized !!!

        Args:
            None

        Returns:
            OpenGL information dict
    """
    try:
        glcontext = glfw.get_current_context()
    except glfw.GLFWError:
        try:
            glfw.init()
            glfw.window_hint(glfw.VISIBLE, False)
            glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
            glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
            glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)
            glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
            window = glfw.create_window(100, 100, '', None, None)
            glfw.make_context_current(window)
        except:
            return None
        else:
            wasInitialized = False
    else:
        wasInitialized = True
    major = gl.glGetIntegerv(gl.GL_MAJOR_VERSION)
    minor = gl.glGetIntegerv(gl.GL_MINOR_VERSION)
    version = gl.glGetString(gl.GL_VERSION)
    vendor = gl.glGetString(gl.GL_VENDOR)
    renderer = gl.glGetString(gl.GL_RENDERER)
    glsl = gl.glGetString(gl.GL_SHADING_LANGUAGE_VERSION)
    glversion = float("%d.%d" % (major, minor))
    retval = {
            'glversion': glversion,
            'version': version,
            'vendor': vendor,
            'renderer': renderer,
            'glsl': glsl,
            }
    if glversion >= 4.3:
        count = np.zeros(3, dtype=np.int32)
        size = np.zeros(3, dtype=np.int32)
        count[0] = gl.glGetIntegeri_v(gl.GL_MAX_COMPUTE_WORK_GROUP_COUNT, 0)[0]
        count[1] = gl.glGetIntegeri_v(gl.GL_MAX_COMPUTE_WORK_GROUP_COUNT, 1)[0]
        count[2] = gl.glGetIntegeri_v(gl.GL_MAX_COMPUTE_WORK_GROUP_COUNT, 2)[0]
        size[0] = gl.glGetIntegeri_v(gl.GL_MAX_COMPUTE_WORK_GROUP_SIZE, 0)[0]
        size[1] = gl.glGetIntegeri_v(gl.GL_MAX_COMPUTE_WORK_GROUP_SIZE, 1)[0]
        size[2] = gl.glGetIntegeri_v(gl.GL_MAX_COMPUTE_WORK_GROUP_SIZE, 2)[0]
        retval['maxComputeWorkGroupCount'] = count
        retval['maxComputeWorkGroupSize'] = size
    if not wasInitialized:
        glfw.terminate()
    print("retval=%s" % retval)
    return retval

#------------------------------------------------------------------------------
def errorCallback(error, description):
    print('Error %s, %s' % (error, description))

#==============================================================================
class glfwApp(metaclass=ABCMeta):

    KEY_G = glfw.KEY_G
    KEY_N = glfw.KEY_N
    KEY_F = glfw.KEY_F
    PRESS = glfw.PRESS
    RELEASE = glfw.RELEASE

    def __init__(self, title='', width=800, height=600, resizable=True):
        """ Create a new glfwApp instance.

            Args:
                title (string): window title
                width (integer): window width in pixels
                height (integer): window height in pixels
                resizable (bool): if True the window can be resized
        """
        self._width = width
        self._height = height
        self._title = title
        self.bg_color = (0.0, 0.0, 0.0, 0.0)

        glfw.set_error_callback(errorCallback)
        if not glfw.init():
            raise SystemExit("Error initializing GLFW")
        if resizable:
            glfw.window_hint(glfw.RESIZABLE, gl.GL_TRUE)
        else:
            glfw.window_hint(glfw.RESIZABLE, gl.GL_FALSE)
        # Create the window
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        self._window = glfw.create_window(self._width, self._height,
                self._title, None, None)
        glfw.make_context_current(self._window)
        #glfw.set_window_size_callback(self._window, self.onResize)
        glfw.set_framebuffer_size_callback(self._window, self.onResize)

        if not self._window:
            glfw.terminate()
            raise SystemExit

        glfw.make_context_current(self._window)
        glfw.set_key_callback(self._window, self.onKeyboard)
        self.fwidth, self.fheight = glfw.get_framebuffer_size(self._window)
        gl.glViewport(0, 0, self.fwidth, self.fheight)


    def restoreKeyCallback(self):
        glfw.set_key_callback(self._window, self.onKeyboard)

    @abstractmethod
    def onResize(self, window, width, height):
        """ This method must be implemened. It is called automatically when
            the window gets resized.

            Args:
                window (class:`glfw.LP__GLFWwindow` instance): window
                width (int): window width in pixels
                height (int): window height in pixels
        """
        pass

    def onKeyboard(self, window, key, scancode, action, mode):
        """ Process keybord input. This method is called automatically when
            the user interacts with the keyboard.

            Args:
                window (class:`glfw.LP__GLFWwindow` instance): window
                key (integer): the key that was pressed
                scancode (integer):
                action (integer): PRESS, RELEASE, REPEAT
                mode (integer): modifier
        """
        if key in (glfw.KEY_ESCAPE, glfw.KEY_Q):
            glfw.set_window_should_close(self._window, 1)
        glfw.poll_events()

    def window(self):
        """ Return the window instance

            Returns:
                the window instance
        """
        return self._window

    def title(self):
        """ Return window title

            Returns:
                the window title
        """
        return self._title

    def setTitle(self, title):
        """ Set window title

            Args:
                title (string): the new window title
        """
        glfw.set_window_title(self._window, title)

    def run(self):
        """ Start the application main loop
        """
        while not glfw.window_should_close(self._window):
            gl.glClearColor(*self.bg_color)
            glfw.poll_events()
            self.renderScene()
            glfw.swap_buffers(self._window)

        self.close()

    def close(self):
        """ Destroy the window and terminate glfw
        """
        glfw.destroy_window(self._window)
        glfw.terminate()

    def renderScene(self):
        """ Render the scene. This method is called automatically in the run
            loop
        """
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

if __name__ == "__main__":
    app = glfwApp('glfwApp')
    app.run()

