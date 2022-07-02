# -*- coding: utf-8 -*-
"""Extra_HA3_3_Dergunov_VA.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1JPnnbEo_RO56Qq-tqjny1yLHPF8hnVqw
"""

import threading
import random
import time

N = 5

class Philosopher(threading.Thread):
    running = True  #used to check if everyone is finished eating


    def __init__(self, index, leftChopstick, rightChopstick):
        threading.Thread.__init__(self)
        self.index = index
        self.leftChopstick = leftChopstick
        self.rightChopstick = rightChopstick

    def run(self):
        while(self.running):
            # Philosopher is thinking
            print ('Philosopher %s started thinking.' % self.index)
            time.sleep(random.random() * 5)  # think 0-5 seconds
            print ('Philosopher %s finished thinking.' % self.index)
            self.eat()

    def eat(self):
        # if both the semaphores(chopsticks) are free, then philosopher will eat
        chopstick1, chopstick2 = self.leftChopstick, self.rightChopstick
        while self.running:
            chopstick1.acquire() # wait operation on left chopstick
            locked = chopstick2.acquire(False) 
            if locked: break #if right chopstick is not available leave left chopstick
            chopstick1.release()
        else:
            return
        self.eating()
        #release both the chopsticks after eating
        chopstick2.release()
        chopstick1.release()
 
    def eating(self):			
        print ('Philosopher %s starts eating. '% self.index)
        time.sleep(random.random() * 5)  # eat 0-5 seconds
        print ('Philosopher %s finishes eating and leaves to think.' % self.index)

def main():
    chopsticks = [threading.Semaphore() for n in range(N)] #initialising array of semaphore i.e chopsticks

    #here (i+1)%5 is used to get right and left chopsticks circularly between 1-5
    philosophers= [Philosopher(i, chopsticks[i%N], chopsticks[(i+1)%N])
            for i in range(N)]

    Philosopher.running = True
    for p in philosophers: p.start()
    time.sleep(100)
    Philosopher.running = False
    print ("Now we're finishing.")
 

if __name__ == "__main__":
    main()
