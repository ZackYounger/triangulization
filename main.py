import pygame
from PIL import Image
import time
from copy import deepcopy
from random import randint as rand

scale = 5
image = Image.open("images/moana liza.jpg")
image = image.convert('RGB')
sizeY = 128
sizeFactor = sizeY / image.height
sizeX = round(image.width * sizeFactor)
image = image.resize((sizeX,sizeY))

pygame.init()

clock = pygame.time.Clock()
fps_limit = 30

white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
black = (0, 0, 0)
blue = (0, 0, 255)

background_colour = black

imgWidth, imgHeight = image.width, image.height
width, height = scale * image.width, scale * image.height
screen = pygame.display.set_mode((width, height))
# screen = pygame.display.set_mode((800,800))
screen.fill(background_colour)
print(imgWidth, imgHeight)
triangles = []


def sign(n):
    return n / abs(n) if n!=0 else 1


class Triangle:
    def __init__(self, points):
        self.points = points
        self.findEquations()

    def findEquations(self):
        mean = [sum(self.points[i][0] for i in range(3)) / 3,
                sum(self.points[i][1] for i in range(3)) / 3]
        #print(f'mean = {mean}')
        #c = (255,0,0)
        #for p in self.points:
        #    pygame.draw.circle(screen, black, [p[0]*scale,p[1]*scale], 5)
        #pygame.draw.circle(screen,black,[mean[0]*scale,mean[1]*scale],10)
        #pygame.display.flip()
        #time.sleep(2)
        #for p in self.points:
        #    pygame.draw.circle(screen, white, [p[0]*scale,p[1]*scale], 5)
        #pygame.draw.circle(screen,white,[mean[0]*scale,mean[1]*scale],10)
        self.equations = []
        for line in range(3):
            if self.points[line][1] == self.points[line - 1][1]:
                gradient = 0
            elif self.points[line][0] == self.points[line - 1][0]:
                gradient = 10**10 #doubt!!!
            else:
                gradient = (self.points[line][1] - self.points[line - 1][1]) / (
                            self.points[line][0] - self.points[line - 1][0])
            intercept = self.points[line][1] - gradient * self.points[line][0]
            tempSign = sign(mean[1] - gradient * mean[0] - intercept)
            #print(f"gradient = {gradient}")
            #print(f"tempsign = {tempSign, mean[1] - gradient * mean[0] - intercept}")
            self.equations.append({'gradient': gradient,
                                   'intercept': intercept,
                                   'sign': tempSign})


    def checkDuplicate(self):

        #for e in self.equations:
        #    if e['gradient'] == 10**10:
        #        print('weird line')
        global returnPoint
        global rgb
        # new triangle

        # sample lines
        gap = 5
        inspectionLength = 4
        maxColorChange = 0
        colorChangePos = [0, 0]

        for line in range(3):
            tempLine = []
            length = [round(self.points[line][0] - self.points[(line + 1) % 3][0]),
                      round(self.points[line][1] - self.points[(line + 1) % 3][1])]
            for point in range(max(length)):
                x, y = (round(self.points[(line + 1) % 3][0]) + length[0] * point / max(length),
                        round(self.points[(line + 1) % 3][1]) + length[1] * point / max(length))

                rgb = image.getpixel((min(x, imgWidth-1), min(y, imgHeight-1)))
                tempLine.append({'pos': [x, y], 'rgb': rgb})


                if inspectionLength + gap < point < max(length) - inspectionLength - gap:
                    delta = sum(abs(tempLine[point - inspectionLength]['rgb'][i] - tempLine[point]['rgb'][i]) for i in range(3))
                    if delta > maxColorChange:
                        maxColorChange = delta
                        colorChangePos = tempLine[round(point - inspectionLength/ 2)]['pos']
                        returnPoint = self.points[line - 1]




        xRange = [min(x[0] for x in self.points), max(x[0] for x in self.points)]
        yRange = [min(y[1] for y in self.points), max(y[1] for y in self.points)]

        #print('range = ', xRange, yRange)

        rC, gC, bC = 0, 0, 0  # count
        rC2, gC2, bC2 = 0, 0, 0
        count = 0

        for x in range(*xRange):
            for y in range(*yRange):
                point = [x, y]
                acceptPoint = 0
                for equation in self.equations:
                    if equation['sign'] < 0:
                        if point[1] < equation['gradient'] * point[0] + equation['intercept']:
                            acceptPoint += 1
                    else:
                        if point[1] > equation['gradient'] * point[0] + equation['intercept']:
                            acceptPoint += 1

                if acceptPoint == 3:
                    r, g, b = image.getpixel((x, y))

                    rC += r
                    gC += g
                    bC += b

                    rC2 += r**2
                    gC2 += g**2
                    bC2 += b**2

                    count += 1

            #    pygame.draw.rect(screen, white if acceptPoint == 3 else black, [point[0]*scale,point[1]*scale, scale, scale])
            #pygame.display.flip()

        if count > 0:
            rVar = (rC2 - rC) / count * count
            gVar = (gC2 - gC) / count * count
            bVar = (bC2 - bC) / count * count
        else:
            rVar = 0
            gVar = 0
            bVar = 0

        var = rVar + gVar + bVar

        return var, maxColorChange, colorChangePos, returnPoint


    def updateColor(self):
        xRange = [min(x[0] for x in self.points), max(x[0] for x in self.points)]
        yRange = [min(y[1] for y in self.points), max(y[1] for y in self.points)]

        #print('range = ',xRange,yRange)

        rC, gC, bC = 0, 0, 0  # count
        count = 0

        for x in range(*xRange):
            for y in range(*yRange):
                point = [x, y]
                acceptPoint = 0
                for equation in self.equations:
                    if equation['sign'] < 0:
                        if point[1] < equation['gradient'] * point[0] + equation['intercept']:
                            acceptPoint += 1
                    else:
                        if point[1] > equation['gradient'] * point[0] + equation['intercept']:
                            acceptPoint += 1

                if acceptPoint == 3:
                    rgb = image.getpixel((x, y))
                    rC += rgb[0]
                    gC += rgb[1]
                    bC += rgb[2]
                    count += 1

        if count > 0:
            rgb = [rC / count,
               bC / count,
               gC / count]
        else:
            rgb = [0,0,0]

        newpoints = []
        for point in self.points:
            newpoints.append([point[0] * scale, point[1] * scale])

        pygame.draw.polygon(screen, rgb, newpoints)


def roundList(x):
    return [round(x[0]), round(x[1])]

def area(p):
    p1 = p[0]
    p2 = p[1]
    p3 = p[2]
    return (0.5) * (p1[0]*(p2[1]-p3[1])+p2[0]*(p3[1]-p1[1])+p3[0]*(p1[1]-p2[1]))

maxTriangles = 400

triangles.append(Triangle([[0, 0], [0, imgHeight], [imgWidth, 0]]))
triangles[-1].updateColor()
triangles.append(Triangle([[0, imgHeight], [imgWidth, 0], [imgWidth, imgHeight]]))
triangles[-1].updateColor()
pygame.display.flip()

while len(triangles) < maxTriangles:
    #time.sleep(1)
    #for t in triangles:
    #    print(t.equations)
    #    print(t.points)
    #print('\t\n')
    #for t in triangles:
        #print(t.points)
        #for i,p in enumerate(t.points):
        #    pygame.draw.circle(screen,green,[p[0]*scale,p[1]*scale],5)
        #    pygame.draw.line(screen,red,[t.points[i-1][0]*scale,t.points[i-1][1]*scale],[t.points[i][0]*scale,t.points[i][1]*scale],3)

    #time.sleep(.25)

    data = []

    for triangle in triangles:
        #if area(triangle.points) > 1 or True:
        w, x, y, z = triangle.checkDuplicate()
        data.append({'colorVar' : w, 'colorDiff' : x, 'pos' : y, 'point' : z})
        #else:
        #    data.append({'colorVar' : 0, 'colorDiff' : 0})

    sortedData = sorted(deepcopy(data), key=lambda e: e['colorDiff'])[::-1]
    chosen = sortedData[0]
    index = data.index(chosen)
    points = deepcopy(triangles[index].points)
    #print(points)
    #print(chosen['point'])
    if chosen['point'] in points:
        points.remove(chosen['point'])
        triangles.append(Triangle([roundList(chosen['point']), roundList(chosen['pos']), roundList(points[0])]))
        triangles[-1].updateColor()
        #time.sleep(.25)
        triangles.append(Triangle([roundList(chosen['point']), roundList(chosen['pos']), roundList(points[1])]))
        triangles[-1].updateColor()

        triangles.pop(index)
        pygame.display.flip()
    else:
        print("I broke :(")
        break


running = True
while running:
    clock.tick(fps_limit)
    # screen.fill(background_colour)
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    # for i in range(len(tri.points)):
    #    pygame.draw.line(screen,red,tri.points[i-1],tri.points[i],3)

    # tri.testPoint([rand(0,800),rand(0,800)])
    pygame.display.flip()
pygame.quit()
