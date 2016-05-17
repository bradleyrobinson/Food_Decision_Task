import time


# This class is only for Windows! Uses time.clock, which functions differently on UNIX systems
class stimTime:
    def __init__(self):
        # This variable should be changed each time a new stimulus is presented using stim_start()
        self.start = time.clock()
        self.end = time.clock()+.005

    # Make sure this starts everytime a stimuli is presented
    def stim_start(self):
        self.start = time.clock()

    # when a valid key is pressed, this function should be called!
    def stim_end(self):
        self.end = time.clock()

    # This gives us the RT so we can record it in the data later on
    def get_rt(self):
        rt = (self.end - self.start) * 1000
        if rt > 0:
            return rt
        else:
            raise TimeError(rt, "Stimulus end time is before begin time, stimulus was not set properly")


# If the time is negative, this is a problem! It's impossible to go back in time in an experiment,
# so this exception should be thrown
class TimeError(Exception):
    def __init__(self, time, msg):
        self.time = time
        self.msg = msg

    def __str__(self):
        return self.time, self.msg


