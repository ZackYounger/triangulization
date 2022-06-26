from PIL import Image, ImageDraw
from PyProbs import Probability as pr
import numpy as np

n = 500

oldImage = Image.open("images/cat.jpg")
#oldImage.show()
oldImage = oldImage.convert('RGB')

imgWidth, imgHeight = oldImage.width, oldImage.height
print(f"Dimensions = [{imgWidth, imgHeight}]")

newImage = Image.new('RGB',(imgWidth, imgHeight))

directions = [[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1],[0,-1],[1,-1]]

deltaData = [[None for i in range(imgWidth)] for j in range(imgHeight)]
adjustedDeltaData = [[None for i in range(imgWidth)] for j in range(imgHeight)]
colorData = [[None for i in range(imgWidth)] for j in range(imgHeight)]

for x in range(imgWidth):
    for y in range(imgHeight):
        colorData[y][x] = oldImage.getpixel((x,y))

maxDelta = 0
for x in range(imgWidth):
    for y in range(imgHeight):
        totalDelta = 0
        pixelData = colorData[y][x]
        for direction in directions:
            nX, nY = x + direction[0], y + direction[1]
            if 0 <= nX < imgWidth and 0 <= nY < imgHeight:
                newPixelData = colorData[nY][nX]
                pixelDelta = sum(abs(pixelData[i] - newPixelData[i]) for i in range(3))
            totalDelta += pixelDelta
            if totalDelta > maxDelta:
                maxDelta = totalDelta
        deltaData[y][x] = totalDelta


expectation = sum(sum(deltaData[y][x] for y in range(imgHeight)) for x in range(imgWidth))
readjust = n / expectation


for x in range(imgWidth):
    for y in range(imgHeight):
        adjustedDeltaData[y][x] = deltaData[y][x] / maxDelta
        colorValue = (round(adjustedDeltaData[y][x] * 255),
                      round(adjustedDeltaData[y][x] * 255),
                      round(adjustedDeltaData[y][x] * 255))
        newImage.putpixel((x,y), colorValue)
newImage.show()

points = []
colors = []
for x in range(imgWidth):
    for y in range(imgHeight):
        if deltaData[y][x] * readjust > 0.0001:
            if pr.Prob(deltaData[y][x] * readjust):
                points.append([x,y])
                colors.append(oldImage.getpixel((x,y)))
                newImage.putpixel((x, y), (255,0,0))

"""
print(len(points))

voronoi = Voronoi(points)
vertices = [tuple(t) for t in voronoi.vertices]
regions = voronoi.regions
print("\n")
print(len(points))
print(len(regions))

drawImage = ImageDraw.Draw(newImage)
for index,region in enumerate(regions):
    #print([vertices[r] for r in region])
    if len(region) >= 3 and -1 not in region and index < len(regions)-1:
        color = colorData[points[index][1]][points[index][0]]
        drawImage.polygon([vertices[r] for r in region], fill=color)
"""

for x in range(imgWidth):
    for y in range(imgHeight):
        values = []
        for point in points:
            values.append((x - point[0])**2 + (y - point[1])**2)
        index = values.index(min(values))
        newImage.putpixel((x,y),colors[index])

newImage.show()
