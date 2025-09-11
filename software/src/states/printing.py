from .state import State
class Printing(State):
      def __init__(self, *args, type=None):
        super().__init__(*args)
        self.type = type

      def on_enter(self, previous_state):
        print('Entering PRINTING state')
        if self.type == '12mm':
          self.device.left_illumination.pulsate(fromColor=(0, 0, 0), fromBrightness=0.0, toColor=(0, 255, 0), toBrightness=0.6)
        elif self.type == '16mm': 
          self.device.right_illumination.pulsate(fromColor=(0, 0, 0), fromBrightness=0.0, toColor=(0, 255, 0), toBrightness=0.6)

      def on_exit(self, next_state):
        print('Exiting PRINTING state')
        self.device.left_illumination.stop_pulsating()
        self.device.right_illumination.stop_pulsating()

