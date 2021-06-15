import xml.etree.ElementTree as ET
from math import atan, degrees, radians, sin, sqrt, tan, cos
from OSGridConverter import latlong2grid
tree = ET.parse(r'xml\map.osm.xml')
root = tree.getroot()
import numpy as np


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
        print("Created building at {0} at angle {1} and area of {2} with nodes: {3}".format(self.centre, self.angle, self.area, self.nodes))
        
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

print("Finding buildings and nodes")
buildings = find_buildings(root)
nodes = find_nodes(root)
minX = 9999999999
minY = 9999999999
print("Converting polar to OS")
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
print("Building classes")
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
    buildings[building] = {'nodes' : building_nodes}
    Building(building, building_nodes)

ArmaBuildings = [
    ["Land_DeerStand_01_F",2.59886,6.28295,16.3285],["Land_Chapel_V1_F",25.1245,11.1802,280.898],["Land_Chapel_Small_V1_F",10.2299,4.8312,49.4229],["Land_LampAirport_off_F",3.67955,2.65154,9.75646],["Land_LampAirport_F",3.68039,2.65652,9.77702],["Land_Offices_01_V1_F",35.5418,28.5798,1015.78],["Land_u_Addon_01_V1_F",12.9945,9.01308,117.121],["Land_i_Addon_02_V1_F",9.08004,9.88255,89.7339],["Land_i_Garage_V1_F",17.9996,7.38,132.837],["Land_i_Garage_V2_F",17.9996,7.38,132.837],["Land_i_House_Big_01_V1_F",15.7869,16.9651,267.827],["Land_i_House_Big_01_V2_F",15.7869,16.9651,267.827],["Land_i_House_Big_01_V3_F",15.7869,16.9651,267.827],["Land_u_House_Big_01_V1_F",15.7869,16.9651,267.827],["Land_i_House_Big_02_V1_F",10.6575,24.1829,257.729],["Land_i_House_Big_02_V2_F",10.6575,24.1829,257.729],["Land_i_House_Big_02_V3_F",10.6575,24.1829,257.729],["Land_u_House_Big_02_V1_F",10.5465,24.1829,255.046],["Land_i_Shop_01_V1_F",9.50362,20.2661,192.601],["Land_i_Shop_01_V2_F",9.50362,19.5814,186.094],["Land_i_Shop_01_V3_F",9.50362,20.2661,192.601],["Land_u_Shop_01_V1_F",9.50044,20.2661,192.537],["Land_i_Shop_02_V1_F",17.1573,10.8809,186.687],["Land_i_Shop_02_V2_F",17.1573,10.8809,186.687],["Land_i_Shop_02_V3_F",17.1573,10.8809,186.687],["Land_u_Shop_02_V1_F",17.1197,10.8809,186.277],["Land_i_House_Small_01_V1_F",10.8686,15.2865,166.142],["Land_i_House_Small_01_V2_F",10.8686,15.2865,166.142],["Land_i_House_Small_01_V3_F",10.8686,15.2865,166.142],["Land_u_House_Small_01_V1_F",11.2038,15.2865,171.266],["Land_i_House_Small_02_V1_F",16.4065,9.28948,152.408],["Land_i_House_Small_02_V2_F",16.4065,9.28948,152.408],["Land_i_House_Small_02_V3_F",16.4065,9.28948,152.408],["Land_u_House_Small_02_V1_F",16.3985,9.28948,152.334],["Land_i_House_Small_03_V1_F",12.401,18.5387,229.897],["Land_Slum_House02_F",7.57338,8.83605,66.9187],["Land_i_Stone_HouseBig_V1_F",13.5694,12.3194,167.167],["Land_i_Stone_HouseBig_V2_F",13.5694,12.3194,167.167],["Land_i_Stone_HouseBig_V3_F",13.5694,12.3194,167.167],["Land_i_Stone_Shed_V1_F",9.0647,9.91131,89.8431],["Land_i_Stone_Shed_V2_F",9.0647,9.91131,89.8431],["Land_i_Stone_Shed_V3_F",9.0647,9.91131,89.8431],["Land_i_Stone_HouseSmall_V1_F",20.4124,11.6361,237.52],["Land_i_Stone_HouseSmall_V2_F",20.4124,11.6361,237.52],["Land_i_Stone_HouseSmall_V3_F",20.4124,11.6361,237.52],["Land_Airport_Tower_F",10.9142,15.837,172.848],["Land_CarService_F",11.7837,22.2659,262.375],["Land_cmp_Shed_F",11.607,7.65184,88.8151],["Land_FuelStation_Build_F",7.63554,8.66433,66.1568],["Land_i_Shed_Ind_F",32.9415,18.781,618.675],["Land_spp_Tower_F",12.1304,9.04931,109.772],["Land_TTowerBig_1_F",16.9496,16.8498,285.597],["Land_TTowerBig_2_F",8.01202,8.81394,70.6175],["Land_i_Barracks_V1_F",38.7341,25.314,980.515],["Land_i_Barracks_V2_F",38.7341,25.314,980.515],["Land_u_Barracks_V2_F",36.6147,25.314,926.865],["Land_MilOffices_V1_F",36.0532,30.8228,1111.26],["Land_Caravan_01_rust_F",2.7922,12.9612,36.1903],["Land_TentHangar_V1_F",21.4878,25.8224,554.867],["Land_CombineHarvester_01_wreck_F",3.6231,7.74055,28.0448],["Land_GarageShelter_01_F",11.6746,15.0146,175.289],["Land_House_Big_01_F",17.0329,16.2912,277.486],["Land_House_Big_02_F",32.3112,26.9924,872.157],["Land_House_Big_03_F",36.1531,15.5634,562.665],["Land_House_Big_04_F",28.0872,17.9375,503.813],["Land_House_Big_05_F",22.0272,15.0456,331.414],["Land_House_Native_01_F",16.074,10.0833,162.079],["Land_House_Native_02_F",10.7255,8.20301,87.9812],["Land_House_Small_01_F",14.4986,17.0245,246.832],["Land_House_Small_02_F",11.2901,14.438,163.007],["Land_House_Small_03_F",15.2209,12.5698,191.323],["Land_House_Small_04_F",14.9744,18.7541,280.832],["Land_House_Small_05_F",16.5681,11.8582,196.468],["Land_House_Small_06_F",16.8159,12.0663,202.906],["Land_School_01_F",33.9548,16.0473,544.883],["Land_Shed_01_F",6.12006,4.71479,28.8548],["Land_Shed_02_F",4.75119,6.16625,29.297],["Land_Shed_03_F",6.91778,4.51711,31.2484],["Land_Shed_04_F",1.99326,3.24812,6.47435],["Land_Shed_05_F",7.27864,6.77387,49.3045],["Land_Shed_06_F",7.61943,10.5673,80.517],["Land_Shed_07_F",10.4983,5.92065,62.1565],["Land_Slum_01_F",11.8566,5.76483,68.3514],["Land_Slum_02_F",9.93849,11.5124,114.416],["Land_Slum_03_F",15.3873,17.4331,268.248],["Land_Slum_04_F",11.5145,12.9413,149.013],["Land_Slum_05_F",11.5726,12.52,144.889],["Land_Addon_01_F",6.17282,10.1316,62.5406],["Land_Addon_02_F",7.4773,10.1635,75.9959],["Land_Addon_03_F",6.67497,17.2001,114.81],["Land_Addon_04_F",14.103,17.6597,249.055],["Land_Addon_05_F",11.451,21.5956,247.292],["Land_FuelStation_01_arrow_F",1.28411,0.545564,0.700565],["Land_FuelStation_01_prices_F",2.54934,1.0831,2.7612],["Land_FuelStation_01_pump_F",1.19335,1.22202,1.4583],["Land_FuelStation_01_roof_F",20.06,20,401.2],["Land_FuelStation_01_shop_F",16.3457,20.0769,328.171],["Land_FuelStation_01_workshop_F",15.6096,19.0338,297.11],["Land_FuelStation_02_workshop_F",11.7837,22.2659,262.375],["Land_Hotel_01_F",18.604,18.7043,347.974],["Land_Hotel_02_F",26.4756,34.1198,903.345],["Land_MultistoryBuilding_01_F",46.4313,43.2387,2007.63],["Land_MultistoryBuilding_03_F",25.7994,34.3996,887.489],["Land_MultistoryBuilding_04_F",32.1027,32.3643,1038.98],["Land_Shop_City_01_F",25.1681,14.9432,376.093],["Land_Shop_City_02_F",25.4224,26.7368,679.713],["Land_Shop_City_03_F",16.9467,28.0982,476.171],["Land_Shop_City_04_F",18.5177,26.5523,491.688],["Land_Shop_City_05_F",22.4233,34.93,783.246],["Land_Shop_City_06_F",25.8982,25.5047,660.525],["Land_Shop_City_07_F",10.9589,20.3041,222.511],["Land_Shop_Town_01_F",11.2705,21.3017,240.081],["Land_Shop_Town_02_F",14.3117,18.5264,265.144],["Land_Shop_Town_03_F",18.07,25.8489,467.09],["Land_Shop_Town_04_F",10.6252,18.8046,199.802],["Land_Shed_12_F",2.96437,9.98941,29.6123],["Land_Shop_Town_05_F",22.3496,20.9483,468.185],["Land_Shop_Town_05_addon_F",8.951,3.83922,34.3649],["Land_Supermarket_01_F",17.2436,28.3771,489.324],["Land_Warehouse_03_F",23.3287,19.6043,457.342],["Land_Cathedral_01_F",37.0245,50.1683,1857.46],["Land_Mausoleum_01_F",9.44064,9.432,89.0441],["Land_Church_01_F",19.9099,33.7458,671.876],["Land_Church_02_F",14.6791,42.4225,622.725],["Land_Church_03_F",16.8436,20.4255,344.04],["Land_Temple_Native_01_F",19.6252,27.6484,542.606],["Land_GuardHouse_01_F",11.7436,11.6776,137.137],["Land_SM_01_shed_F",32.9415,18.781,618.675],["Land_Airport_01_controlTower_F",10.3536,10.8855,112.704],["Land_Airport_01_hangar_F",42.3519,39.2176,1660.94],["Land_Airport_01_terminal_F",33.0087,23.3369,770.319],["Land_Airport_02_controlTower_F",9.67602,19.2093,185.869],["Land_Airport_02_terminal_F",48.2979,28.8931,1395.47],["Land_Barracks_01_camo_F",38.7341,25.314,980.515],["Land_Barracks_01_grey_F",38.7341,25.314,980.515],["Land_Barracks_01_dilapidated_F",36.6147,25.314,926.865],["Land_i_Addon_02_b_white_F",13.9136,8.81176,122.604],["Land_i_House_Big_01_b_blue_F",15.7869,16.8099,265.377],["Land_i_House_Big_01_b_brown_F",15.7869,16.8099,265.377],["Land_i_House_Big_01_b_pink_F",15.7869,16.8099,265.377],["Land_i_House_Big_01_b_white_F",15.7869,16.8099,265.377],["Land_i_House_Big_01_b_whiteblue_F",15.7869,16.8099,265.377],["Land_i_House_Big_01_b_yellow_F",15.7869,16.8099,265.377],["Land_i_House_Big_02_b_blue_F",10.6575,24.1829,257.729],["Land_i_House_Big_02_b_brown_F",10.6575,24.1829,257.729],["Land_i_House_Big_02_b_pink_F",10.6575,24.1829,257.729],["Land_i_House_Big_02_b_white_F",10.6575,24.1829,257.729],["Land_i_House_Big_02_b_whiteblue_F",10.6575,24.1829,257.729],["Land_i_House_Big_02_b_yellow_F",10.6575,24.1829,257.729],["Land_i_House_Small_01_b_blue_F",10.8686,15.2865,166.142],["Land_i_House_Small_01_b_brown_F",10.8686,15.2865,166.142],["Land_i_House_Small_01_b_pink_F",10.8686,15.2865,166.142],["Land_i_House_Small_01_b_white_F",10.8686,15.2865,166.142],["Land_i_House_Small_01_b_whiteblue_F",10.8686,15.2865,166.142],["Land_i_House_Small_01_b_yellow_F",10.8686,15.2865,166.142],["Land_i_House_Small_02_b_blue_F",20.2627,9.10882,184.57],["Land_i_House_Small_02_b_brown_F",20.2627,9.10882,184.57],["Land_i_House_Small_02_b_pink_F",20.2627,9.10882,184.57],["Land_i_House_Small_02_b_white_F",20.2627,9.10882,184.57],["Land_i_House_Small_02_b_whiteblue_F",20.2627,9.10882,184.57],["Land_i_House_Small_02_b_yellow_F",20.2627,9.10882,184.57],["Land_i_House_Small_02_c_blue_F",20.2627,9.10882,184.57],["Land_i_House_Small_02_c_brown_F",20.2627,9.10882,184.57],["Land_Church_04_yellow_damaged_F",16.4798,33.7621,556.391],["Land_i_House_Small_02_c_pink_F",20.2627,9.10882,184.57],["Land_i_House_Small_02_c_white_F",20.2627,9.10882,184.57],["Land_i_House_Small_02_c_whiteblue_F",20.2627,9.10882,184.57],["Land_i_House_Small_02_c_yellow_F",20.2627,9.10882,184.57],["Land_i_Stone_House_Big_01_b_clay_F",13.5694,12.3194,167.167],["Land_i_Stone_Shed_01_b_clay_F",13.8156,9.91131,136.93],["Land_i_Stone_Shed_01_b_raw_F",13.8156,9.91131,136.93],["Land_i_Stone_Shed_01_b_white_F",13.8156,9.91131,136.93],["Land_i_Stone_Shed_01_c_clay_F",13.8156,9.91131,136.93],["Land_i_Stone_Shed_01_c_raw_F",13.8156,9.91131,136.93],["Land_i_Stone_Shed_01_c_white_F",13.8156,9.91131,136.93],["Land_FuelStation_01_prices_malevil_F",2.54934,1.0831,2.7612],["Land_FuelStation_01_pump_malevil_F",1.19335,1.22202,1.4583],["Land_FuelStation_01_roof_malevil_F",20.06,20,401.2],["Land_i_Shop_02_b_blue_F",17.1573,10.8809,186.687],["Land_i_Shop_02_b_brown_F",17.1573,10.8809,186.687],["Land_i_Shop_02_b_pink_F",17.1573,10.8809,186.687],["Land_i_Shop_02_b_white_F",17.1573,10.8809,186.687],["Land_i_Shop_02_b_whiteblue_F",17.1573,10.8809,186.687],["Land_i_Shop_02_b_yellow_F",17.1573,10.8809,186.687],["Land_Supermarket_01_malden_F",17.2436,28.3771,489.324],["Land_Barn_01_brown_F",35.1886,25.6271,901.783],["Land_Barn_01_grey_F",35.1886,25.6271,901.783],["Land_FeedShack_01_F",11.3694,4.50292,51.1953],["Land_DeerStand_02_F",3.89101,7.07349,27.523],["Land_PortableLight_02_single_olive_F",0.306938,0.342523,0.105133],["Land_PortableLight_02_single_yellow_F",0.306938,0.342523,0.105133],["Land_PortableLight_02_single_black_F",0.306938,0.342523,0.105133],["Land_PortableLight_02_single_sand_F",0.306938,0.342523,0.105133],["Land_PortableLight_02_double_olive_F",0.560242,0.240968,0.135],["Land_PortableLight_02_double_yellow_F",0.560242,0.240968,0.135],["Land_PortableLight_02_double_black_F",0.560242,0.240968,0.135],["Land_PortableLight_02_double_sand_F",0.560242,0.240968,0.135],["Land_PortableLight_02_quad_olive_F",0.560242,0.243792,0.136583],["Land_PortableLight_02_quad_yellow_F",0.560242,0.243792,0.136583],["Land_PortableLight_02_quad_black_F",0.560242,0.243792,0.136583],["Land_PortableLight_02_quad_sand_F",0.560242,0.243792,0.136583],["Land_PortableLight_02_folded_olive_F",0.430716,0.231759,0.0998222],["Land_PortableLight_02_folded_yellow_F",0.430716,0.231759,0.0998222],["Land_PortableLight_02_folded_black_F",0.430716,0.231759,0.0998222],["Land_PortableLight_02_folded_sand_F",0.430716,0.231759,0.0998222],["Land_PortableLight_02_single_folded_olive_F",0.149026,0.38957,0.058056],["Land_PortableLight_02_single_folded_yellow_F",0.149026,0.38957,0.058056],["Land_PortableLight_02_single_folded_black_F",0.149026,0.38957,0.058056],["Land_PortableLight_02_single_folded_sand_F",0.149026,0.38957,0.058056],["Land_TentLamp_01_suspended_F",0.109421,0.615993,0.0674023],["Land_TentLamp_01_standing_F",0.322469,0.44026,0.14197],["Land_TentLamp_01_suspended_red_F",0.109421,0.615993,0.0674023],["Land_TentLamp_01_standing_red_F",0.322469,0.44026,0.14197],["Land_Camp_House_01_brown_F",7.6295,14.8663,113.423],["Land_Caravan_01_green_F",2.34496,9.6415,22.6089],["Land_House_1B01_F",17.8576,23.4467,418.702],["Land_House_1W01_F",11.8687,13.531,160.596],["Land_House_1W02_F",12.5492,14.4129,180.87],["Land_House_1W03_F",8.99603,18.0952,162.785],["Land_House_1W04_F",11.7879,19.4508,229.285],["Land_House_1W05_F",12.8921,16.479,212.45],["Land_Greenhouse_01_F",5.68997,4.23187,24.0792],["Land_House_1W06_F",12.4149,16.5235,205.138],["Land_House_1W07_F",17.4538,19.0982,333.336],["Land_House_1W08_F",15.63,10.1706,158.967],["Land_House_1W09_F",15.3647,10.1624,156.142],["Land_House_1W10_F",12.6238,10.2474,129.361],["Land_House_1W11_F",17.2587,14.483,249.957],["Land_House_1W12_F",19.654,20.6619,406.089],["Land_House_1W13_F",9.50405,16.0815,152.839],["Land_House_2B01_F",17.7067,11.7725,208.452],["Land_House_2B02_F",25.4097,26.7781,680.424],["Land_House_2B03_F",31.1118,28.3106,880.795],["Land_House_2B04_F",18.7474,26.0283,487.962],["Land_House_2W01_F",17.0495,19.5777,333.79],["Land_House_2W02_F",20.4256,10.7747,220.079],["Land_House_2W03_F",21.1218,16.1098,340.268],["Land_House_2W04_F",23.9722,16.5524,396.797],["Land_House_2W05_F",18.5578,23.7092,439.992],["Land_HealthCenter_01_F",29.2735,30.2772,886.32],["Land_PoliceStation_01_F",23.9323,16.0317,383.676],["Land_Shed_09_F",5.48325,7.0834,38.84],["Land_Shed_10_F",8.8935,5.93546,52.787],["Land_Shed_11_F",5.7621,7.63825,44.0123],["Land_Shed_13_F",10.7502,3.59757,38.6746],["Land_Shed_14_F",6.65336,13.8055,91.8527],["Land_FuelStation_03_prices_F",0.476601,1.19101,0.567636],["Land_FuelStation_03_pump_F",1.09052,0.376118,0.410165],["Land_FuelStation_03_roof_F",18.5954,12.418,230.917],["Land_FuelStation_03_shop_F",7.63554,10.1945,77.8408],["Land_VillageStore_01_F",17.2752,19.5702,338.079],["Land_Chapel_01_F",10.0979,5.96232,60.2071],["Land_Chapel_02_white_F",4.19647,6.82578,28.6442],["Land_Chapel_02_yellow_F",4.19647,6.82578,28.6442],["Land_Chapel_02_white_damaged_F",4.20221,6.82578,28.6833],["Land_Chapel_02_yellow_damaged_F",4.20221,6.82578,28.6833],["Land_Church_04_lightblue_F",16.4798,33.7621,556.391],["Land_Church_04_lightblue_damaged_F",16.4798,33.7621,556.391],["Land_Church_04_lightyellow_F",16.4798,33.7621,556.391],["Land_Church_04_lightyellow_damaged_F",16.4798,33.7621,556.391],["Land_Church_04_red_F",16.4798,33.7621,556.391],["Land_Church_04_red_damaged_F",16.4798,33.7621,556.391],["Land_Church_04_white_F",16.4798,33.7621,556.391],["Land_Church_04_white_damaged_F",16.4798,33.7621,556.391],["Land_Church_04_white_red_F",16.4798,33.7621,556.391],["Land_Church_04_white_red_damaged_F",16.4798,33.7621,556.391],["Land_Church_04_yellow_F",16.4798,33.7621,556.391],["Land_Church_04_small_lightblue_F",16.4798,26.8728,442.857],["Land_Church_04_small_lightblue_damaged_F",16.4798,26.8728,442.857],["Land_Church_04_small_lightyellow_F",16.4798,26.8728,442.857],["Land_Church_04_small_lightyellow_damaged_F",16.4798,26.8728,442.857],["Land_Church_04_small_red_F",16.4798,26.8728,442.857],["Land_Church_04_small_red_damaged_F",16.4798,26.8728,442.857],["Land_Church_04_small_white_F",16.4798,26.8728,442.857],["Land_Church_04_small_white_damaged_F",16.4798,26.8728,442.857],["Land_Rail_Warehouse_Small_F",26.1697,11.296,295.613],["Land_Church_04_small_white_red_F",16.4798,26.8728,442.857],["Land_Church_04_small_white_red_damaged_F",16.4798,26.8728,442.857],["Land_Church_04_small_yellow_F",16.4798,26.8728,442.857],["Land_Church_04_small_yellow_damaged_F",16.4798,26.8728,442.857],["Land_Church_05_F",17.4693,13.6965,239.268],["Land_OrthodoxChurch_02_F",28.9805,17.7496,514.393],["Land_OrthodoxChurch_03_F",36.8301,20.7342,763.643],["Land_FeedStorage_01_F",2.93607,4.19325,12.3117],["Land_CementWorks_01_brick_F",36.7431,56.414,2072.83],["Land_CementWorks_01_grey_F",37.1946,56.4318,2098.96],["Land_CoalPlant_01_MainBuilding_F",49.7894,43.7236,2176.97],["Land_Barn_02_F",22.3095,15.7565,351.519],["Land_Barn_03_small_F",17.1943,30.0363,516.451],["Land_Barn_03_large_F",22.741,56.0172,1273.89],["Land_Barn_04_F",36.9042,59.6114,2199.91],["Land_StrawStack_01_F",20.698,9.15197,189.428],["Land_WaterTower_02_F",18.4257,20.7716,382.73],["Land_Cowshed_01_A_F",36.9802,26.8447,992.72],["Land_Cowshed_01_B_F",26.9882,9.80874,264.72],["Land_Cowshed_01_C_F",14.2436,15.1078,215.189],["Land_Greenhouse_01_damaged_F",5.68997,4.23187,24.0792],["Land_GarageOffice_01_F",7.59621,17.9957,136.699],["Land_GarageRow_01_large_F",27.5572,24.5905,677.647],["Land_GarageRow_01_small_F",16.0403,14.2976,229.337],["Land_Factory_02_F",48.8312,29.2746,1429.51],["Land_WaterStation_01_F",5.92313,12.3152,72.9442],["Land_Workshop_01_F",11.1461,12.8016,142.688],["Land_Workshop_01_grey_F",11.1461,12.8016,142.688],["Land_Workshop_02_F",16.6192,10.8098,179.65],["Land_Workshop_02_grey_F",16.6192,10.8098,179.65],["Land_Workshop_03_F",17.322,13.2426,229.389],["Land_Workshop_03_grey_F",17.322,13.2426,229.389],["Land_Workshop_04_F",16.9213,15.6242,264.381],["Land_Workshop_04_grey_F",16.9213,15.6242,264.381],["Land_Workshop_05_F",13.4628,18.3863,247.532],["Land_Workshop_05_grey_F",13.4628,18.3863,247.532],["Land_PowerStation_01_F",17.9046,20.5482,367.908],["Land_Substation_01_F",3.58544,9.35762,33.5512],["Land_Sawmill_01_F",27.1297,40.3162,1093.77],["Land_IndustrialShed_01_F",12.1418,34.1123,414.184],["Land_i_Shed_Ind_old_F",32.9415,18.781,618.675],["Land_Smokestack_01_F",21.7441,14.6893,319.406],["Land_Smokestack_01_factory_F",21.7441,14.6893,319.406],["Land_Smokestack_02_F",8,9.55184,76.4147],["Land_Smokestack_03_F",6.8354,7.03766,48.1052],["Land_Rail_Station_Big_F",28.1414,23.3566,657.288],["Land_ServiceHangar_01_L_F",56.8913,62.9825,3583.16],["Land_ServiceHangar_01_R_F",56.6427,62.9329,3564.69],["Land_ControlTower_02_F",21.9594,13.1984,289.83],["Land_GuardBox_01_green_F",2.64557,4.47481,11.8384],["Land_GuardBox_01_brown_F",2.64557,4.47481,11.8384],["Land_GuardBox_01_smooth_F",2.64557,4.47481,11.8384],["Reflector_Cone_01_white_F",8.93501e-006,0.0590016,5.2718e-007],["Land_ControlTower_01_F",10.1492,10.1181,102.691],["Land_Barracks_02_F",22.0147,11.1161,244.718],["Land_Barracks_03_F",25.1347,8.59003,215.908],["Land_Barracks_04_F",18.7839,19.2686,361.939],["Land_Barracks_05_F",20.0386,7.87601,157.824],["Land_Barracks_06_F",32.7547,20.7042,678.159],["Land_GuardHouse_02_F",12.4651,9.1657,114.251],["Land_GuardHouse_02_grey_F",12.4651,9.1657,114.251],["Land_GuardHouse_03_F",13.8414,10.8421,150.069],["Land_GuardTower_01_F",5.9797,16.0083,95.725],["Land_GuardTower_02_F",3.16319,6.26303,19.8112],["Land_Radar_01_airshaft_F",2.54338,2.54886,6.48272],["Land_Radar_01_cooler_F",8.54837,8.96347,76.6231],["Land_Radar_01_antenna_F",44.0221,36.0288,1586.06],["Land_Radar_01_antenna_base_F",50.3048,26.5868,1337.44],["Land_Radar_01_kitchen_F",17.5895,31.5386,554.749],["Land_Radar_01_HQ_F",22.8515,26.4499,604.419],["Land_MobileRadar_01_generator_F",2.83719,5.92266,16.8037],["Land_MobileRadar_01_radar_F",13.9682,17.44,243.605],["Land_ShootingPos_Roof_01_F",7.80445,3.27248,25.5399],["Reflector_Cone_01_orange_F",8.93501e-006,0.0590016,5.2718e-007],["Reflector_Cone_01_red_F",8.93501e-006,0.0590016,5.2718e-007],["Reflector_Cone_01_green_F",8.93501e-006,0.0590016,5.2718e-007],["Reflector_Cone_01_blue_F",8.93501e-006,0.0590016,5.2718e-007],["Reflector_Cone_01_narrow_white_F",8.93501e-006,0.0590016,5.2718e-007],["Reflector_Cone_01_narrow_orange_F",8.93501e-006,0.0590016,5.2718e-007],["Reflector_Cone_01_narrow_red_F",8.93501e-006,0.0590016,5.2718e-007],["Reflector_Cone_01_narrow_green_F",8.93501e-006,0.0590016,5.2718e-007],["Reflector_Cone_01_narrow_blue_F",8.93501e-006,0.0590016,5.2718e-007],["Reflector_Cone_01_wide_white_F",8.93501e-006,0.0590016,5.2718e-007],["Reflector_Cone_01_wide_orange_F",8.93501e-006,0.0590016,5.2718e-007],["Reflector_Cone_01_wide_red_F",8.93501e-006,0.0590016,5.2718e-007],["Reflector_Cone_01_wide_green_F",8.93501e-006,0.0590016,5.2718e-007],["Reflector_Cone_01_wide_blue_F",8.93501e-006,0.0590016,5.2718e-007],["Reflector_Cone_01_Long_white_F",8.93501e-006,0.0590016,5.2718e-007],["Reflector_Cone_01_Long_orange_F",8.93501e-006,0.0590016,5.2718e-007],["Reflector_Cone_01_Long_red_F",8.93501e-006,0.0590016,5.2718e-007],["Reflector_Cone_01_Long_green_F",8.93501e-006,0.0590016,5.2718e-007],["Reflector_Cone_01_Long_blue_F",8.93501e-006,0.0590016,5.2718e-007]]

print("Finding Arma match")
for building in Building.all_buildings:
    rating = 0
    prevRating = 0
    for armaBuilding in ArmaBuildings:
        classStr, width, length, area = tuple(armaBuilding)
        diffW = abs(width - building.width)
        diffL = abs(width - building.length)
        diffA = abs(width - building.area)
        rating = 1/(diffW + diffL + diffA)
        if rating > prevRating:
            prevRating = rating
            building.armaClass = classStr
print("Outputting")
build_array = []
for b in Building.all_buildings:
    build_array.append([b.armaClass, b.centre, b.angle])
with open("output.txt", 'w') as f:
    f.truncate()
    f.write(str(build_array))