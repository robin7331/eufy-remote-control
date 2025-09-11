from .state import State

class Stopping(State):
      def __init__(self, *args, type=None):
        super().__init__(*args)
        self.type = type
        
      def on_enter(self, previous_state):
        print('Entering STOPPING state')
        if self.type == '12mm':
          self.device.left_illumination.pulsate(fromColor=(0, 0, 0), fromBrightness=0.0, toColor=(255, 240, 66), toBrightness=0.8)
        else:
          self.device.right_illumination.pulsate(fromColor=(0, 0, 0), fromBrightness=0.0, toColor=(255, 240, 66), toBrightness=0.8)

      def on_exit(self, next_state):
        print('Exiting STOPPING state')
        self.device.left_illumination.stop_pulsating()
        self.device.right_illumination.stop_pulsating()
        self.device.left_illumination.clear_color()
        self.device.right_illumination.clear_color()


