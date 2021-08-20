import xml.etree.ElementTree as ET
from math import degrees, radians, sin, cos, inf
from statistics import mean
import time
import numpy as np
from PIL import Image, ImageDraw
import ast
import random
from arma_object_classes import Arma_barrier, Arma_building, Arma_node_object, define_roads, define_barriers
from OSM_object_classes import Road, Node, Building, Barrier, match_building_type
from arma_to_osm_helpers import Progress_bar, pol2cart
from concurrent.futures import ProcessPoolExecutor
from itertools import repeat
random.seed(1)
tree = ET.parse(r'xml/map.osm.xml')
root = tree.getroot()
EARTH_RADIUS = 6371000

# Clone all the classes for new process threads
def init_process(nodes_all, nodes_hash, all_roads, roads_hash, road_uids, all_arma_sizes, all_arma_classes, building_max_dimensions):
    global Node
    global Road
    global Arma_building
    Node.nodes_all = nodes_all
    Node.nodes_hash = nodes_hash
    Road.all_roads = all_roads
    Road.roads_hash = roads_hash
    Road.road_uids = road_uids
    Arma_building.sizes = all_arma_sizes
    Arma_building.all_classes = all_arma_classes
    Arma_building.max_dimensions = building_max_dimensions

#This has to be in global namespace for threading reasons
def convert_building_to_arma(building):
    uid = building.attrib['id']
    if len(building.findall('nd')) > 1:
        nodes = [Node.nodes_hash[node.attrib['ref']] for node in building.findall("nd")]
    elif building.find(".//*[@role='outer']") is not None:
        outerRefs = building.findall(".//*[@role='outer']")
        nodes = []
        for outerRef in outerRefs:
            outerID = outerRef.attrib['ref']
            outerObject = root.find(".//*[@id='{}']".format(outerID)) 
            if outerObject is None: continue
            nodes.extend([Node.nodes_hash[node.attrib['ref']] for node in outerObject.findall("nd")])
    if len(nodes) == 0:
        print("\nWARNING: Building {} had no nodes? OSM bug probably \n".format(uid))
        return [] # OSM glitch where refernced way doesn't exist?
    building_type = get_sub_object_attrib(building, 'building')
    building_street = get_sub_object_attrib(building, 'addr:street', 'none')
    building_amenity =  get_sub_object_attrib(building, 'amenity', 'none')
    if building_type == 'yes' and building_amenity != 'none':
        building_use = building_amenity
    else:
        building_use = building_type
    building_use  = match_building_type(building_use)
    nodes_coords = [node.coords for node in nodes]
    # Get extents of building
    maxes = np.max(nodes_coords, 0)
    mins = np.min(nodes_coords, 0)
    max_x = maxes[0]
    max_y = maxes[1]
    min_x = mins[0]
    min_y = mins[1]
    diff_x = max_x - min_x
    diff_y = max_y - min_y
    if diff_x == 0 or diff_y == 0:
        print("\nWARNING: Building {} was flat\n".format(uid))
        return [] # Fix infinite loop due to terracing.
    centreX = (min_x + max_x)/2
    centreY = (min_y + max_y)/2
    centre = np.asarray([centreX, centreY])
    close_enough_distance = 2*(diff_x + diff_y)
    # If building has an associated street or a nearby street, then find the tangent of the closest segment, else calculate it manually.
    if building_street == 'none' or building_street not in Road.roads_hash.keys():
        distance, road_object = Road.find_nearest_road(centre, 0)
    else:
        road_object = Road.roads_hash[building_street]
        vector_distances = road_object.all_nodes_as_coords() - centre
        distances = np.asarray([np.hypot(point[0], point[1]) for point in vector_distances])
        distance = np.min(distances)

    # Is it near a road, if so then use that as direction, if not calculate manually
    is_near_road = False
    if distance <= close_enough_distance:
        is_near_road = True
        direction_deg = road_object.get_direction_perp_to_road(centre)
        # TODO: make face road. Right now will always face easterly.
    else:
        # Average the angles of all nodes that make up this building, return between 0-45 degrees.
        angles = []
        for i, node in enumerate(nodes_coords[:-1]):
            next_node = nodes_coords[i+1]
            diff = next_node -  node
            angle = degrees(np.arctan2(diff[0], diff[1]))%90
            angles.append(angle)
        direction_deg = mean(angles)
    # Direction always 0-360. Makes handling stuff easier.
    if direction_deg < 0: direction_deg += 360
    # This is used for actually getting the rectangular length of the building. It is 0 if the building is facing N/E/S/W and 45 for NE/SE/SW/NW.
    direction_to_nearest_45_deg = min(90-direction_deg%90, direction_deg%90)
    cos_nearest_45 = cos(radians((direction_to_nearest_45_deg)))
    # diff_y =  bounding box length
    # (1-(direction_to_nearest_45_deg/90) = If width/length of building is hypotenuse, then this is the adjacent length of the buidling.
    # Divide by cos nearest 45 to get the actual building length/width
    width = (diff_x * (1-(direction_to_nearest_45_deg/90)))/cos_nearest_45
    length = (diff_y * (1-(direction_to_nearest_45_deg/90)))/cos_nearest_45
    # If building is facing NE-SW or SE-NW then the width is actually the length and visa versa.
    if 45<direction_deg<135 or 315>direction_deg>225:
        a,b = width, length
        width, length = b, a
    # Split long buildings apart
    max_width, max_length = Arma_building.max_dimensions
    buildings = []
    def split_building_to_terrace(width, length, centre, direction_deg):
        width = width/3
        centre_change = pol2cart(radians(90-direction_deg+90), width)
        centres = (centre+centre_change, centre, centre-centre_change)
        for centre in centres:
            if width > 2*length:
                split_building_to_terrace(width, length, centre, direction_deg)
            else:
                building_class = Arma_building.find_suitable_building(width, length, building_use)
                buildings.append((centre, direction_deg, width, length, road_object.uid, building_use, uid, building_class))
    def split_city_block(width, length, centre, direction_deg, road_object):
        width = width/3
        length = length/3
        width_change = pol2cart(radians(90-direction_deg+90), width)
        length_change = pol2cart(radians(90-direction_deg), length)
        centres = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i==0 and j==0: continue # Miss centre
                new_centre = centre + i * width_change + j * length_change
                centres.append(new_centre)
        for centre in centres:
            if is_near_road:
                ___, road_object = Road.find_nearest_road(centre, 0)
                direction_deg_new = road_object.get_direction_perp_to_road(centre)
                if not (45<direction_deg<135 or 315>direction_deg>225) and (45<direction_deg_new<135 or 315>direction_deg_new>225):
                    a,b = width, length
                    width, length = b, a
                direction_deg = direction_deg_new
            random_width = width * (0.835 + random.random()/3) 
            random_length = length * (0.835 + random.random()/3) 
            if (max_width>width or max_length>length) or Arma_building.find_suitable_building(width/3.125, length/3.125, building_use) is None:
                building_class = Arma_building.find_suitable_building(random_width, random_length, building_use)
                buildings.append((centre, direction_deg, random_width, random_length, road_object.uid, building_use, uid, building_class))
            else:
                split_city_block(random_width, random_length, centre, direction_deg, road_object)
    # If very wide building, rescursively split it into multiple buildings.
    # If a huge square building, recursively split it into 8 buildings (not including a centre)
    if width > 2*length and building_use == 'city':
        split_building_to_terrace(width, length, centre, direction_deg)
    elif building_use == 'city' and (max_width<width or max_length<length) and Arma_building.find_suitable_building(width/3.125, length/3.125, building_use) is not None:
        split_city_block(width, length, centre, direction_deg, road_object)
    else:
        building_class =  Arma_building.find_suitable_building(width, length, building_use)
        buildings.append((centre, direction_deg, width, length, road_object.uid, building_use, uid, building_class))
    return buildings

# Needs to be in global namespace for threading reasons
def convert_node_to_arma(object_type, node):
    node_id = node.attrib['id']
    if node_id in Node.nodes_hash.keys():
        node_coords = Node.nodes_hash[node_id].coords
    else:
        return None, "WARNING: Node object {} failed to find node".format(node_id), None
    ____, road = Road.find_nearest_road(node_coords, 15, ignore_paths=False)
    direction = road.get_direction_perp_to_road(node_coords)
    return node_coords, direction, object_type

# Convert exported buildings from Arma to classes matchable to OSM building
def define_arma_buildings(path=r"input_data/armaObjects.txt", biome_blacklist=[]):
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

# OSM XML lines come in key:values rather than tag:vakue, so each will have an attribute 'k' and attribute 'v', tag is property.
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
    for road in Road.all_roads:
        road.calculate_road_length()
    print("Created {} unique roads. {} are unnamed. {} are named.".format(len(Road.all_roads), len(Road.all_roads) - len(Road.roads_hash), len(Road.roads_hash)))
    print("Unique road types: {}".format(all_road_types))
    print("Unique road surfaces: {}".format(all_road_surfaces))
    print("All unique road types succesfully simplified.")

    print("WARNING: The following road types are not defined and defaulted to 'secondary': {}".format(Road.unmatched_road_types))
    print("WARNING: The following road surfaces are not defined and defaulted to 'paved': {}".format(Road.unmatched_road_surfaces))

def convert_buildings(root):
    print("Converting buildings")
    buildings = [building for building in root if building.find(".//*[@k='building']") is not None and (building.find(".//*[@role='outer']") is not None or len(building.findall('nd')) > 1)]
    random.shuffle(buildings)
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

    print("Starting multithreading. This may take a while.")

    process_executor = ProcessPoolExecutor(initializer=init_process, initargs=(Node.nodes_all, Node.nodes_hash, Road.all_roads, Road.roads_hash, Road.road_uids, Arma_building.sizes, Arma_building.all_classes, Arma_building.max_dimensions), max_workers=8)
    progress_bar = Progress_bar("Creating buildings", len(buildings))
    results = process_executor.map(convert_building_to_arma, buildings, chunksize=512)
    for buildings in results:
        for centre, direction_deg, width, length, road_object_uid, building_use, uid, building_class in buildings:
            road_object = Road.road_uids[road_object_uid]
            Building(centre, direction_deg, width, length, road_object, building_use, uid, building_class)
        progress_bar.update_progress()
    print("WARNING: The following building types were not exactly matched and have defaulted to residential/commercial: {}".format(Building.uses_not_exactly_matched))
    print("Done converting buildings")

# Converts single point objects, such as trees, benches etc to arma objects.
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
    process_executor = ProcessPoolExecutor(initializer=init_process, initargs=(Node.nodes_all, Node.nodes_hash, Road.all_roads, Road.roads_hash, Road.road_uids, Arma_building.sizes, Arma_building.all_classes, Arma_building.max_dimensions), max_workers=8)
    progress_bar = Progress_bar("Creating node objects", count)
    for object_type, object_list in (benches, telephones, post_boxes, automated_teller_machines, statues, memorials, bus_stops):
        results = process_executor.map(convert_node_to_arma,repeat(object_type), object_list, chunksize=512)
        for node_coords, direction, object_type in results:
            if node_coords is None:
                print(direction)
            else:
                Arma_node_object(node_coords, direction, object_type)
            progress_bar.update_progress()
    for object_type, object_list in (trees, bins):
        for node in object_list:
            node_id = node.attrib['id']
            node_coords = Node.nodes_hash[node_id].coords
            direction = random.random()*360
            Arma_node_object(node_coords, direction, object_type)
            progress_bar.update_progress()
    print("Done converting point objects")

# Convert fences, walls to arma objects.
def convert_barriers(root):
    ways = root.findall('way')
    barriers = [way for way in ways if way.find(".//*[@k='barrier']") is not None]
    print("Found {} barriers".format(len(barriers)))
    barriers_not_processed = []
    for barrier in barriers:
        nodes = [Node.nodes_hash[node.attrib['ref']] for node in barrier.findall("nd")]
        barrier_type = get_sub_object_attrib(barrier, 'barrier')
        if barrier_type in Arma_barrier.arma_barrier_match.keys():
            uid = barrier.attrib['id']
            Barrier(barrier_type, nodes, uid)
        else:
            if barrier_type not in barriers_not_processed: barriers_not_processed.append(barrier_type)
    print("WARNING: The following barrier types are not processed: {}".format(barriers_not_processed))

# Write output file.
def output_all_to_arma_array():
    print("Writing output")
    buildArray = []
    count = sum([len(x) for x in (Road.all_roads, Building.all_buildings, Arma_node_object.all_node_objects, Barrier.all_barriers)])
    progress_bar = Progress_bar("Writing output", count)
    for road in Road.all_roads:
        buildArray.extend(road.create_arma_objects())
        progress_bar.update_progress()
    for road_search, road_identifier in Road.unmatched_road_pairs:
        print("WARNING: Arma Road {} could not be found. Defaulted to {}".format(road_search, road_identifier))
    for building in Building.all_buildings:
        buildArray.append(building.create_arma_objects())
        progress_bar.update_progress()
    for thing in Arma_node_object.all_node_objects:
        buildArray.append(thing.create_arma_objects())
        progress_bar.update_progress()
    for barrier in Barrier.all_barriers:
        buildArray.extend(barrier.create_arma_objects())
        progress_bar.update_progress()
    with open(r"input_data/fn_createCity.sqf") as c:
        script = c.readlines()
    with open(r"output/fn_buildScript.sqf", 'w') as f:
        f.truncate()
        f.writelines([line.replace("[THE_BUILD_ARRAY]", str(buildArray)) for line in script])
    print("Done writing output")

# From created properties draw a debug file.
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
    for barrier in Barrier.all_barriers:
        nodes = barrier.all_nodes_as_coords()
        for node in nodes:
            max_x = max(node[0], max_x)
            max_y = max(node[1], max_y)
            min_x = min(node[0], min_x)
            min_y = min(node[1], min_y)
    for node_object in Arma_node_object.all_node_objects:
        node = node_object.position
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
    for thing in Arma_node_object.all_node_objects:
        centre = to_pixels(thing.position)
        bottom_left = tuple([p - 2 for p in centre])
        top_right = tuple([p + 2 for p in centre])
        draw.ellipse((bottom_left, top_right), fill=(255, 255, 0), outline='black')
    for barrier in Barrier.all_barriers:
        nodes =  barrier.all_nodes_as_coords()
        as_tuples = tuple([tuple(to_pixels(node)) for node in nodes])
        draw.line(as_tuples, fill='brown', width=2)
    img.save(r"output/preview.png")
    print("Done drawing preview")

def main():
    start_time = time.time()
    # Default blacklistable: ['middle_east', 'mediterranean', 'misc', 'asia_modern', 'east_europe]
    define_arma_buildings(biome_blacklist=['mediterranean', 'middle_east', 'misc', 'asia_modern'])
    define_roads()
    define_barriers()
    convert_nodes(root)
    convert_highway_lines(root)
    convert_node_objects(root)
    convert_buildings(root)
    convert_barriers(root)
    output_all_to_arma_array()
    debug_draw_image()
    end_time = time.time()
    print("Took {} seconds for conversion".format(round(end_time - start_time)))

if __name__ == "__main__":
    main()