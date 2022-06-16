import pygame
from PIL import Image
import time

scale = 3
image = Image.open("images/colours.png")
image = image.convert('RGB')

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
    return n / abs(n)


class Triangle:
    def __init__(self, points):
        # self.points = [[0, 0] for i in range(3)]
        self.points = points

        self.findEquations()

    def findEquations(self):
        mean = [sum(self.points[i][0] for i in range(3)) / 3,
                sum(self.points[i][1] for i in range(3)) / 3]

        self.equations = []
        for line in range(3):
            if self.points[line][1] == self.points[(line + 1) % 3][1]:
                gradient = 0
            elif self.points[line][0] == self.points[(line + 1) % 3][0]:
                gradient = 10**10 #doubt!!!
            else:
                gradient = (self.points[line][1] - self.points[(line + 1) % 3][1]) / (
                            self.points[line][0] - self.points[(line + 1) % 3][0])
            intercept = self.points[line][1] - gradient * self.points[line][0]
            tempSign = sign(mean[0] - gradient * mean[1] - intercept)
            self.equations.append({'gradient': gradient,
                                   'intercept': intercept,
                                   'sign': tempSign})


    def checkDuplicate(self):
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

                print(x,y)
                rgb = image.getpixel((min(x, imgWidth-1), min(y, imgHeight-1)))
                tempLine.append({'pos': [x, y], 'rgb': rgb})


                if inspectionLength + gap < point < max(length) - inspectionLength - gap:
                    delta = sum(abs(tempLine[point - inspectionLength]['rgb'][i] - tempLine[point]['rgb'][i]) for i in range(3))
                    if delta > maxColorChange:
                        maxColorChange = delta
                        colorChangePos = tempLine[round(point - inspectionLength/ 2)]['pos']
        return maxColorChange, colorChangePos, self.points[line]


    def updateColor(self):
        xRange = [min(x[0] for x in self.points), max(x[0] for x in self.points)]
        yRange = [min(y[1] for y in self.points), max(y[1] for y in self.points)]

        print('range = ',xRange,yRange)

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


maxTriangles = 10

triangles.append(Triangle([[0, 0], [0, imgHeight], [imgWidth, 0]]))
triangles[-1].updateColor()
triangles.append(Triangle([[0, imgHeight], [imgWidth, 0], [imgWidth, imgHeight]]))
triangles[-1].updateColor()
pygame.display.flip()

while len(triangles) < maxTriangles:
    for t in triangles:
        print(t.points)
        #for i,p in enumerate(t.points):
        #    pygame.draw.circle(screen,green,[p[0]*scale,p[1]*scale],5)
        #    pygame.draw.line(screen,red,[t.points[i-1][0]*scale,t.points[i-1][1]*scale],[t.points[i][0]*scale,t.points[i][1]*scale],3)

    pygame.display.flip()
    time.sleep(1)

    data = []
    for triangle in triangles:
        x, y, z = triangle.checkDuplicate()
        data.append({'colorDiff' : x, 'pos' : y, 'point' : z})
    sortedData = sorted(data, key=lambda e: e['colorDiff'])[::-1]
    chosen = sortedData[0]
    index = data.index(chosen)
    points = triangles[index].points
    points.remove(chosen['point'])

    triangles.append(Triangle([roundList(chosen['point']), roundList(chosen['pos']), roundList(points[0])]))
    triangles[-1].updateColor()
    triangles.append(Triangle([roundList(chosen['point']), roundList(chosen['pos']), roundList(points[1])]))
    triangles[-1].updateColor()
    triangles.pop(index)
    print('duped')
    pygame.display.flip()


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
