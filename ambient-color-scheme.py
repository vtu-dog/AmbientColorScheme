import sublime
import threading
import ctypes
import os

NAMESPACE = 'AmbientColorScheme'
# importing the shared sensor library
path = os.path.dirname(os.path.realpath(__file__))
dll = ctypes.cdll.LoadLibrary(path + '/lib/lmulib.so')

# initialize global variables used throughout the program
settings = None
cancel_thread = None
light_scheme_set = None
current_timeout = 0


def plugin_loaded():
    """
    Called when the plugin is loaded, used to:
    - load the settings
    - set callbacks for setting changes
    - run the first thread
    """
    global settings, cancel_thread
    settings = sublime.load_settings(NAMESPACE + '.sublime-settings')
    options = [
        'disabled', 'light_color_scheme', 'dark_color_scheme',
        'threshold', 'refresh_rate', 'cycle_timeout'
    ]

    # reload settings when they are changed
    list(map(lambda aux: settings.add_on_change(aux, lambda: reload_settings()), options))

    # run the first thread if the user didn't disable the program explicitly
    if settings.get('disabled') is False:
        cancel_thread = start_thread()


def plugin_unloaded():
    """
    Called when the plugin is about to exit, kills the sensor daemon
    """
    if cancel_thread is not None:
        cancel_thread()


def reload_settings():
    """
    Reloads settings and stops the sensor daemon if necessary
    """
    global settings, cancel_thread

    # cancel the thread if the settings say so
    if cancel_thread is None:
        if settings.get('disabled') is False:
            cancel_thread = start_thread()
    else:
        if settings.get('disabled') is True:
            light_scheme_set = None
            current_timeout = 0
            cancel_thread()
            cancel_thread = None


def start_thread():
    return call_repeatedly(settings.get('refresh_rate'), read_sensor_data, {})


def call_repeatedly(interval, function, args):
    """
    Repeatedly calls a function with a set interval and returns a thread cancel handle
    """
    stopped = threading.Event()

    def loop():
        while not stopped.wait(interval):
            function(**args)

    threading.Thread(target=loop).start()

    # return the thread closing handle
    return stopped.set


def read_sensor_data():
    """
    Reads the light sensor data and changes user's color scheme if the reading is above a threshold
    """
    global light_scheme_set, current_timeout

    # prevents very rapid changes of the color scheme
    if current_timeout is not 0:
        current_timeout -= 1
        return
    else:
        # call the shared library's sensor code
        reading = dll.readSensor()
        scheme = None

        # check if the scheme needs to be changed
        if reading >= settings.get('threshold') and light_scheme_set is not True:
            scheme = settings.get('light_color_scheme')
            light_scheme_set = True

        elif reading < settings.get('threshold') and light_scheme_set is not False:
            scheme = settings.get('dark_color_scheme')
            light_scheme_set = False

        # change user settings
        if scheme is not None:
            global_settings = sublime.load_settings('Preferences.sublime-settings')
            if global_settings.get('color_scheme') != scheme:
                global_settings.set('color_scheme', scheme)
                sublime.save_settings('Preferences.sublime-settings')
                current_timeout = settings.get('cycle_timeout')
