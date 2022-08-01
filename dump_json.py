from arma_object_classes import define_roads, Arma_road
import json
def main():
    define_roads()
    json_dump = {}
    for key, value in Arma_road.arma_road_match.items():
        stuff = {}
        new_key = f"{key[0]},{key[1]}"
        stuff["surfaces"] = value.surfaces
        stuff["usages"] = value.road_types
        stuff["straights"] = value.straights
        stuff["curves"] = value.curves
        stuff["end"] = value.end
        stuff["place_at_centre"] = value.placeCentre
        json_dump[new_key] = stuff
    print(json_dump)
    with open('roads.json', 'w') as outfile:
        json.dump(json_dump, outfile)

if __name__ == "__main__":
    main()
