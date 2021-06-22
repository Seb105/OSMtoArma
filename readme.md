## OpenStreetMap to Arma build script


Requires [CUP Terrains - Core](https://steamcommunity.com/workshop/filedetails/?id=583496184) and [CUP Terrains - Maps](https://steamcommunity.com/sharedfiles/filedetails/?id=583544987).

Requires [Python3](https://www.python.org/downloads/) and [pillow](https://pypi.org/project/Pillow/)

Will convert any [OpenStreetMap](https://www.openstreetmap.org/search?query=rome#map=14/41.8914/12.4876) exported XML file to a build script for ArmA.
If in 3den, the objects will be placed as 3den objects.
If in a mission, they will be spawned normally.
It will also create an image approximaton of the output (for debug purposes)

Central Rome/The Vatican:
![Rome/TheVatican](https://raw.githubusercontent.com/Seb105/OSMtoArma/main/images/rome_vatican.jpg)
Vladivostok:
![Vladivostok](https://raw.githubusercontent.com/Seb105/OSMtoArma/main/images/vladivostok.jpg)


# Basic usage:

Place an exported OSM file into the ```xml``` directory with the name ```map.osm.xml``` and run main.py. Use the file ```output\fn_buildScript.sqf``` in-game to create your map.

### Choosing map theme

You may edit the arguments of the function ```define_arma_buildings``` in main() in order to choose the biome. Default biomes in ```input_data\armaObjects.txt``` are:
- 'mediterranean'
    - (Altis/Malden)
- 'asia_modern' 
    - (Tanoa)
- 'eastern_europe'
    - (Chernarus, etc)
- 'middle_east'
    - (Takistan/Zargabad)
- 'misc' (extra CUP stuff, generally ugly and low quality)

Theme selection is done by blacklisting biomes.

For example, if you wanted a purely Mediterranean themed map your call would look like: 

```define_arma_buildings(biome_blacklist=['middle_east', 'east_europe', 'misc', 'asia_modern'])```

## Advanced usage:

### Defining custom objects

You may add your own buildings to the build script. ```input_data\armaObjects.txt``` is parsed every time main.py is run. The format is a list of lists with the following format:
```
[
    [
        "building_use1",
        "building_biome1",
        [
            [
                "arma_object_class1",
                width(float)
                length(float)
                height(float)
            ],
            [
                "arma_object_class2"... etc
            ]
        ]
    ],
    [
        "building_use1"
        "building_biome1,
        [
            ...
        ],
        [
            ...
        ]
    ]
]
```
Check out ```tools\fn_getObjects.sqf``` to see how the basic armaObjects.txt is built, as the clipboard result of that function makes up the txt file.
## Contributing

I welcome all contributions. The code is a labrynthine mess... so have fun!
