class State:
    def __init__(self, device):
        self.device = device

    def on_enter(self, previous_state):
        pass

    def on_exit(self, next_state):
        pass
    
    def on_left_button_tap(self):
        pass
    
    def on_right_button_tap(self):
        pass
  
    def tick(self, tick_ms):
        pass
  
  