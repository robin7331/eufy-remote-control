from .state import State
class Idle(State):
      def __init__(self, *args):
        super().__init__(*args)

      def on_enter(self, previous_state):
        print('Entering IDLE state')
        self.device.left_illumination.pulsate(fromColor=(0, 255, 0), fromBrightness=0.2, toColor=(0, 255, 0), toBrightness=0.4)
        self.device.right_illumination.pulsate(fromColor=(0, 255, 0), fromBrightness=0.2, toColor=(0, 255, 0), toBrightness=0.4)

      def on_exit(self, next_state):
        print('Exiting IDLE state')
        self.device.left_illumination.stop_pulsating()
        self.device.right_illumination.stop_pulsating()
        self.device.left_illumination.clear_color()
        self.device.right_illumination.clear_color()  

      

