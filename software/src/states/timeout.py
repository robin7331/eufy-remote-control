from .state import State

class Timeout(State):
      def __init__(self, *args):
        super().__init__(*args)
        
      def on_enter(self, previous_state):
        print('Entering TIMEOUT state')
        self.device.left_illumination.pulsate(fromColor=(255, 0, 0), fromBrightness=0.2, toColor=(255, 0, 0), toBrightness=0.8)
        self.device.right_illumination.pulsate(fromColor=(255, 0, 0), fromBrightness=0.2, toColor=(255, 0, 0), toBrightness=0.8)

      def on_exit(self, next_state):
        print('Exiting TIMEOUT state')
        self.device.left_illumination.stop_pulsating()
        self.device.right_illumination.stop_pulsating()
        self.device.left_illumination.clear_color()
        self.device.right_illumination.clear_color()


