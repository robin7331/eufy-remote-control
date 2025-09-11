from states.connecting import Connecting
from states.error import Error
from states.idle import Idle
from states.connecting import Connecting
from states.printing import Printing
from states.timeout import Timeout
from states.stopping import Stopping

class Device:
    def __init__(self, left_illumination, right_illumination, tapper):
        self.state = None
        self.left_illumination = left_illumination
        self.right_illumination = right_illumination
        self.tapper = tapper

        self.last_state_class = None
        self.state = None

        self.set_state(Connecting(self))

    def is_idle(self):
        return isinstance(self.state, Idle)
    
    def is_error(self):
        return isinstance(self.state, Error)
    


    def set_state(self, state):
        last_state = self.state
        if last_state:
            self.last_state_class = last_state.__class__
            last_state.on_exit(state)
        self.state = state
        self.state.on_enter(last_state)

    def set_last_state(self):
      if self.last_state_class:
          self.set_state(self.last_state_class(self))

    def to_error(self, type=None):
        self.set_state(Error(self, type=type))

    def to_stopping(self, type=None):
        self.set_state(Stopping(self, type=type))

    def to_timeout(self):
        self.set_state(Timeout(self))

    def to_idle(self):
        self.set_state(Idle(self))

    def to_connecting(self):
        self.set_state(Connecting(self))
    
    def to_printing(self, type=None):
        self.set_state(Printing(self, type=type))

    def tick(self, tick_ms):
        self.state.tick(tick_ms)
