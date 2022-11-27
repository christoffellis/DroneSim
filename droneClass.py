from tfClass import TransferFunction
from math import *
from random import *

yd = 0

positionHistory = [[[], [], []], [[], [], []]]


class Drone():
    def __init__(self, data, logHistory=False,):
        self.mass = .5

        self.dimensions = [0.1, 0.1, 0.05]

        self.position = [0, 0, 250]
        self.velocity = [0, 0, 0]
        self.acceleration = [0, 0, 0]   

        self.anglePosition = [0, 0, 0]
        self.angleVelocity = [0, 0, 0]
        self.angleAcceleration = [0, 0, 0]

        self.colour = (50 + randint(-50, 50), 235 + randint(-20, 20), 50 + randint(-50, 50))


        self.target = 0

        self.rotorDuty = [9.81 / (4 * 4) for i in range(4)]
        # print(self.rotorDuty[0])
        self.rotorStrength = [
            data["rotors"][0]["maxSpeed"],
            data["rotors"][1]["maxSpeed"],
            data["rotors"][2]["maxSpeed"],
            data["rotors"][3]["maxSpeed"]
        ]

        self.rotorGamma = [
            data["rotors"][0]["angle"],
            data["rotors"][1]["angle"],
            data["rotors"][2]["angle"],
            data["rotors"][3]["angle"]
        ]

        self.rotorArmLength = [
            data["rotors"][0]["armLength"],
            data["rotors"][1]["armLength"],
            data["rotors"][2]["armLength"],
            data["rotors"][3]["armLength"]
        ]

        self.tickSpeed = 0.1
        self.windDamping = 0.98

        self.logHistory = logHistory
        if self.logHistory:
            self.updatePositionHistory()

    @property
    def maxLift(self):
        val = 0
        for i in range(len(self.rotorStrength)):
            val += self.rotorStrength[i]
        return val

    def inertia(self, axis="x"):
        if axis == "x" or axis == "y":
            return self.mass * (self.dimensions[0] ** 2 + self.dimensions[2] ** 2) / 12

        if axis == "z":
            return self.mass * (self.dimensions[0] ** 2 + self.dimensions[1] ** 2) / 12


    def tick(self, height=1, angle=(0, 0, 0), hoops=[], time=0):

        distance1 = sqrt((hoops[self.target].position[0] - self.position[0]) ** 2 +
                         (hoops[self.target].position[1] - self.position[1]) ** 2 +
                         (hoops[self.target].position[2] - self.position[2]) ** 2)

        self.updateMovement()
        self.updateAngles()


        self.control(positionTarget=(0, 0, height), angleTarget=angle)

        if self.position[2] <= 0 and self.acceleration[2] < 0:
            self.acceleration[2] = 0
            self.velocity[2] = 0
            return -100

        angleAccel = sqrt(self.angleAcceleration[0] ** 2 + self.angleAcceleration[1] ** 2 + self.angleAcceleration[2] ** 2)



        distance2 = sqrt((hoops[self.target].position[0] - self.position[0]) ** 2 +
                        (hoops[self.target].position[1] - self.position[1]) ** 2 +
                        (hoops[self.target].position[2] - self.position[2]) ** 2)

        if distance1 < 12.5:

            self.target += 1
            if self.target >= len(hoops):
                self.target = 0
            return 25 * (self.target + 1) * (250 - time) / 250

        if self.logHistory:
            self.updatePositionHistory()
        #val = 50 / (distance2 * 100) + (distance1 - distance2) / 100
        val = (distance1 - distance2) / 100

        return val

    def updateMovement(self):
        rotorForce = 0
        for i in range(4):
            if self.rotorDuty[i] > 1:
                self.rotorDuty[i] = 1
            elif self.rotorDuty[i] < 0:
                self.rotorDuty[i] = 0
            rotorForce += self.rotorDuty[i] * self.rotorStrength[i]

        self.acceleration[2] = (-9.81 + rotorForce * cos(radians(self.anglePosition[1])) * cos(radians(self.anglePosition[0]))) / self.mass
        self.acceleration[1] = (rotorForce * cos(radians(self.anglePosition[2])) * sin(radians(self.anglePosition[0]))) / self.mass
        self.acceleration[0] = -(rotorForce * cos(radians(self.anglePosition[2])) * sin(radians(self.anglePosition[1]))) / self.mass


        for i in range(3):
            self.velocity[i] += self.acceleration[i] * self.tickSpeed
            self.velocity[i] *= self.windDamping
            self.position[i] += self.velocity[i] * self.tickSpeed
        if self.position[2] < 0:
            self.position[2] = 0

    def updateAngles(self):
        MxTotal = 0
        for i in range(4):
            MxTotal += self.rotorStrength[i] * self.rotorDuty[i] * sin(radians(self.rotorGamma[i])) * self.rotorArmLength[i]
        self.angleAcceleration[0] = MxTotal / self.inertia('x')

        MyTotal = 0
        for i in range(4):
            MyTotal += self.rotorStrength[i] * self.rotorDuty[i] * cos(radians(self.rotorGamma[i])) * \
                       self.rotorArmLength[i]
        self.angleAcceleration[1] = MyTotal / self.inertia('y')

        for i in range(3):
            self.angleVelocity[i] += self.angleAcceleration[i] * self.tickSpeed
            self.angleVelocity[i] *= self.windDamping
            self.anglePosition[i] += self.angleVelocity[i] * self.tickSpeed

    def control(self, positionTarget=(0, 0, 1), angleTarget=(0, 0, 0)):
        hc = self.hoverControl(positionTarget)

        for i in range(4):
            self.rotorDuty[i] = hc[i]

        rc = self.rollControl(angleTarget)
        for i in range(4):
            self.rotorDuty[i] += rc[i]

        pc = self.pitchControl(angleTarget)
        for i in range(4):
           self.rotorDuty[i] += pc[i]

        for i, duty in enumerate(self.rotorDuty):
            if duty < 0 or duty > 1:
                self.rotorDuty[i] = min(max(self.rotorDuty[i], 0), 1)

    def rollControl(self, angleTarget):
        global positionHistory
        u = (angleTarget[0] - self.anglePosition[0])
        kd = 12.26
        a = 6.467
        acc = u * kd - self.angleVelocity[0] * a

        #self.angleAcceleration[0] = acc

        back = [(self.inertia('x') * acc)/ (0.05 * sin(radians(45)) * 4 * 4) for _ in range(4)]
        back[2] *= -1
        back[3] *= -1


        return back

    def pitchControl(self, angleTarget):
        global positionHistory
        u = (angleTarget[1] - self.anglePosition[1])
        kd = 12.26
        a = 6.467
        acc = u * kd - self.angleVelocity[1] * a

        #self.angleAcceleration[0] = acc

        back = [(self.inertia('y') * acc)/ (0.05 * cos(radians(45)) * 4 * 4) for _ in range(4)]
        back[1] *= -1
        back[2] *= -1

        positionHistory[1].append(self.anglePosition[1])

        return back


    def hoverControl(self, positionTarget):
        u = (positionTarget[2] - self.position[2])

        acc = 7.04 * u - 3 * self.velocity[2]

        return [max(min((acc * self.mass + 9.81 * cosh(radians(self.anglePosition[0])) * cos(
            radians(self.anglePosition[1]))) / self.maxLift * ((self.maxLift/4)/ self.rotorStrength[i]) , 1), 0) for i in range(4)]

    def print(self):
        print("Pos:\t\t", self.position)
        print("Vel:\t\t", self.velocity)
        print("Acl:\t\t", self.acceleration)
        print("Duty:\t\t", self.rotorDuty)

    def updatePositionHistory(self):
        positionHistory[0][0].append([self.position[0], self.position[1], self.position[2]])
        positionHistory[0][1].append([self.velocity[0], self.velocity[1], self.velocity[2]])
        positionHistory[0][2].append([self.acceleration[0], self.acceleration[1], self.acceleration[2]])

        positionHistory[1][0].append(self.anglePosition)
        positionHistory[1][1].append(self.angleVelocity)
        positionHistory[1][2].append(self.angleAcceleration)