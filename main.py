import os.path
import random
import time

import neat.config
import pygame, sys
from math import *
import json
import matplotlib.pyplot as plt  # Import the matplotlib module
from droneClass import Drone, positionHistory
from hoopClass import hoop

# from graphicsHandler import GraphicsHandler

# game initialization
pygame.init()
size = (900, 600)
screen = pygame.display.set_mode(size, 0, pygame.DOUBLEBUF | pygame.HWSURFACE)
pygame.display.set_caption('Drone Sim')

viewThetaAngle = 60  # angle at which we look at from XY plane
viewPhiAngle = 60  # angle at which we look at around Z
zoomMultiplier = 1


def loadJsonData():
    with open('config.json') as f:
        return json.load(f)


data = loadJsonData()


def drawDrone(screen, drone):
    points = []
    length = 100 * zoomMultiplier

    for i in range(45, 405, 360 // 4):
        points.append([
            length * cos(radians(i)) + drone.position[0] * zoomMultiplier,
            length * sin(radians(i)) + drone.position[1] * zoomMultiplier,
            -drone.position[2] * zoomMultiplier
        ])

    newPoints = []
    for point in points:
        newPoints.append(transformTo2D(rotateIn3D((0,0,0), point))) #drone.anglePosition, point)))

    for i, point in enumerate(newPoints):
        points[i] = [point[0], point[1]]

    pygame.draw.polygon(screen, (25, 255, 25), points)

    linePoint1 = transformTo2D(rotateIn3D(drone.anglePosition,
                                          [drone.position[0] * zoomMultiplier, drone.position[1] * zoomMultiplier,
                                           -drone.position[2] * zoomMultiplier]))
    linePoint2 = transformTo2D(rotateIn3D(drone.anglePosition, [length + drone.position[0] * zoomMultiplier,
                                                                drone.position[1] * zoomMultiplier,
                                                                -drone.position[2] * zoomMultiplier]))

    pygame.draw.line(screen, (255, 255, 255), linePoint1, linePoint2)


def drawShadow(screen, drone):
    points = []
    length = 100 * zoomMultiplier
    for i in range(45, 405, 360 // 4):
        points.append([
            length * cos(radians(i)) + drone.position[0] * zoomMultiplier,
            length * sin(radians(i)) + drone.position[1] * zoomMultiplier,
            0
        ])
    newPoints = []
    for point in points:
        threeD = rotateIn3D(drone.anglePosition, point)
        threeD[2] = 0
        newPoints.append(transformTo2D(threeD))

    for i, point in enumerate(newPoints):
        points[i] = [point[0], point[1]]

    pygame.draw.polygon(screen, (156, 30, 30), points)


def drawEnvironment(screen, drone):
    points = []
    length = 1000 * zoomMultiplier
    for i in range(0, 360, 360 // 4):
        points.append([
            length * cos(radians(i)),
            length * sin(radians(i)),
            0
        ])
    newPoints = []
    for point in points:
        threeD = rotateIn3D([0, 0, 0], point)
        threeD[2] = 0
        newPoints.append(transformTo2D(threeD))

    pygame.draw.polygon(screen, (255, 25, 25), newPoints)


def transformTo2D(point):
    x = point[0] * cos(radians(viewPhiAngle)) - point[1] * sin(radians(viewPhiAngle)) + size[0] // 2
    y = (point[0] * sin(radians(viewPhiAngle)) + point[1] * cos(radians(viewPhiAngle))) * cos(radians(viewThetaAngle)) + \
        point[2] * sin(radians(viewThetaAngle)) + size[1] // 2
    return [x, y]


def rotateIn3D(anglePosition, position):
    c = radians(anglePosition[0])
    b = radians(anglePosition[1])
    a = radians(anglePosition[2])  # + viewPhiAngle)
    x = position[0]
    y = position[1]
    z = position[2]
    newX = x * cos(b) * cos(a) - y * cos(b) * sin(a) + z * sin(b)

    newY = x * (sin(c) * sin(b) * cos(a) + cos(c) * sin(a)) + y * (
            cos(c) * cos(a) - sin(c) * sin(b) * sin(a)) - z * sin(c) * cos(b)

    newZ = x * (sin(c) * sin(a) - cos(c) * sin(b) * cos(a)) + y * (
            cos(c) * sin(b) * sin(a) + sin(c) * cos(a)) + z * cos(c) * cos(b)

    return [newX, newY, newZ]

def add3D(point, position):
    for i in range(3):
        point[i] += position[i]

    return point


def writeText(screen, string, coordx, coordy, fontSize, colour, center=True, background=None):
    # set the font to write with
    font = pygame.font.SysFont('calibri', fontSize)
    if background == None:
        # (0, 0, 0) is black, to make black text
        text = font.render(string, True, colour)
    else:
        text = font.render(string, True, colour, background)
    # get the rect of the text
    textRect = text.get_rect()
    # set the position of the text
    if center:
        textRect.center = (coordx, coordy)
    else:
        textRect.topleft = (coordx, coordy)
    screen.blit(text, textRect)


def drawInfoDialog(position, screen):
    width, height = (size[0] * 0.25, size[1])
    infoScreen = pygame.Surface(size)
    infoScreen.set_alpha(178)

    infoScreen.fill((35, 35, 35))

    graphHeight = height / 3 * .7

    for i in range(1, 4):
        centerY = height / 3 * i - graphHeight * 0.75
        pygame.draw.line(infoScreen, (255, 255, 255), (width * 0.1, centerY - graphHeight * 0.5),
                         (width * 0.1, centerY + graphHeight * 0.5))
        pygame.draw.line(infoScreen, (255, 255, 255), (width * 0.1, centerY), (width * 0.9, centerY))

        pointsX = []
        pointsY = []
        pointsZ = []
        for j in range(max(-int(width * 0.8), -len(positionHistory[0][i - 1])), 0):
            pointsX.append((j + width * 0.9, centerY - positionHistory[0][i - 1][j][0] // 1))
            pointsY.append((j + width * 0.9, centerY - positionHistory[0][i - 1][j][1] // 1))
            pointsZ.append((j + width * 0.9, centerY - positionHistory[0][i - 1][j][2] // 1))

        pygame.draw.lines(infoScreen, (75, 65, 255), False, pointsX, width=2)
        pygame.draw.lines(infoScreen, (65, 255, 75), False, pointsY, width=2)
        pygame.draw.lines(infoScreen, (255, 75, 65), False, pointsZ, width=2)

        writeText(infoScreen, "Position", width // 2, height // 3 // 2 * .3 - 12, center=True, fontSize=12,
                  colour=(255, 255, 255))
        writeText(infoScreen, "Velocity", width // 2, height // 3 + 12, center=True, fontSize=12,
                  colour=(255, 255, 255))
        writeText(infoScreen, "Acceleration", width // 2, 2 * height // 3 + 12, center=True, fontSize=12,
                  colour=(255, 255, 255))

    screen.blit(infoScreen, (position, 0))


def drawTargetLine(drone):
    targetPos = hoops[drone.target].position
    pos = transformTo2D(
        (
            targetPos[0] * zoomMultiplier,
            targetPos[1] * zoomMultiplier,
            -targetPos[2] * zoomMultiplier,
        )
    )

    dronePos = transformTo2D(rotateIn3D(drone.anglePosition,
                                        [drone.position[0] * zoomMultiplier, drone.position[1] * zoomMultiplier,
                                         -drone.position[2] * zoomMultiplier]))
    pygame.draw.line(screen, (25, 25, 255), dronePos, pos, width=2)


hoops = []


def genHoops():
    hoops.clear()
    hoopDistance = 1000

    '''
    for i in range(0, 360 * 8, 360 // 4):
        hoops.append(
            hoop(
                [
                    cos(radians(i)) * i / 7.5,
                    sin(radians(i)) * i / 7.5,
                    i + 200,
                ]
            ))
    '''
    angle = random.randint(0, 360)
    for i in range(100, 3000, 75):
        angle += random.randint(-5, 5)
        hoops.append(
            hoop((
                cos(radians(angle)) * i,
                sin(radians(angle)) * i,
                100
            )
            ))


def drawHoops(drone):
    for j, hoop in enumerate(hoops):
        pos = transformTo2D(
            (
                hoop.position[0] * zoomMultiplier,
                hoop.position[1] * zoomMultiplier,
                -hoop.position[2] * zoomMultiplier,
            )
        )

        pygame.draw.circle(screen, (25 + 100 * (j < drone.target), 25 + 100 * (j < drone.target), 255), pos,
                           int(7 * zoomMultiplier))

        if j < drone.target:
            pygame.draw.circle(screen, (50, 50, 255), pos, int(11 * zoomMultiplier), width=2)


def run(configPath):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                neat.DefaultStagnation, configPath)

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    p.add_reporter(neat.StatisticsReporter())

    winner = p.run(main, 50000)


showInfo = False
infoOffset = 0

counterLimit = 0


def main(genomes, config):
    drones = []
    ge = []
    nets = []

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        drones.append(Drone(data))
        g.fitness = 0
        ge.append(g)

    drones[0].logHistory = True

    global viewThetaAngle
    global viewPhiAngle
    global zoomMultiplier
    global showInfo
    global infoOffset
    global counterLimit

    targetHeight = 100
    pressHeightValue = 0

    pressPitchValue = 0
    pressRollValue = 0
    pressYawValue = 0

    changingAngle = 0

    startTime = time.time()
    screenshotCount = 0

    genHoops()
    counter = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    for plot in positionHistory:
                        plt.plot(plot)
                    plt.show()
                    pygame.quit()
                    sys.exit()

                if event.key == pygame.K_i:
                    showInfo = not showInfo

                if event.key == pygame.K_o:
                    pygame.image.save(screen, str(screenshotCount) + "_screenshot.jpg")
                    screenshotCount += 1

                if event.key == pygame.K_p:
                    changingAngle = (changingAngle + 1) % 3
                    print(changingAngle)

                if event.key == pygame.K_LSHIFT:
                    pressHeightValue += 1

                if event.key == pygame.K_LCTRL:
                    pressHeightValue -= 1

                if event.key == pygame.K_w:
                    pressPitchValue += 1

                if event.key == pygame.K_s:
                    pressPitchValue -= 1

                if event.key == pygame.K_a:
                    pressRollValue += 1

                if event.key == pygame.K_d:
                    pressRollValue -= 1

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LSHIFT:
                    pressHeightValue -= 1

                if event.key == pygame.K_LCTRL:
                    pressHeightValue += 1

                if event.key == pygame.K_a:
                    pressRollValue -= 1

                if event.key == pygame.K_d:
                    pressRollValue += 1

                if event.key == pygame.K_w:
                    pressPitchValue -= 1

                if event.key == pygame.K_s:
                    pressPitchValue += 1

            if event.type == pygame.MOUSEBUTTONDOWN:
                pygame.mouse.get_rel()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    zoomMultiplier *= 1.1
                elif event.button == 5:
                    zoomMultiplier /= 1.1

            if event.type == pygame.MOUSEMOTION and pygame.mouse.get_pressed(num_buttons=3)[0]:
                mousePos = pygame.mouse.get_rel()
                viewPhiAngle -= mousePos[0]

                viewPhiAngle = viewPhiAngle % 360
                viewThetaAngle += mousePos[1]

                if viewThetaAngle > 90:
                    viewThetaAngle = 90
                if viewThetaAngle < 0: viewThetaAngle = 0

        # game code here

        screen.fill((200, 240, 255))
        targetHeight += pressHeightValue
        if targetHeight < 0:
            targetHeight = 0

        for x, drone in enumerate(drones):
            tickVal = drone.tick(height=targetHeight,
                                 angle=(pressRollValue * -15, pressPitchValue * -15, pressYawValue * -15),
                                 hoops=hoops)

            if tickVal == -100:
                drones.pop(x)
                ge.pop(x)
                nets.pop(x)
            else:
                ge[x].fitness += tickVal

                output = nets[x].activate(
                    (
                        drone.position[0],
                        drone.position[1],
                        drone.position[2],
                        drone.velocity[0],
                        drone.velocity[1],
                        drone.velocity[2],
                        drone.acceleration[0],
                        drone.acceleration[1],
                        drone.acceleration[2],
                        drone.anglePosition[0],
                        drone.anglePosition[1],
                        drone.anglePosition[2],
                        drone.angleVelocity[0],
                        drone.angleVelocity[1],
                        drone.angleVelocity[2],
                        drone.angleAcceleration[0],
                        drone.angleAcceleration[1],
                        drone.angleAcceleration[2],
                        hoops[drone.target].position[0],
                        hoops[drone.target].position[1],
                        hoops[drone.target].position[2],
                        hoops[drone.target + 1].position[0],
                        hoops[drone.target + 1].position[1],
                        hoops[drone.target + 1].position[2],
                    )
                )

                drone.rotorDuty[0] += (output[4] + output[0] + output[2] + output[3]) / 100
                drone.rotorDuty[1] += (output[4] + output[1] + output[2] - output[3]) / 100
                drone.rotorDuty[2] += (output[4] - output[0] - output[2] - output[3]) / 100
                drone.rotorDuty[3] += (output[4] - output[1] - output[2] + output[3]) / 100

        if len(drones) > 0:
            if counterLimit % 5 == 0:
                drawEnvironment(screen, drones[0])
                drawShadow(screen, drones[0])
                for drone in drones:
                    drawDrone(screen, drone)
                drawHoops(drones[0])
                drawTargetLine(drones[0])
        else:
            break

        if showInfo:
            if infoOffset < size[0] * 0.25:
                infoOffset += 8
        elif infoOffset > 0:
            infoOffset -= 8

        if infoOffset > 0:
            drawInfoDialog(size[0] - infoOffset, screen)

        pygame.time.wait(100 // 60)
        counter += 1

        if counter > 250:
            counterLimit += 1
            break
        pygame.display.flip()


if __name__ == "__main__":
    dir = os.path.dirname(__file__)
    config_path = os.path.join(dir, "config.txt")
    run(config_path)
