import threading
from time import sleep
from Hoist import system

class job:
    
    #object to represent each job or rack being run through the tank line
    def __init__(self, ID, tankTimes, tankNums, movingqueue, system):
        self.tankTimes = tankTimes
        self. tankNums = tankNums
        self.jobID = ID
        self.moveQueue = movingqueue
        self.thread = None
        self.system = system
        
        self.currentTank = 0
        
    def _timer(self, seconds):
        print('Job ' + self.jobID + ' has been placed in tank ' + self.currentTank + ' for ' + self.seconds + ' seconds.')
        for i in range(seconds, 0, -1):
            time.sleep(1)
        print('Job ' + self.jobID + ' is finished.')
        self.moveQueue.append(self)
        
    def start_timer(self):
        self.thread = threading.Thread(target=self._timer)
        self.thread.join()
        
    def next_tank(self):
        return tankNums[currentTank + 1]

        
        
    
