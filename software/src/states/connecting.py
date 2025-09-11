from .state import State
from .idle import Idle
from .error import Error

class Connecting(State):
      def __init__(self, *args):
        super().__init__(*args)

      def on_enter(self, previous_state):
        print('Entering CONNECTING state')
        self.device.left_illumination.pulsate(fromColor=(0, 0, 0), fromBrightness=0.0, toColor=(0, 0, 255), toBrightness=0.5)
        self.device.right_illumination.pulsate(fromColor=(0, 0, 0), fromBrightness=0.0, toColor=(0, 0, 255), toBrightness=0.5)

      def on_exit(self, next_state):
        print('Exiting CONNECTING state')
        self.device.left_illumination.stop_pulsating()
        self.device.right_illumination.stop_pulsating()
        self.device.left_illumination.clear_color()
        self.device.right_illumination.clear_color()  

      def to_idle(self):
          self.device.set_state(Idle(self.device))