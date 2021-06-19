import random
from arma_to_osm_helpers import nearest_value

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


class Arma_road:
    """
    An arma road is a collection of arma road segment classes with some identifying properties such as segment length, turning radius and turning angle, 
    
    These segments may be used to convert an OSM way into arma classes.
    """
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

class Arma_node_object:
    """
    An Arma node object is a node which represents a single object, like a bench or rubbish bin.
    """
    all_node_objects = []
    def __init__(self, position, direction, object_type):
        self.position = position
        self.direction =  direction
        arma_classes = NODE_OBJECT_TYPES[object_type]
        if isinstance(arma_classes, str): arma_classes = (arma_classes, )
        self.arma_class = arma_classes[random.randint(0, len(arma_classes) - 1)]
        Arma_node_object.all_node_objects.append(self)

    def create_arma_objects(self):
        return [self.arma_class, list(self.position), self.direction]

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
