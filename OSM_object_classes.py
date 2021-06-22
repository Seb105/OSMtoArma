import numpy as np
from arma_to_osm_helpers import cart2pol, pol2cart
from math import degrees, inf
from arma_object_classes import Arma_road, Arma_building, Arma_barrier
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

BUILDING_TYPES_RELIGIOUS = ['place_of_worship', 'cathedral', 'chapel', 'church', 'mosque', 'monastery', 'presbytery', 'religious', 'shrine', 'synagogue', 'temple']
BUILDING_TYPES_INDUSTRIAL = ['industrial', 'warehouse']
BUILDING_TYPES_HOUSE = ['yes', 'house', 'apartments', 'detatched','residential', 'terrace']
BUILDING_TYPES_COMMERCIAL = ['commercial', 'retail', 'cafe', 'restraunt', 'cinema']

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
    road_uids = {}
    unmatched_road_types = []
    unmatched_road_surfaces = []
    unmatched_road_pairs = []
    def __init__(self, name, road_type, surface, nodes, uid, is_lit):
        self.name = name
        self.nodes = [nodes]
        self.uid = uid
        self.is_lit = is_lit
        self.buildings = []
        self.length = 0

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
        Road.road_uids[uid] = self

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

    def calculate_road_length(self):
        length = 0
        node_sets = self.node_sets_as_coords()
        for node_set in node_sets:
            for i, node in enumerate(node_set[0:-1]):
                next_node = node_set[i+1]
                diff = next_node - node
                dist = np.hypot(diff[0], diff[1])
                length += dist
        self.length = length


    def get_direction_perp_to_road(self, coords):
        """
        This function returns the angle perpendicular to the tangent of the closest road section of the given coordinates. Used for aligning a property to the road.

        TODO: Make it so the house faces the road, right now it only faces N/E. Atan2, normalise to 0-360 where 0 = NORTH. Then if > 180, add 180 to output?
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

            # Optimize road searching
            first_diff = nodes[0] - coords
            first_distance = np.hypot(first_diff[0], first_diff[1])
            if first_distance > 2*road.length: continue

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
                if (road_search, road_identifier) not in Road.unmatched_road_pairs:
                    Road.unmatched_road_pairs.append((road_search, road_identifier))
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
            # TODO: reimplement this
            # caps = [start, end]
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
                # TODO: reimplement this
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

class Barrier:
    """
    A Road object is an imported OSM barrier
    City walls, fences hedges etc.
    """
    all_barriers = []
    unmatched_barriers = []
    def __init__(self, barrier_type, nodes, uid):
        self.nodes = nodes
        self.uid = uid
        self.barrier_type = barrier_type

        Barrier.all_barriers.append(self)


    def all_nodes_as_coords(self):
        return [node.coords for node in self.nodes]

    # Create an array of objects that can be used in Arma 3 to create objects. Format [class, pos, dir]
    def create_arma_objects(self):
        nodes = self.all_nodes_as_coords()
        arma_array = []
        # Find the type of segments to use from the road surface and type.
        # If the road type does not exist, try matching just the surface. Throw error if that doesn't exist either
        barriers_search = self.barrier_type
        if barriers_search in Arma_barrier.arma_barrier_match.keys():
            barrier_class = Arma_barrier.arma_barrier_match[barriers_search]
        else:
            raise KeyError("{} cannot be matched to any type of Arma road".format(barriers_search))
        lengths = barrier_class.straights.keys()
        min_road_length = min(lengths)
        for i, node in enumerate(nodes[:-1]):
            next_node = nodes[i+1]
            current_pos = node
            #Vector distance between two points
            diff = next_node - node
            # Distance from this node to next node and angle.
            dist, angle_rad = cart2pol(diff)
            dist_done = 0
            # Subtract from 90 as angle_rad is actually 0 when pointing east, and we want 0 = north.
            angle_deg = 90 - degrees(angle_rad)
            if barrier_class.rotate_90: angle_deg += 90
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
                centre = segement_start + offset/2
                current_pos = segment_end
                dist_done += segment_length
                arma_array.append([barrier_class.straights[segment_length], list(centre), angle_deg])
        return arma_array

class Building:
    """
    A building is an extracted OSM building object.
    
    It can be matched to an Arma_building using the class method from Arma_building.
    """
    all_buildings = []
    uses_not_exactly_matched = []
    def __init__(self, centre, direction, width, length, road_object, building_use, uid, building_class):
        self.uid = uid
        self.centre = centre
        self.direction = direction
        self.width = width
        self.length = length
        self.building_use = building_use
        self.arma_class = building_class
        if road_object is not None:
            road_object.buildings.append(self)
        
        self.arma_class = Arma_building.find_suitable_building(width, length, self.building_use)
        
        if self.arma_class != None:
            Building.all_buildings.append(self)
            self.actual_width = Arma_building.all_classes[self.arma_class].width
            self.actual_length = Arma_building.all_classes[self.arma_class].length

    def create_arma_objects(self):
        return [self.arma_class, list(self.centre), self.direction]

def match_building_type(building_use):
        if building_use in BUILDING_TYPES_RELIGIOUS:
            return "religious"
        elif building_use in BUILDING_TYPES_INDUSTRIAL:
            return 'industrial'
        elif building_use in BUILDING_TYPES_HOUSE:
            return 'city'
        elif building_use in BUILDING_TYPES_COMMERCIAL:
            #TODO: Make unique?
            return 'city'
        else:
            return 'city'