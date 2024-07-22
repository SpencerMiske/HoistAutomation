import threading
from time import sleep

class job:
    
    #object to represent each job or rack being run through the tank line
    def __init__(self, ID, tankTimes, tankNums, movingqueue, endQueue, occupiedTanks):
        self.tankTimes = tankTimes
        self.tankNums = tankNums
        self.jobID = ID
        self.moveQueue = movingqueue
        self.thread = None
        self.occupiedTanks = occupiedTanks
        self.endQueue = endQueue
        
        self.currentTank = 0
        
    def _timer(self, seconds):
        print('Job ' + str(self.jobID) + ' has been placed in tank ' + str(self.tankNums[self.currentTank]) + ' for ' + str(seconds) + ' seconds.')
        for i in range(seconds, 0, -1):
            sleep(1)
        print('Job ' + str(self.jobID) + ' is finished.')
        self.moveQueue.append(self)
        
    def start_timer(self, seconds):
        if seconds != 'END':
            self.thread = threading.Thread(target=self._timer, args=(seconds,))
            self.thread.start()
        else:
            print(str(self.jobID) + ' is done treatment.')
            self.endQueue.append(self)
        
    def next_tank(self):
        return self.tankNums[self.currentTank + 1]
    
    def cantDo(self):
        temp = self.currentTank
        if (self.occupiedTanks[self.tankNums[temp +1]]) == 'X':
            return True
        else:
            return False
        
    #Serialization Methods
    


        
        
    
