from logging import error
import xml.etree.ElementTree as ET
from math import atan, atan2, degrees, radians, sin, sqrt, cos, inf
from statistics import mean
import time
import numpy as np
from PIL import Image, ImageDraw
import ast
import random
random.seed(1)
EARTH_RADIUS = 6371000
# ROAD TYPE DEFINITIONS
MOTORWAY_ROAD_TYPES =       ['motorway', 'motorway_link']
PRIMARY_ROAD_TYPES =        ["primary", "primary_link", 'trunk', 'trunk_link', 'corridor']
SECONDARY_ROAD_TYPES =      ["secondary", "secondary_link"]
SERVICE_ROAD_TYPES =        ["service"]
RESIDENTIAL_ROAD_TYPES =    ["residential", 'living_street']
TERTIARY_ROAD_TYPES =       ["tertiary", "tertiary_link", 'unclassified']
PATH_ROAD_TYPES =           ["pedestrian", "path", "steps", "bridleway", "track", "footway", "cycleway", "elevator"]

# ROAD SURFACE DEFINITIONS
PAVED_ROAD_TYPES =  ["concrete", "paved", "paving_stones", "paved", "asphalt", 'resin bonded']
DIRT_ROAD_TPYES =   ["dirt", "compacted"]
GRAVEL_ROAD_TYPES = ["pebblestone", "gravel", "unpaved", "unhewn_cobblestone", "cobblestone"]

# Single node lookup table
NODE_OBJECT_TYPES = {
    'tree' : ["CUP_les_dub", "CUP_les_dub_jiny", "CUP_t_quercus2f_summer", "CUP_t_betula2f_summer", "CUP_t_betula2s_summer"],
    'bench' : "Land_Bench_01_F",
    'post_box' : "Land_GasMeterCabinet_01_F", #eh
    'waste_basket' : "Land_GarbageBin_02_F",
    'telephone' : "Land_PhoneBooth_01_F",
    'atm' : "Land_ATM_01_malden_F",
    'statue' : ["Land_Maroula_F", "Land_Statue_02_F", "Land_Statue_01_F", "Land_Monument_01_F", "Land_Statue_03_F"],
    "memorial" : ["Land_Grave_memorial_F", "Land_Pedestal_01_F"],
    "bus_stop" : "Land_BusStop_01_shelter_F"
}

#Woods objets
WOODS_OBJECT_TYPES = [
    "CUP_les_dub",
    "CUP_les_dub_jiny",
    "CUP_t_quercus2f_summer",
    "CUP_t_betula2f_summer",
    "CUP_t_betula2s_summer",
    "CUP_b_AmygdalusN1s_EP1",
    "CUP_ker_s_bobulema",
    "CUP_koprivy",
    "CUP_ker_pichlavej",
    "CUP_kmen_1_buk",
]

class Progress_bar():
    def __init__(self, activity, count):#
        self.activity = activity
        self.count = count
        self.i = -1
        self.barlength = 20
        self.last_update = time.time()-10
        print("")
        self.update_progress()

    # def print(self, string)
    #     print(string)
    #     print("")

    def update_progress(self):
        self.i += 1
        progress = self.i/self.count
        if self.last_update+1<time.time() or progress >= 1:
            self.last_update=time.time()
            block = int(round(self.barlength*progress))
            text = "{0}: [{1}] {2}%".format(self.activity, "#"*block + "-"*(self.barlength-block), round(progress*100))
            lineEnd = '\r' if progress<1.0 else '\n\n'
            print(text, end=lineEnd)

class Arma_road:
    """
    An arma road is a collection of arma road segment classes with some identifying properties such as segment length, turning radius and turning angle, 
    
    These segments may be used to convert an OSM way into arma classes."""
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
    """
    An Arma building is the class representation of an actual arma building class.

    It contains the data of that building such as width, length and height so that it may be matched to an OSM building.
    """
    sizes = {}
    all_classes = {}
    def __init__(self, arma_class, biome, width, length, height, structure_type):
        size_key = (width, length, biome)
        if size_key in Arma_building.sizes.keys():
            # This class will get garbage collected
            existing_building = Arma_building.sizes[size_key]
            existing_building.arma_classes.append(arma_class)
            Arma_building.all_classes[arma_class] = existing_building
        else:
            self.width = width
            self.length = length
            self.height = height
            self.arma_classes = [arma_class,]
            self.biome = biome
            self.structure_type = structure_type
            Arma_building.sizes[size_key] = self
            Arma_building.all_classes[arma_class] = self

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
            if width*0.9>target_width or length>target_length: continue
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

def define_arma_buildings(path=r"input_data\armaObjects.txt", biome_blacklist=[]):
    print("Converting arma buildings to classes")
    i = 0
    with open(path, 'r') as f:
        array_string = f.readline()
    objects_array = ast.literal_eval(array_string)
    for category in objects_array:
        structure_type, structure_biome, structures =  tuple(category)
        if structure_biome in biome_blacklist: continue
        for structure in structures:
            i += 1
            arma_class, width, length, height = tuple(structure)
            Arma_building(arma_class, structure_biome, width, length, height, structure_type)
    print("Converted {} buildings to arma type".format(i))

class Node:
    """
    A node is a coordinate with a UID. OSM objects may or may not share nodes
    """
    nodes_all = []
    nodes_hash = {}
    def __init__(self, uid, coords):
        self.uid = uid
        self.coords = coords
        Node.nodes_all.append(self)
        Node.nodes_hash[uid] = self

class Road:
    """
    A Road object is an imported OSM road. 
    It can be turned into a set of Arma objects using create_arma_objects(self), 
    which uses the Arma_road class to find the correct segments for this road type.
    """
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

    def get_direction_perp_to_road(self, coords):
        """
        This function returns the angle perpendicular to the tangent of the closest road section of the given coordinates. Used for aligning a property to the road.

        TODO: Make it so the house faces the road, right now it only faces N/E
        """
        # Find direction of two closest road points
        nodes = self.all_nodes_as_coords()
        vector_distances = nodes - coords
        distances = np.asarray([np.hypot(point[0], point[1]) for point in vector_distances])
        sorted_distances = np.argsort(distances)
        nearest = vector_distances[sorted_distances[0]]
        second_nearest = vector_distances[sorted_distances[1]]
        #segment_centre = (nearest + second_nearest)/2
        diff = second_nearest - nearest
        ____, angle = cart2pol(diff)
        #dir_to_centre = atan2(segment_centre[1], segment_centre[0])
        #offset = 180 if dir_to_centre > 0 else -180
        return ((90-degrees(angle))%180) - 90
    
    @classmethod
    def find_nearest_road(Road, coords, close_enough=0, ignore_paths=True):
        distance = inf
        for road in Road.all_roads:
            if road.road_type == 'path' and ignore_paths: continue # Buildings aren't aligned to paths
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
    """
    A building is an extracted OSM building object.
    
    It can be matched to an Arma_building using the match method from Arma_building.
    """
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
            self.building_type = 'city'
        elif building_type in BUILDING_TYPES_COMMERCIAL:
            #TODO: Make unique?
            self.building_type = 'city'
        else:
            self.building_type = 'city'
            # Warn that this was not matched for later
            if building_type not in Building.uses_not_exactly_matched: Building.uses_not_exactly_matched.append(building_type)
        
        self.arma_class = Arma_building.find_suitable_building(width, length, self.building_type)
        
        if self.arma_class != None:
            Building.all_buildings.append(self)
            self.actual_width = Arma_building.all_classes[self.arma_class].width
            self.actual_length = Arma_building.all_classes[self.arma_class].length

    def create_arma_objects(self):
        return [self.arma_class, list(self.centre), self.direction]

class Node_object:
    all_node_objects = []
    def __init__(self, position, direction, object_type):
        self.position = position
        self.direction =  direction
        arma_classes = NODE_OBJECT_TYPES[object_type]
        if isinstance(arma_classes, str): arma_classes = (arma_classes, )
        self.arma_class = arma_classes[random.randint(0, len(arma_classes) - 1)]
        Node_object.all_node_objects.append(self)

    def create_arma_objects(self):
        return [self.arma_class, list(self.position), self.direction]

def cart2pol(coords):
    dist = np.sqrt(coords[0]**2 + coords[1]**2)
    angle = np.arctan2(coords[1], coords[0])
    return dist, angle

def pol2cart(angle, dist):
    x = dist * np.cos(angle)
    y = dist * np.sin(angle)
    return np.asarray([x, y])

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
    print("Converting nodes")
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
    progress_bar = Progress_bar("Converting nodes" ,len(nodes))
    for node in nodes:
        lat = radians(float(node.attrib['lat']))
        lon = radians(float(node.attrib['lon']))
        x = EARTH_RADIUS*(lon - min_lon)*cos_standard_parallel
        y = EARTH_RADIUS*(lat - min_lat)
        coords = np.asarray([x, y])
        Node(node.attrib['id'], coords)
        progress_bar.update_progress()
    print("Found {} nodes".format(len(Node.nodes_all)))

def convert_highway_lines(root):
    # Convert all highways to classes.
    # A highway is made up of one or more node sets.
    ways = root.findall('way')
    highways = [way for way in ways if way.find(".//*[@k='highway']") is not None]
    all_road_types = []
    all_road_surfaces = []
    print("Found {} highways".format(len(highways)))
    progress_bar = Progress_bar("Converting highways" ,len(highways))
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
        progress_bar.update_progress()
    print("Created {} unique roads. {} are unnamed. {} are named.".format(len(Road.all_roads), len(Road.all_roads) - len(Road.roads_hash), len(Road.roads_hash)))
    print("Unique road types: {}".format(all_road_types))
    print("Unique road surfaces: {}".format(all_road_surfaces))
    print("All unique road types succesfully simplified.")

    print("WARNING: The following road types are not defined and defaulted to 'secondary': {}".format(Road.unmatched_road_types))
    print("WARNING: The following road surfaces are not defined and defaulted to 'paved': {}".format(Road.unmatched_road_surfaces))

def convert_buildings(root):
    # TODO: multithread this
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
    # print("Unique building types: {}".format(building_types))
    # print("Unique amenity types: {}".format(building_amenities))
    # print("Unique buildings uses: {}".format(building_uses))
    
    progress_bar = Progress_bar("Converting buildings" ,len(buildings))
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
        diff_x = max_x - min_x
        diff_y = max_y - min_y
        centreX = (min_x + max_x)/2
        centreY = (min_y + max_y)/2
        centre = np.asarray([centreX, centreY])
        close_enough_distance = 1.5*sqrt(diff_x**2+diff_y**2)
        # If building has an associated street or a nearby street, then find the tangent of the closest segment, else calculate it manually.
        if building_street == 'none' or building_street not in Road.roads_hash.keys():
            distance, street_object = Road.find_nearest_road(centre, close_enough_distance)
        else:
            street_object = Road.roads_hash[building_street]
            vector_distances = street_object.all_nodes_as_coords() - centre
            distances = np.asarray([np.hypot(point[0], point[1]) for point in vector_distances])
            distance = np.min(distances)

        # Is it near a road, if so then use that as direction, if not calculate manually
        if distance < close_enough_distance:
            direction_deg = street_object.get_direction_perp_to_road(centre)
            # TODO: make face road
        else:
            # Average the angles of all nodes that make up this building, return between 0-45 degrees.
            angles = []
            for i, node in enumerate(nodes_coords[:-1]):
                next_node = nodes_coords[i+1]
                diff = next_node -  node
                angle = degrees(np.arctan2(diff[0], diff[1]))%90
                angles.append(angle)
            direction_deg = mean(angles)
        if direction_deg < 0: direction_deg += 360
        direction_to_nearest_45_deg = min(90-direction_deg%90, direction_deg%90)
        width = diff_x * (1-(direction_to_nearest_45_deg/90))
        length = diff_y * (1-(direction_to_nearest_45_deg/90))
        if 45<direction_deg<135 or 315>direction_deg>225:
            a,b = width, length
            width, length = b, a
        Building(centre, direction_deg, width, length, street_object, building_type, uid)
        progress_bar.update_progress()
    print("WARNING: The following building types were not exactly matched and have defaulted to residential/commercial: {}".format(Building.uses_not_exactly_matched))
    print("Done converting buildings")

def convert_node_objects(root):
    print("Converting point objects")
    def get_value(value):
        return value, [x for x in root if x.find(".//*[@v='{}']".format(value)) is not None and len(x.findall('nd')) == 0]
    trees = get_value('tree')
    bins = get_value('waste_basket')
    benches = get_value('bench')
    telephones = get_value('telephone')
    post_boxes = get_value('post_box')
    automated_teller_machines = get_value('atm')
    statues = get_value('statue')
    memorials = get_value('memorial')
    bus_stops = get_value('bus_stop')
    count = sum([len(x[1]) for x in [trees, bins, benches, telephones, post_boxes, automated_teller_machines, statues, memorials, bus_stops]])
    progress_bar = Progress_bar("Converting point objects", count)
    for object_type, object_list in (benches, telephones, post_boxes, automated_teller_machines, statues, memorials, bus_stops):
        for node in object_list:
            node_id = node.attrib['id']
            node_coords = Node.nodes_hash[node_id].coords
            ____, road = Road.find_nearest_road(node_coords, ignore_paths=False)
            direction = road.get_direction_perp_to_road(node_coords)
            Node_object(node_coords, direction, object_type)
            progress_bar.update_progress()
    for object_type, object_list in (trees, bins):
        for node in object_list:
            node_id = node.attrib['id']
            node_coords = Node.nodes_hash[node_id].coords
            direction = random.random()*360
            Node_object(node_coords, direction, object_type)
            progress_bar.update_progress()
    print("Done converting point objects")

def output_all_to_arma_array():
    print("Writing output")
    buildArray = []
    for road in Road.all_roads:
        buildArray.extend(road.create_arma_objects())
    for building in Building.all_buildings:
        buildArray.append(building.create_arma_objects())
    for thing in Node_object.all_node_objects:
        buildArray.append(thing.create_arma_objects())
    with open(r"input_data\fn_createCity.sqf") as c:
        script = c.readlines()
    with open("output.sqf", 'w') as f:
        f.truncate()
        f.writelines([line.replace("[THE_BUILD_ARRAY]", str(buildArray)) for line in script])
    print("Done writing output")
    
def debug_draw_image():
    print("Drawing preview")
    resolution = 16000
    max_x = 0
    max_y = 0
    min_x = inf
    min_y = inf
    for building in Building.all_buildings:
        centre = building.centre
        max_x = max(centre[0], max_x)
        max_y = max(centre[1], max_y)
        min_x = min(centre[0], min_x)
        min_y = min(centre[1], min_y)
    for road in Road.all_roads:
        nodes = road.all_nodes_as_coords()
        for node in nodes:
            max_x = max(node[0], max_x)
            max_y = max(node[1], max_y)
            min_x = min(node[0], min_x)
            min_y = min(node[1], min_y)
    diff_x = max_x-min_x
    diff_y = max_y-min_y
    diff = max(diff_x, diff_y)


    def to_pixels(coords):
        pos_x = coords[0] - min_x
        pos_y =  max_y - coords[1]
        pixel_x = int(((pos_x/diff)*resolution))
        pixel_y = int((pos_y/diff)*resolution)
        assert 0<=pixel_x<=resolution and 0<=pixel_y<=resolution
        return (pixel_x, pixel_y)

    def to_pixel(length):
        pixel_length = int((length/diff)*resolution)
        return pixel_length
    def make_rectangle(l, w, theta, offset=(0,0)):
        c, s = cos(theta), sin(theta)
        rectCoords = [(l/2.0, w/2.0), (l/2.0, -w/2.0), (-l/2.0, -w/2.0), (-l/2.0, w/2.0)]
        return [(c*x-s*y+offset[0], s*x+c*y+offset[1]) for (x,y) in rectCoords]

    img = Image.new('RGB', (resolution, resolution), color='black')
    draw = ImageDraw.Draw(img, 'RGBA')
    for road in Road.all_roads:
        node_sets = road.node_sets_as_coords()
        for node_set in node_sets:
            as_tuples = tuple([tuple(to_pixels(node)) for node in node_set])
            draw.line(as_tuples, fill='white', width=1)
    for building in Building.all_buildings:
        centre = to_pixels(building.centre)
        width = to_pixel(building.width)
        length =  to_pixel(building.length)
        direction = building.direction
        vertices = make_rectangle(length, width, radians(direction+90), tuple(centre))
        draw.polygon(vertices, fill=(255, 0, 0, 125), outline='black')
    for building in Building.all_buildings:
        centre = to_pixels(building.centre)
        width = to_pixel(building.actual_width)
        length =  to_pixel(building.actual_length)
        direction = building.direction
        vertices = make_rectangle(length, width, radians(direction+90), tuple(centre))
        draw.polygon(vertices, fill=(0, 255, 0, 62), outline='black')
    for thing in Node_object.all_node_objects:
        centre = to_pixels(thing.position)
        bottom_left = tuple([p - 2 for p in centre])
        top_right = tuple([p + 2 for p in centre])
        draw.ellipse((bottom_left, top_right), fill=(255, 255, 0), outline='black')
    img.save("output.png")
    print("Done drawing preview")

def main():
    tree = ET.parse(r'xml\map.osm.xml')
    root = tree.getroot()
    define_arma_buildings(biome_blacklist=[])
    define_roads()
    convert_nodes(root)
    convert_highway_lines(root)
    convert_node_objects(root)
    convert_buildings(root)
    output_all_to_arma_array()
    debug_draw_image()

if __name__ == "__main__":
    main()