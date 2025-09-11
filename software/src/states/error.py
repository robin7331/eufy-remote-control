from .state import State

class Error(State):
      def __init__(self, *args, type=None):
        super().__init__(*args)
        self.type = type
        
      def on_enter(self, previous_state):
        print('Entering ERROR state')
        if self.type == '12mm':
          self.device.left_illumination.pulsate(fromColor=(0, 0, 0), fromBrightness=0.0, toColor=(255, 0, 0), toBrightness=0.8)
        else:
          self.device.right_illumination.pulsate(fromColor=(0, 0, 0), fromBrightness=0.0, toColor=(255, 0, 0), toBrightness=0.8)

      def on_exit(self, next_state):
        print('Exiting ERROR state')
        self.device.left_illumination.stop_pulsating()
        self.device.right_illumination.stop_pulsating()
        self.device.left_illumination.clear_color()
        self.device.right_illumination.clear_color()


