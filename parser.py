import xml.etree.ElementTree as ET
from math import atan, degrees, radians, sin, sqrt, tan, cos
from OSGridConverter import latlong2grid
tree = ET.parse(r'xml\map.osm.xml')
root = tree.getroot()
import numpy as np


class Building:
    buildings = []
    def __init__(self, OSM_id, nodes, centroid):
        Building.buildings.append(self)
        self.OSM_id = OSM_id
        self.nodes = nodes
        self.centre = centroid

        # Extents of orthogonal bounding box drawn around the shape
        minX = min([v[0] for v in self.nodes])
        maxX = max([v[0] for v in self.nodes])
        minY = min([v[1] for v in self.nodes])
        maxY = max([v[1] for v in self.nodes])

        diffX = maxX - minX
        diffY = maxY - minY
        # Is building taller in X dimension than Y?
        self.isVertical =  diffY > diffX

        # Northernmost, easternmost, southernmost, westernmost node.
        for i, node in enumerate(self.nodes):
            if i == 0: continue
            x, y = node
            if x == minX: xNodeMin = self.nodes[i]
            if x == maxX: xNodeMax = self.nodes[i]
            if y == minY: yNodeMin = self.nodes[i]
            if y == maxY: yNodeMax = self.nodes[i]


        # centreMidEast = [yNodeMax[0] + xNodeMax[0], yNodeMax[1] + xNodeMax[1]]
        # centreMidWest = [yNodeMin[0] + xNodeMin[0], yNodeMin[1] + xNodeMin[1]]
        # Find angle of the building, account for possibility of angle being 0.
        if maxX - yNodeMin[0] == 0 or yNodeMax[0] - minX == 0: 
            self.angle = 0
        else:
            ang1 = degrees(atan((xNodeMax[1] - minY) / (maxX - yNodeMin[0])))
            ang2 = degrees(atan((maxY - xNodeMin[1]) / (yNodeMax[0] - minX)))
            self.angle = (ang1 + ang2)/2
            # ang3 = degrees(atan(centreMid))

        # Div by zero fix
        # if self.angle == 0:
        #     self.length = diffX if self.isVertical else diffY
        #     self.width =  diffY if self.isVertical else diffX
        # else:
        #     sinTheta = sin(radians(self.angle))
        #     cosTheta = cos(radians(self.angle))
            
        if self.OSM_id == '461749327':
            print("ok")

        #self.area = 
        print("Created building at {0} at angle {1} and area of {2} with nodes: {3}".format(self.centre, self.angle, 15, self.nodes))
        
def find_nodes(branch, nodes={}):
    if branch.tag == 'node':
        nodes[branch.attrib['id']] = float(branch.attrib['lat']), float(branch.attrib['lon'])
    for child in branch:
        new_nodes = find_nodes(child, nodes)
        nodes.update(new_nodes)
    return nodes

def find_buildings(branch, buildings={}):
    is_building = False
    for child in branch:
        if 'k' in child.attrib:
            if child.attrib['k'] == 'building':
                is_building = True
    if is_building: 
        nodes = []
        for child in branch:
            if child.tag == 'nd': nodes.append(child.attrib['ref'])
        buildings[branch.attrib['id']] = nodes
    for child in branch:
        new_buildings = find_buildings(child, buildings)
        buildings.update(new_buildings)
    return buildings


buildings = find_buildings(root)
nodes = find_nodes(root)
minX = 9999999999
minY = 9999999999
for building in buildings.keys():
    building_nodes = [nodes[node] for node in buildings[building]]
    for i, coords in enumerate(building_nodes):
        lat, long = coords
        osGrid = latlong2grid(lat, long)
        x = osGrid.E
        y = osGrid.N
        minX = min(minX, x)
        minY = min(minY, y)
        building_nodes[i] = x, y
    buildings[building] = building_nodes
for building in buildings.keys():
    xSum = 0
    ySum = 0
    building_nodes = buildings[building]
    for i, coords in enumerate(building_nodes):
        x, y = coords
        x = x - minX
        y = y - minY
        building_nodes[i] = x, y
        xSum += x
        ySum += y
    cenX = xSum / len(building_nodes)
    cenY = ySum / len(building_nodes)
    centroid = (xSum, ySum)
    Building(building, np.asarray(building_nodes), np.asarray(centroid))