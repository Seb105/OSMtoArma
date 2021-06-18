from logging import error
import xml.etree.ElementTree as ET
from math import atan, degrees, radians, sin, sqrt, tan, cos, inf, ceil
from time import time
import numpy as np
import scipy
import ast

EARTH_RADIUS = 6371000

class Arma_road:
    arma_road_match = {}
    def __init__(self, road_surfaces, road_types, straights, curves, end, placeAtCentre=False):
        if isinstance(road_types, str): road_types = (road_types,)
        if isinstance(road_surfaces, str): road_surfaces = (road_surfaces,)
        self.surfaces = road_surfaces
        self.road_types = road_types
        self.straights = straights
        self.curves = curves
        self.end = end
        self.placeCentre = placeAtCentre

        # A road can be multiple types, this allows you to search by a single tuple.
        for road_type in road_types:
            for road_surface in road_surfaces:
                identifier = (road_surface, road_type)
                if identifier in Arma_road.arma_road_match.keys():
                    raise BaseException("Identifier {} already exists".format(identifier))
                else: 
                    Arma_road.arma_road_match[identifier] = self


    # From available angle pieces, find the nearest.
    def nearest_corner(self, angle):
        nearest_angle = nearest_value(abs(angle), self.curves.keys())
        road_class, radius = self.curves[nearest_angle]
        return road_class, radius, nearest_angle

def define_roads():
    paved_primary = Arma_road('paved', ('primary', 'residential'), {
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
    "CUP_A2_Road_asf2_6konec")

    paved_tertiary = Arma_road('paved', ('tertiary', 'unclassified'), {
        6: "CUP_A2_Road_OA_asf2_6",
        12 : "CUP_A2_Road_OA_asf2_12",
        25 : "CUP_A2_Road_OA_asf2_25"
    },
    {
        0:  ("CUP_A2_Road_OA_asf2_6", 6),
        7:  ("CUP_A2_Road_OA_asf2_7100", 100),
        15: ("CUP_A2_Road_OA_asf2_1575", 75),
        30: ("CUP_A2_Road_OA_asf2_3025", 25),
        60: ("CUP_A2_Road_OA_asf2_6010", 10),
    },
    "CUP_A2_Road_OA_asf2_6konec")

    paved_service = Arma_road('paved', 'service', {
        6: "CUP_A1_Road_asf6",
        12 : "CUP_A1_Road_asf12",
        25 : "CUP_A1_Road_asf25"
    },
    {
        0:  ("CUP_A1_Road_asf6", 6),
        10:  ("CUP_A1_Road_asf10_25", 25),
    },
    "CUP_A2_Road_asf6_6konec")

    gravel_tertiary = Arma_road('gravel', ('tertiary', 'unclassified'), {
        6: "CUP_A2_Road_grav_6",
        12 : "CUP_A2_Road_grav_12",
        25 : "CUP_A2_Road_grav_25"
    },
    {
        0:  ("CUP_A2_Road_grav_6", 6),
        7:  ("CUP_A2_Road_grav_7_100", 100),
        10: ("CUP_A2_Road_grav_10_25", 25),
        30: ("CUP_A2_Road_grav_30_25", 25),
        60: ("CUP_A2_Road_grav_60_10", 10),
    },
    "CUP_A2_Road_grav_6konec")

    dirt_tertiary = Arma_road('dirt', ('tertiary', 'unclassified'), {
        6: "CUP_A2_Road_mud_6",
        12 : "CUP_A2_Road_mud_12",
        25 : "CUP_A2_Road_mud_25"
    },
    {
        0:  ("CUP_A2_Road_mud_6", 6),
        7:  ("CUP_A2_Road_mud_7_100", 100),
        10: ("CUP_A2_Road_mud_10_25", 25),
        30: ("CUP_A2_Road_mud_30_25", 25),
        60: ("CUP_A2_Road_mud_60_10", 10),
    },
    "CUP_A2_Road_mud_6konec")

    paved_path = Arma_road('paved', 'path', {
        1: "CUP_Sidewalk_SidewalkSClearShort",
        5 : "CUP_Sidewalk_SidewalkSClearMiddle",
        10 : "CUP_Sidewalk_SidewalkSClearLong"
    },
    {
        0:  ("CUP_Sidewalk_SidewalkSClearShort", 6),
    },
    "CUP_Sidewalk_SidewalkSShortEnd", True)

    dirt_path = Arma_road(('dirt', 'gravel'), 'path', {
        6: "CUP_A2_Road_OA_path_6",
        12 : "CUP_A2_Road_OA_path_12",
        25 : "CUP_A2_Road_OA_path_25"
    },
    {
        0:  ("CUP_A2_Road_OA_path_6", 6),
        7:  ("CUP_A2_Road_OA_path_7_100", 100),
        10: ("CUP_A2_Road_OA_path_10_25", 25),
        30: ("CUP_A2_Road_OA_path_30_25", 25),
        60: ("CUP_A2_Road_OA_path_60_10", 10),
    },
    "CUP_A2_Road_OA_path_6konec")

class Arma_building:
    sizes = {}
    def __init__(self, arma_class, biome, width, length, height, structure_type):
        size_key = (width, length, biome)
        if size_key in Arma_building.sizes.keys():
            # This class will get garbage collected
            Arma_building.sizes[size_key].arma_classes.append(arma_class)
        else:
            self.width = width
            self.length = length
            self.height = height
            self.arma_classes = [arma_class,]
            self.biome = biome
            self.structure_type = structure_type
            Arma_building.sizes[size_key] = self

            self.variety = 0

    @classmethod
    def find_suitable_building(Arma_building, target_width, target_length, desired_type):
        accuracy = 0
        buildings = [building for building in Arma_building.sizes.values() if building.structure_type == desired_type]
        return_building = None
        # Cycle through all buildings of this size
        for building in buildings:
            width = building.width
            length = building.length
            if width>target_width or length>target_length: continue
            this_accuracy = 1/(abs(width-target_width)+abs(length-target_length))
            if this_accuracy > accuracy:
                accuracy = this_accuracy
                return_building = building

        if return_building is None:
            return None
        else:
            return_class = return_building.arma_classes[return_building.variety]
            if return_building.variety == len(return_building.arma_classes)-1:
                return_building.variety = 0
            else:
                return_building.variety += 1
            return return_class

def covert_arma_buildings(path=r"input_data\armaObjects.txt"):
    print("Converting arma buildings to classes")
    i = 0
    with open(path, 'r') as f:
        array_string = f.readline()
    objects_array = ast.literal_eval(array_string)
    for category in objects_array:
        structure_type, structures =  tuple(category)
        for structure in structures:
            i += 1
            arma_class, biome, width, length, height = tuple(structure)
            Arma_building(arma_class, biome, width, length, height, structure_type)
    print("Converted {} buildings to arma type".format(i))



class Node:
    nodes_all = []
    nodes_hash = {}
    def __init__(self, uid, coords):
        self.uid = uid
        self.coords = coords
        Node.nodes_all.append(self)
        Node.nodes_hash[uid] = self

class Road:
    all_roads = []
    roads_hash = {}
    unmatched_road_types = []
    unmatched_road_surfaces = []
    def __init__(self, name, road_type, surface, nodes, uid, is_lit):
        self.name = name
        self.nodes = [nodes]
        self.uid = uid
        self.is_lit = is_lit
        self.buildings = []

        MOTORWAY_ROAD_TYPES =       ['motorway', 'motorway_link']
        PRIMARY_ROAD_TYPES =        ["primary", "primary_link", 'trunk', 'trunk_link', 'corridor']
        SECONDARY_ROAD_TYPES =      ["secondary", "secondary_link"]
        SERVICE_ROAD_TYPES =        ["service"]
        RESIDENTIAL_ROAD_TYPES =    ["residential", 'living_street']
        TERTIARY_ROAD_TYPES =       ["tertiary", "tertiary_link", 'unclassified']
        PATH_ROAD_TYPES =           ["pedestrian", "path", "steps", "bridleway", "track", "footway", "cycleway", "elevator"]

        if road_type in PRIMARY_ROAD_TYPES or road_type in MOTORWAY_ROAD_TYPES:
            self.road_type = "primary"
        elif road_type in SECONDARY_ROAD_TYPES:
            self.road_type = 'secondary'
        elif road_type in SERVICE_ROAD_TYPES:
            self.road_type = 'service'
        elif road_type in RESIDENTIAL_ROAD_TYPES:
            self.road_type = "residential"
        elif road_type in TERTIARY_ROAD_TYPES:
            self.road_type = 'tertiary'
        elif road_type in PATH_ROAD_TYPES:
            self.road_type = 'path'
        else:
            self.road_type = 'secondary'
            if road_type not in Road.unmatched_road_types: Road.unmatched_road_types.append(road_type)

        PAVED_ROAD_TYPES =  ["concrete", "paved", "paving_stones", "paved", "asphalt", 'resin bonded']
        DIRT_ROAD_TPYES =   ["dirt", "compacted"]
        GRAVEL_ROAD_TYPES = ["pebblestone", "gravel", "unpaved", "unhewn_cobblestone", "cobblestone"]

        if surface in PAVED_ROAD_TYPES:
            self.surface = "paved"
        elif surface in DIRT_ROAD_TPYES:
            self.surface = "dirt"
        elif surface in GRAVEL_ROAD_TYPES:
            self.surface = "gravel"
        else:
            self.surface = 'paved'
            if surface not in Road.unmatched_road_surfaces: Road.unmatched_road_surfaces.append(surface)

        if self.name != "NOT_FOUND":
            Road.roads_hash[name] = self
        Road.all_roads.append(self)

    def all_nodes(self):
        nodes = []
        for node_list in self.nodes:
            for node in node_list:
                if node not in nodes: nodes.append(node)
        return nodes

    def all_nodes_as_coords(self):
        return [node.coords for node in self.all_nodes()]

    def node_sets_as_coords(self):
        return [[node.coords for node in node_set] for node_set in self.nodes]

    def get_road_tangent(self, coords):
        # Find perpendicular direction of two closest road points
        nodes = self.all_nodes_as_coords()
        vector_distances = nodes - coords
        distances = np.asarray([np.hypot(point[0], point[1]) for point in vector_distances])
        sorted_distances = np.argsort(distances)
        nearest = vector_distances[sorted_distances[0]]
        second_nearrest = vector_distances[sorted_distances[1]]
        diff = second_nearrest - nearest
        ____, angle = cart2pol(diff)
        return angle
    
    @classmethod
    def find_nearest_road(Road, coords, close_enough=inf):
        distance = inf
        for road in Road.all_roads:
            if road.road_type == 'path': continue # Buildings aren't aligned to paths
            nodes = road.all_nodes_as_coords()
            vector_distances = nodes - coords
            distances = np.asarray([np.hypot(point[0], point[1]) for point in vector_distances])
            min_distance = np.min(distances)
            if min_distance<distance:
                closest_road = road
                distance = min_distance
                if distance < close_enough: break
        return distance, closest_road
            
    # Create an array of objects that can be used in Arma 3 to create objects. Format [class, pos, dir]
    def create_arma_objects(self):
        node_sets = self.node_sets_as_coords()
        arma_array = []
        # Find the type of segments to use from the road surface and type.
        # If the road type does not exist, try matching just the surface. Throw error if that doesn't exist either
        road_search = (self.surface, self.road_type)
        if road_search in Arma_road.arma_road_match.keys():
            road_class = Arma_road.arma_road_match[road_search]
        else:
            road_class_list = [key for key in Arma_road.arma_road_match.keys() if key[0] == road_search[0]]
            if len(road_class_list) > 0:
                road_identifier = road_class_list[0]
                road_class = Arma_road.arma_road_match[road_identifier]
                print("WARNING: Arma Road {} could not be found. Defaulted to {}".format(road_search, road_identifier))
            else:
                raise KeyError("{} cannot be matched to any type of Arma road".format(road_search))
        placeAtCentre = road_class.placeCentre
        lengths = road_class.straights.keys()
        min_road_length = min(lengths)
        # Roads are made up of multiple sets of nodes, we must iterate over all.
        # Example node set:
        # [
        #   [
        #       [1x1, 1y1], 
        #       [1x2, 2xy]
        #       [1x3...]
        #   ], 
        #   [
        #       [2x1, 2y1], 
        #       [2x2, 2y2]
        #       [2x3....]
        #   ]...
        # ]
        for node_set in node_sets:
            start = node_set[:2]
            end = np.flip(node_set[-2:], axis=0)
            caps = [start, end]
            # There is a special road piece for the start and end of segments. Find and place it.
            # for cap in caps:
            #     diff = cap[0] - cap[1]
            #     dist, angle_rad = cart2pol(diff[0], diff[1])
            #     angle_deg = 90 - degrees(angle_rad)
            #     arma_array.append([test_road.end, list(cap[0]), angle_deg])
            
            # Create roads from segments. Do not do last element as knowledge of the next node is required.
            for i, node in enumerate(node_set[:-1]):
                next_node = node_set[i+1]
                current_pos = node
                #Vector distance between two points
                diff = next_node - node
                # Distance from this node to next node and angle.
                dist, angle_rad = cart2pol(diff)
                dist_done = 0
                # Subtract from 90 as angle_rad is actually 0 when pointing east, and we want 0 = north.
                angle_deg = 90 - degrees(angle_rad)

                # Corner pieces between segments. As this requires knowledge of the previous node, do not do the first node.
                # if i > 0:
                #     prev_node = node_set[i-1]
                #     prev_diff = node - prev_node
                #     # Direction of road incoming to curve
                #     ____, prev_angle_rad = cart2pol(prev_diff)
                #     prev_angle = 90 - degrees(prev_angle_rad)
                #     # Direction of road outgoing to curve
                #     next_angle = angle_deg
                #     # The difference between the two angles. This is the angle desired for the corner segment
                #     angle_diff = next_angle - prev_angle
                #     # Only create a curve if there is a curve small enough to work.
                #     if abs(angle_diff) > min(road_class.curves.keys()):
                #         corner_class, radius, actual_angle = road_class.nearest_corner(angle_diff)
                #         corner_place_angle = prev_angle
                #         # All road pieces curve right. If we want it to curve left, rotate by 180 degrees - the angle of the segment.
                #         if angle_diff < 0: corner_place_angle += 180 - actual_angle
                #         arma_array.append([corner_class, list(node), corner_place_angle])
                #         # TODO: figure out a way of connecting up more cleanly.
                #     else:
                #         pass
                #         #TODO: use a straight segment at an angle?

                while dist>=dist_done:
                    # Filter segment lengths to those less than or equal to the distance remaining
                    available_segments = [length for length in lengths if length <= dist-dist_done]
                    # Segment to use
                    segment_length = max(available_segments) if len(available_segments) > 0 else min_road_length
                    
                    # Move the segment into position and update origin for next iteration
                    offset = pol2cart(angle_rad, segment_length)
                    segement_start = current_pos
                    segment_end = segement_start + offset

                    # Some objects are placed at the model centre, and some are placed at the edge of the model. Offset is different in each case. Handle that here.
                    centre = segement_start + offset/2 if placeAtCentre else segement_start
                    current_pos = segment_end
                    dist_done += segment_length
                    arma_array.append([road_class.straights[segment_length], list(centre), angle_deg])
        return arma_array

class Building:
    all_buildings = []
    uses_not_exactly_matched = []
    def __init__(self, centre, direction, width, length, road_object, building_type, uid):
        self.uid = uid
        self.centre = centre
        self.direction = direction
        self.width = width
        self.length = length
        if road_object is not None:
            road_object.buildings.append(self)
        
        BUILDING_TYPES_RELIGIOUS = ['place_of_worship', 'cathedral', 'chapel', 'church', 'mosque', 'monastery', 'presbytery', 'religious', 'shrine', 'synagogue', 'temple']
        BUILDING_TYPES_INDUSTRIAL = ['industrial', 'warehouse']
        BUILDING_TYPES_HOUSE = ['yes', 'house', 'apartments', 'detatched','residential', 'terrace']
        BUILDING_TYPES_COMMERCIAL = ['commercial', 'retail', 'cafe', 'restraunt', 'cinema']

        if building_type in BUILDING_TYPES_RELIGIOUS:
            self.building_type = "religious"
        elif building_type in BUILDING_TYPES_INDUSTRIAL:
            self.building_type = 'industrial'
        elif building_type in BUILDING_TYPES_HOUSE:
            self.building_type = 'town'
        elif building_type in BUILDING_TYPES_COMMERCIAL:
            #TODO: Make unique?
            self.building_type = 'town'
        else:
            self.building_type = 'town'
            # Warn that this was not matched for later
            if building_type not in Building.uses_not_exactly_matched: Building.uses_not_exactly_matched.append(building_type)
        
        self.arma_class = Arma_building.find_suitable_building(width, length, self.building_type)
        
        if self.arma_class != None:
            Building.all_buildings.append(self)

    def create_arma_objects(self):
        return [self.arma_class, list(self.centre), self.direction]

def cart2pol(coords):
    dist = np.sqrt(coords[0]**2 + coords[1]**2)
    angle = np.arctan2(coords[1], coords[0])
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
    # Grab all nodes from the XML file and convert it to local x, y via equirectangular projection
    # https://en.wikipedia.org/wiki/Equirectangular_projection
    # Store it as a class acessible by the UID.
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
    # Convert all highways to classes.
    # A highway is made up of one or more node sets.
    ways = root.findall('way')
    highways = [way for way in ways if way.find(".//*[@k='highway']") is not None]
    all_road_types = []
    all_road_surfaces = []
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

            if road_type not in all_road_types: all_road_types.append(road_type)
            if road_surface not in all_road_surfaces: all_road_surfaces.append(road_surface)
    print("Created {} unique roads. {} are unnamed. {} are named.".format(len(Road.all_roads), len(Road.all_roads) - len(Road.roads_hash), len(Road.roads_hash)))
    print("Unique road types: {}".format(all_road_types))
    print("Unique road surfaces: {}".format(all_road_surfaces))
    print("All unique road types succesfully simplified.")

    print("WARNING: The following road types are not defined and defaulted to 'secondary': {}".format(Road.unmatched_road_types))
    print("WARNING: The following road surfaces are not defined and defaulted to 'paved': {}".format(Road.unmatched_road_surfaces))

def convert_buildings(root):
    print("Converting buildings")
    buildings = [building for building in root if building.find(".//*[@k='building']") is not None and len(building.findall('nd')) > 1]
    print("Found {} buildings".format(len(buildings)))
    building_types = []
    building_amenities = []
    building_uses = []
    for building in buildings: 
        building_type = get_sub_object_attrib(building, 'building')
        building_amenity =  get_sub_object_attrib(building, 'amenity', 'none')
        if building_type not in building_types: building_types.append((building_type))
        if building_amenity not in building_amenities: building_amenities.append(building_amenity)
        if building_type == 'yes' and building_amenity != 'none':
            building_use = building_amenity
        else:
            building_use = building_type
        if building_use not in building_uses: building_uses.append(building_use)
    print("Unique building types: {}".format(building_types))
    print("Unique amenity types: {}".format(building_amenities))
    print("Unique buildings uses: {}".format(building_uses))

    for building in buildings:
        uid = building.attrib['id']
        building_type = get_sub_object_attrib(building, 'building')
        building_street = get_sub_object_attrib(building, 'addr:street', 'none')
        building_amenity =  get_sub_object_attrib(building, 'amenity', 'none')
        if building_type == 'yes' and building_amenity != 'none':
            building_use = building_amenity
        else:
            building_use = building_type
        nodes = [Node.nodes_hash[node.attrib['ref']] for node in building.findall("nd")]
        nodes_coords = [node.coords for node in nodes]
        maxes = np.max(nodes_coords, 0)
        mins = np.min(nodes_coords, 0)
        max_x = maxes[0]
        max_y = maxes[1]
        min_x = mins[0]
        min_y = mins[1]
        # Get northernmost, easternmost, southernmost, westernmost points.
        n = [p for p in nodes_coords if p[1] == max_y][0]
        s = [p for p in nodes_coords if p[1] == min_y][0]
        e = [p for p in nodes_coords if p[0] == max_x][0]
        w = [p for p in nodes_coords if p[0] == min_x][0]

        diff_x = max_x - min_x
        diff_y = max_y - min_y
        diff = ((n-e)+(s-w))/2
        delta_x = diff[0]
        delta_y = diff[1]
        width = sqrt(delta_x**2 + (diff_y - delta_y)**2)
        length = sqrt(delta_y**2 + (diff_x - delta_x)**2)
        centreX = (min_x + max_x)/2
        centreY = (min_y + max_y)/2
        centre = np.asarray([centreX, centreY])
        direction_manual = np.arctan2(delta_y, delta_x)
        direction_deg_manual = degrees(direction_manual)
        if direction_deg_manual < 0: direction_deg_manual += 360
        # If building has an associated street or a nearby street, then find the tangent of the closest segment, else calculate it manually.
        if building_street == 'none' or building_street not in Road.roads_hash.keys():
            distance, street_object = Road.find_nearest_road(centre, 15)
        else:
            street_object = Road.roads_hash[building_street]
            vector_distances = street_object.all_nodes_as_coords() - centre
            distances = np.asarray([np.hypot(point[0], point[1]) for point in vector_distances])
            distance = np.min(distances)
        if distance < 45:
            direction = street_object.get_road_tangent(centre)
            # Rotate to face road
            direction_deg = 90 - degrees(direction) - 90
            if direction_deg < 0: direction_deg += 360
            # Difference between the two disagreeing directions to nearest 90 deg
            x = (direction_deg%90 + direction_deg_manual%90) % 90
            disagreement = min(x, 90-x)
            modifier = cos(radians(disagreement))
            width = width * modifier
            length = length * modifier
            # If angle is east or west, then swap with and length
            if 45>direction_deg<135 or 225>direction_deg<315:
                a, b = width, length
                width, length = b, a
                #directionDeg += 90
        else:
            direction_deg = direction_deg_manual
            width = width/1.41
            length = length/1.41
            if length > width:
                a, b = width, length
                width, length = b, a
                direction_deg += 90
        Building(centre, direction_deg, width, length, street_object, building_type, uid)
    print("WARNING: The following building types were not exactly matched: {}".format(Building.uses_not_exactly_matched))

def output_all_to_arma_array():
    buildArray = []
    for road in Road.all_roads:
        buildArray.extend(road.create_arma_objects())
    for building in Building.all_buildings:
        buildArray.append(building.create_arma_objects())
    with open(r"input_data\fn_createCity.sqf") as c:
        script = c.readlines()
    with open("output.sqf", 'w') as f:
        f.truncate()
        f.writelines([line.replace("[THE_BUILD_ARRAY]", str(buildArray)) for line in script])
    

def main():
    tree = ET.parse(r'xml\map.osm.xml')
    root = tree.getroot()
    covert_arma_buildings()
    convert_nodes(root)
    define_roads()
    convert_highway_lines(root)
    convert_buildings(root)
    output_all_to_arma_array()
    # with open("road_test.txt", 'w') as f:
    #     array = []
    #     for road in Road.all_roads:
    #         array.extend(road.create_arma_objects())
    #     f.write(str(array))

if __name__ == "__main__":
    main()