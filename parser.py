from logging import error
import xml.etree.ElementTree as ET
from math import atan, degrees, radians, sin, sqrt, tan, cos, inf, ceil
import numpy as np

EARTH_RADIUS = 6371000

class Arma_road:
    arma_road_match = {}
    def __init__(self, road_surface, road_type, straights, curves, end):
        self.surface = road_surface
        self.road_type = road_type
        self.straights = straights
        self.curves = curves
        self.end = end

        identifier = (road_type, road_surface)
        if identifier in Arma_road.arma_road_match.keys():
            raise BaseException("Identifier {} already exists".format(identifier))
        else: 
            Arma_road.arma_road_match[identifier] = self



    def nearest_corner(self, angle):
        nearest_angle = nearest_value(abs(angle), self.curves.keys())
        road_class, radius = self.curves[nearest_angle]
        return road_class, radius, nearest_angle

paved_primary = Arma_road('paved', 'primary', {
    6: "CUP_A2_Road_asf1_6",
    12 : "CUP_A2_Road_asf1_12",
    25 : "CUP_A2_Road_asf1_25"
},
{
    0:  ("CUP_A2_Road_asf1_6", 6),
    7:  ("CUP_A2_Road_asf1_7_100", 100),
    10: ("CUP_A2_Road_asf1_10_25", 25),
    30: ("CUP_A2_Road_asf1_30_25", 25),
    60: ("CUP_A2_Road_asf1_60_10", 10),
},
"CUP_A2_Road_asf1_6konec")

paved_secondary = Arma_road('paved', 'secondary', {
    6: "CUP_A2_Road_asf2_6",
    12 : "CUP_A2_Road_asf2_12",
    25 : "CUP_A2_Road_asf2_25"
},
{
    0:  ("CUP_A2_Road_asf2_6", 6),
    7:  ("CUP_A2_Road_asf2_7_100", 100),
    10: ("CUP_A2_Road_asf2_10_25", 25),
    30: ("CUP_A2_Road_asf2_30_25", 25),
    60: ("CUP_A2_Road_asf2_60_10", 10),
},
"CUP_A2_Road_asf3_6konec")

paved_secondary = Arma_road('paved', 'tertiary', {
    6: "CUP_A2_Road_asf3_6",
    12 : "CUP_A2_Road_asf3_12",
    25 : "CUP_A2_Road_asf3_25"
},
{
    0:  ("CUP_A2_Road_asf3_6", 6),
    7:  ("CUP_A2_Road_asf3_7_100", 100),
    10: ("CUP_A2_Road_asf3_10_25", 25),
    30: ("CUP_A2_Road_asf3_30_25", 25),
    60: ("CUP_A2_Road_asf3_60_10", 10),
},
"CUP_A2_Road_asf3_6konec")

paved_primary = Arma_road('paved', 'residential', {
    6: "CUP_A2_Road_asf1_6",
    12 : "CUP_A2_Road_asf1_12",
    25 : "CUP_A2_Road_asf1_25"
},
{
    0:  ("CUP_A2_Road_asf1_6", 6),
    7:  ("CUP_A2_Road_asf1_7_100", 100),
    10: ("CUP_A2_Road_asf1_10_25", 25),
    30: ("CUP_A2_Road_asf1_30_25", 25),
    60: ("CUP_A2_Road_asf1_60_10", 10),
},
"CUP_A2_Road_asf1_6konec")

class Node:
    nodes_all = []
    nodes_hash = {}
    def __init__(self, uid, coords):
        self.uid = uid
        self.coords = coords
        Node.nodes_all.append(self)
        Node.nodes_hash[uid] = self

class Road:
    roads_all = []
    roads_hash = {}
    def __init__(self, name, road_type, surface, nodes, uid, is_lit):
        self.name = name
        self.nodes = [nodes]
        self.uid = uid
        self.is_lit = is_lit

        if road_type in ["primary", 'trunk', "primary_link"]:
            self.road_type = "primary"
        elif road_type in ["secondary", "service"]:
            self.road_type = 'secondary'
        elif road_type in ["residential"]:
            self.road_type = "residential"
        elif road_type in ["tertiary", 'unclassified']:
            self.road_type = 'tertiary'
        elif road_type in ["pedestrian", "path", "steps", "bridleway", "track", "footway", "cycleway"]:
            self.road_type = 'path'
        else:
            raise NameError("{} not matched to any road type".format(road_type))

        if surface in ["concrete", "paved", "paving_stones", "paved", "asphalt"]:
            self.surface = "paved"
        elif surface in ["dirt", "compacted"]:
            self.surface = "dirt"
        elif surface in ["pebblestone", "gravel", "unpaved"]:
            self.surface = "gravel"
        else:
            raise NameError("{} not matched to any surface type".format(surface))
        Road.roads_all.append(self)


        if self.name != "NOT_FOUND":
            Road.roads_hash[name] = self

    def all_nodes(self):
        nodes = []
        for node_list in self.nodes:
            for node in node_list:
                if node not in nodes: nodes.append(node)
        return nodes

    def all_nodes_as_coords(self):
        return [node.coords for node in self.all_nodes()]

    def node_lists_as_coords(self):
        return [[node.coords for node in node_set] for node_set in self.nodes]

    def create_arma_objects(self):
        node_sets = self.node_lists_as_coords()
        arma_array = []
        road_class = Arma_road.arma_road_match[(self.road_type, self.surface)]
        lengths = road_class.straights.keys()
        min_road_length = min(lengths)
        for node_set in node_sets:
            start = node_set[:2]
            end = np.flip(node_set[-2:], axis=0)
            caps = [start, end]
            # for cap in caps:
            #     diff = cap[0] - cap[1]
            #     dist, angle_rad = cart2pol(diff[0], diff[1])
            #     angle_deg = 90 - degrees(angle_rad)
            #     arma_array.append([test_road.end, list(cap[0]), angle_deg])
            
            for i, node in enumerate(node_set[:-1]):
                next_node = node_set[i+1]
                current_pos = node
                diff = next_node - node
                dist, angle_rad = cart2pol(diff)
                dist_done = 0
                angle_deg = 90 - degrees(angle_rad)
                # corners
                if i > 0:
                    prev_node = node_set[i-1]
                    prev_diff = node - prev_node
                    ____, prev_angle_rad = cart2pol(prev_diff)
                    prev_angle = 90 - degrees(prev_angle_rad)
                    next_angle = angle_deg
                    angle_diff = next_angle - prev_angle
                    if abs(angle_diff) > min(road_class.curves.keys()):
                        corner_class, radius, actual_angle = road_class.nearest_corner(angle_diff)
                        corner_place_angle = prev_angle
                        if angle_diff < 0: corner_place_angle += 180 - actual_angle
                        arma_array.append([corner_class, list(node), corner_place_angle])

                while dist>=dist_done:
                    available_segments = [length for length in lengths if length <= dist-dist_done]
                    segment_length = max(available_segments) if len(available_segments) > 0 else min_road_length
                    offset = pol2cart(angle_rad, segment_length)
                    segement_start = current_pos
                    segment_end = segement_start + offset
                    centre = segement_start + offset/2
                    current_pos = segment_end
                    dist_done += segment_length
                    arma_array.append([road_class.straights[segment_length], list(centre), angle_deg])
        return arma_array



class Building:
    all_buildings = []
    def __init__(self, OSM_id, nodes):
        Building.all_buildings.append(self)
        self.OSM_id = OSM_id
        self.nodes = nodes

        # Extents of orthogonal bounding box drawn around the shape
        minX = min([v[0] for v in self.nodes])
        maxX = max([v[0] for v in self.nodes])
        minY = min([v[1] for v in self.nodes])
        maxY = max([v[1] for v in self.nodes])

        diffX = maxX - minX
        diffY = maxY - minY
        # Is building taller in Y dimension than X?
        self.isVertical =  diffY > diffX

        # Northernmost, easternmost, southernmost, westernmost node.
        for i, node in enumerate(self.nodes):
            if i == 0: continue
            x, y = node
            if x == minX: xNodeMin = self.nodes[i]
            if x == maxX: xNodeMax = self.nodes[i]
            if y == minY: yNodeMin = self.nodes[i]
            if y == maxY: yNodeMax = self.nodes[i]

        # centreMidNorth is the average of the northernmost and westernmost point
        # centreMidEast is the average of the easternmost and northernmost point
        # TODO: convert all this shit to numpy
        centreMidNorth= [(xNodeMin[0] + yNodeMax[0]) / 2, (xNodeMin[1] + yNodeMax[1]) / 2]
        centreMidEast = [(yNodeMax[0] + xNodeMax[0]) / 2, (yNodeMax[1] + xNodeMax[1]) / 2]
        centreMidSouth= [(xNodeMax[0] + yNodeMin[0]) / 2, (xNodeMax[1] + yNodeMin[1]) / 2]
        centreMidWest = [(yNodeMin[0] + xNodeMin[0]) / 2, (yNodeMin[1] + xNodeMin[1]) / 2]
        self.centre = [(xNodeMin[0] + xNodeMax[0] + yNodeMin[0] + yNodeMax[0]) / 4, (xNodeMin[1] + xNodeMax[1] + yNodeMin[1] + yNodeMax[1]) / 4]
        # Find angle of the building, account for possibility of angle being 0.
        if maxX - yNodeMin[0] == 0 or yNodeMax[0] - minX == 0: 
            self.angle = 0
        else:
            self.angle = degrees(atan( (centreMidEast[1]-centreMidWest[1]) / (centreMidEast[0]-centreMidWest[0]) ))

        a = sqrt((centreMidEast[0]  - centreMidWest[0])**2   + (centreMidEast[1] - centreMidWest[1])**2)
        b = sqrt((centreMidNorth[0] - centreMidSouth[0])**2 + (centreMidNorth[1] - centreMidSouth[1])**2)
        self.width = b if self.isVertical else a
        self.length = a if self.isVertical else b
        self.area = self.length * self.width
        if self.isVertical: self.angle += 90
        self.armaClass = ""

def cart2pol(triangle):
    dist = np.sqrt(triangle[0]**2 + triangle[1]**2)
    angle = np.arctan2(triangle[1], triangle[0])
    return dist, angle

def pol2cart(angle, dist):
    x = dist * np.cos(angle)
    y = dist * np.sin(angle)
    return np.asarray([x, y])

# def direction_to(p1, p2):
#     d = p2 - p1
#     return np.arctan2(d[1], d[0])

def get_dist(p1, p2):
    d = p2-p1
    return np.hypot(d[0], d[1])

def get_angle(p1, p2, return_radians=False):
    d = p2-p1
    angle = np.arctan2(d[0], d[1])
    if return_radians:
        return angle
    else:
        return np.degrees(angle)

def nearest_value(target, values):
    diff = inf
    for value in values:
        this_diff = abs(value - target)
        if this_diff < diff: 
            result = value
            diff = this_diff
    return result
    

def get_sub_object_attrib(instance, attrib, default_value = "NOT_FOUND"):
    sub = instance.find(".//*[@k='{}']".format(attrib))
    if sub is not None:
        return sub.attrib['v']
    else: 
        return default_value

def convert_nodes(root):
    nodes = root.findall('node')
    min_lat = min([float(node.attrib['lat']) for node in nodes])
    min_lon = min([float(node.attrib['lon']) for node in nodes])
    print("Min lat: {}, Min lon: {}".format(min_lat, min_lon))
    min_lat = radians(min_lat)
    min_lon = radians(min_lon)
    cos_standard_parallel = cos(min_lat)
    for node in nodes:
        lat = radians(float(node.attrib['lat']))
        lon = radians(float(node.attrib['lon']))
        x = EARTH_RADIUS*(lon - min_lon)*cos_standard_parallel
        y = EARTH_RADIUS*(lat - min_lat)
        coords = np.asarray([x, y])
        Node(node.attrib['id'], coords)
    print("Found {} nodes".format(len(Node.nodes_all)))

def convert_highway_lines(root):
    ways = root.findall('way')
    highways = [way for way in ways if way.find(".//*[@k='highway']") is not None]
    print("Found {} highways".format(len(highways)))
    for highway in highways:
        nodes = [Node.nodes_hash[node.attrib['ref']] for node in highway.findall("nd")]
        road_name = get_sub_object_attrib(highway, 'name')
        if road_name in Road.roads_hash.keys():
            this_road = Road.roads_hash[road_name]
            this_road.nodes.append(nodes)
        else:
            road_uid = highway.attrib['id']
            road_type = get_sub_object_attrib(highway, 'highway')
            road_lit = get_sub_object_attrib(highway, 'lit')
            road_surface = get_sub_object_attrib(highway, 'surface', "asphalt")

            Road(road_name, road_type, road_surface, nodes, road_uid, road_lit)
    unique_road_types = list(set([road.road_type for road in Road.roads_all]))
    unique_road_surfaces = list(set([road.surface for road in Road.roads_all]))
    print("Created {} unique roads. {} are unnamed. {} are named.".format(len(Road.roads_all), len(Road.roads_all) - len(Road.roads_hash), len(Road.roads_hash)))
    print("Unique road types: {}".format(unique_road_types))
    print("Unique road surfaces: {}".format(unique_road_surfaces))




def main():
    tree = ET.parse(r'xml\map.osm.xml')
    root = tree.getroot()
    convert_nodes(root)
    convert_highway_lines(root)
    with open("road_test.txt", 'w') as f:
        array = []
        for road in Road.roads_all:
            array.extend(road.create_arma_objects())
        f.write(str(array))
    # with open("road_nodes.txt", 'w') as f:
    #     road_nodes = []
    #     for road in Road.roads_all:
    #         road_nodes.extend([list(coord) for coord in road.all_nodes_as_coords()])
    #     f.write(str(road_nodes))

if __name__ == "__main__":
    main()