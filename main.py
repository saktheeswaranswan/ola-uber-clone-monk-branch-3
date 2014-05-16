#!/usr/bin/python
import kivy
kivy.require('1.8.0')
from time import time
from Queue import Queue, Empty
from kivy.app import App
from kivy.uix.label import Label
from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty, BooleanProperty,\
  ListProperty
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.actionbar import ActionBar
from kivy.uix.button import Button
from kivy.uix.label import Label
from olalistener import OLAListener, UIEvent


class MainScreen(Screen):
  pass

class PatchingScreen(Screen):
  pass

class ConsoleScreen(Screen):
  pass

class RDMSettingsScreen(Screen):
  pass

class RDMTestsScreen(Screen):
  pass

class RPiUI(App):
  """Class for drawing and handling the Kivy application itself."""
  EVENT_POLL_INTERVAL = 1 / 20
  index = NumericProperty(-1)
  time = NumericProperty(0)
  current_title = StringProperty()
  screen_names = ListProperty([])

  def build(self):
    """Initializes the user interface and starts timed events."""
    #TODO: Reorganize and consolidate; make necessary helper functions
    self.title = 'Open Lighting Architecture'
    self.ui_queue = Queue()
    self.ola_listener = OLAListener(self.ui_queue)
    self.ola_listener.start()
    self.layout = BoxLayout(orientation='vertical')
    #ActionBar creation and layout placing
    self.ab = ActionBar()
    self.layout.add_widget(self.ab)
    #Screen creation and layout placing
    self.sm = ScreenManager(transition=SlideTransition())
    self.devsets = MainScreen(name='Device Settings')
    self.sm.add_widget(self.devsets)
    self.sm.add_widget(PatchingScreen(name='Device Patching'))
    self.sm.add_widget(ConsoleScreen(name='DMX Console'))
    self.sm.add_widget(RDMSettingsScreen(name='RDM Settings'))
    self.sm.add_widget(RDMTestsScreen(name='RDM Tests'))
    self.layout.add_widget(self.sm)
    self.screens = {}
    self.available_screens = ['Device Settings','Device Patching',
      'DMX Console', 'RDM Settings', 'RDM Tests']
    self.screen_names = self.available_screens
    self.go_next_screen()
    Clock.schedule_interval(lambda dt: self.display_tasks(),
                            self.EVENT_POLL_INTERVAL)
    Clock.schedule_interval(self._update_clock, 1 / 60.)
    return self.layout

  def on_pause(self):
    return True

  def on_resume(self):
    pass

  def set_ola_status(self, text_string):
    self.devsets.ids.olad_status.text = text_string

  def display_tasks(self):
    """Polls for events that need to update the UI, 
       then updates the UI accordingly.
    """
    try:
      event = self.ui_queue.get(False)
      event.run()
      self.display_tasks()
    except Empty:
      pass

  def display_universes(self):
    """Makes a call to fetch the active universes; then put them in the
       UI queue to be handled by display_universes_callback.
    """
    self.ola_listener.pull_universes(self.display_universes_callback)

  def display_universes_callback(self, status, universes):
    """Updates the user interface with the active universes.

       Args:
         status: RequestStatus object indicating whether the request
                 was successful
         universes: A list of Universe objects
    """
    universe_names = [uni.name for uni in universes]
    def uni_to_string(a,b):
        return '{}\n{}'.format(a,b)
    uni_string = reduce(uni_to_string, universe_names, '')
    self.devsets.ids.universes.text = uni_string

  def go_previous_screen(self):
    """Changes the UI to view the screen to the left of the current one"""
    self.index = (self.index - 1) % len(self.available_screens)
    SlideTransition.direction = 'right'
    self.sm.current = self.screen_names[self.index]
    self.current_title = self.screen_names[self.index]

  def go_next_screen(self):
    """Changes the UI to view the screen to the right of the current one"""
    self.index = (self.index + 1) % len(self.available_screens)
    SlideTransition.direction = 'left'
    self.sm.current = self.screen_names[self.index]
    self.current_title = self.screen_names[self.index]

  def _update_clock(self, dt):
    self.time = time()

  def olad_listen(self, dt):
    self.ola_listener.listen(self)

if __name__ == '__main__':
    RPiUI().run()
