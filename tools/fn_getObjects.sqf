/*
This function dumps the sizes of arma objects to the clipboard, along with their biome use. It also sanitises the data before importing so you don't get crap stuff.
*/

// Never get buildings with this in the name
BLACKLIST_NAMES =   ["destroyed", "ruin", "damaged", "abandoned", "burned", "dock", "platform", "pier", "unfinished", "escape", "cover", 'shack', 'terrace', 'slum', 'shed', 'sidewalk', 'picnic', 'green house',
                    "coop", "pile", "hutch", "well", 'pergola', 'tree', 'water source', 'land_pot'];
// Special list of buildings to gather properties for.
SPECIAL_WHITELIST = ["Land_Vysilac_budova", "Land_a_stationhouse", "Land_House_C_12_EP1", "Land_A_Hospital", "Land_Hotel_01_F", "Land_Supermarket_01_malden_F", "Land_FuelStation_03_shop_F"];

systemChat "Filtering config. This will take a while.";
allVehicleConfigs = ([configFile >> "CfgVehicles", 0] call BIS_fnc_returnChildren) select {
    private _config = _x;
    getNumber (_config >> "scope") == 2 && 
    ({_x in (toLower ([_config, "displayName", "nil"] call BIS_fnc_returnConfigEntry))} count BLACKLIST_NAMES) isEqualTo 0
};

private _get_all_of_type = {
    params ["_editorCat","_editorSubcat", "_type", "_biome"];
    systemChat format ["Getting %1 %2", _biome, _editorSubcat];
    private _used = (allVehicleConfigs select {
        [_x, "editorCategory", "nil"] call BIS_fnc_returnConfigEntry isEqualTo _editorCat && 
        [_x, "editorSubcategory", "nil"] call BIS_fnc_returnConfigEntry isEqualTo _editorSubcat
    }) apply {
        configName _x
    };
    private _output = [];
    systemChat format ["%1: %2 objects to do", _type, count _used];
    {
        [_output, _x] spawn {
            params ["_output", "_objectClass"];
            private _object = createVehicle [_objectClass, [0, 0]];
            private _bbr = 0 boundingBoxReal vehicle _object;
            private _p1 = _bbr select 0;
            private _p2 = _bbr select 1;
            private _maxWidth = abs ((_p2 select 0) - (_p1 select 0));
            private _maxLength = abs ((_p2 select 1) - (_p1 select 1));
            private _maxHeight = abs ((_p2 select 2) - (_p1 select 2));
            _output pushBack [_objectClass, _maxWidth, _maxLength, _maxHeight];
            deleteVehicle _object;
        }
    } forEach _used;
    waitUntil {count _output == count _used};
    [_type, _biome, _output]
};


private _outputStr = [];

// Vanilla Altis + Malden
// Altis
_outputStr pushBack (["EdCat_Structures_Altis", "EdSubcat_Residential_City", "city", "mediterranean"] call _get_all_of_type);
_outputStr pushBack (["EdCat_Structures_Altis", "EdSubcat_Residential_Village", "village", "mediterranean"] call _get_all_of_type);
_outputStr pushBack (["EdCat_Structures_Altis", "EdSubcat_Industrial", "industrial", "mediterranean"] call _get_all_of_type);
_outputStr pushBack (["EdCat_Structures_Altis", "EdSubcat_Religious", "religious", "mediterranean"] call _get_all_of_type);
// Malden
_outputStr pushBack (["EdCat_Structures_Malden", "EdSubcat_Residential_City", "city", "mediterranean"] call _get_all_of_type);
_outputStr pushBack (["EdCat_Structures_Malden", "EdSubcat_Residential_Village", "village", "mediterranean"] call _get_all_of_type);
_outputStr pushBack (["EdCat_Structures_Malden", "EdSubcat_Industrial", "industrial", "mediterranean"] call _get_all_of_type);
_outputStr pushBack (["EdCat_Structures_Malden", "EdSubcat_Religious", "religious", "mediterranean"] call _get_all_of_type);

//Tanoa
_outputStr pushBack (["EdCat_Structures_Tanoa", "EdSubcat_Residential_City", "city", "asia_modern"] call _get_all_of_type);
_outputStr pushBack (["EdCat_Structures_Tanoa", "EdSubcat_Residential_Village", "village", "asia_modern"] call _get_all_of_type);
_outputStr pushBack (["EdCat_Structures_Tanoa", "EdSubcat_Industrial", "industrial", "asia_modern"] call _get_all_of_type);
_outputStr pushBack (["EdCat_Structures_Tanoa", "EdSubcat_Religious", "religious", "asia_modern"] call _get_all_of_type);

// Eastern europe stuff
// CUP Chernarus, EU stuff.
_outputStr pushBack (["EdCat_CUP_Structures_EU", "EdSubcat_Residential_City", "city", "east_europe"] call _get_all_of_type);
_outputStr pushBack (["EdCat_CUP_Structures_EU", "EdSubcat_Residential_Village", "village", "east_europe"] call _get_all_of_type);
_outputStr pushBack (["EdCat_CUP_Structures_EU", "EdSubcat_Industrial", "industrial", "east_europe"] call _get_all_of_type);
_outputStr pushBack (["EdCat_CUP_Structures_EU", "EdSubcat_Religious", "religious", "east_europe"] call _get_all_of_type);
// Livonia. No city subcat!
_outputStr pushBack (["EdCat_Structures_Enoch", "EdSubcat_Residential_Village", "village", "east_europe"] call _get_all_of_type);
_outputStr pushBack (["EdCat_Structures_Enoch", "EdSubcat_Industrial", "industrial", "east_europe"] call _get_all_of_type);
_outputStr pushBack (["EdCat_Structures_Enoch", "EdSubcat_Religious", "religious", "east_europe"] call _get_all_of_type);

// CUP middle east
_outputStr pushBack (["EdCat_CUP_Structures_ME", "EdSubcat_Residential_City", "city", "middle_east"] call _get_all_of_type);
_outputStr pushBack (["EdCat_CUP_Structures_ME", "EdSubcat_Residential_Village", "village", "middle_east"] call _get_all_of_type);
_outputStr pushBack (["EdCat_CUP_Structures_ME", "EdSubcat_Shops", "city", "middle_east"] call _get_all_of_type);
_outputStr pushBack (["EdCat_CUP_Structures_ME", "EdSubcat_Industrial", "industrial", "middle_east"] call _get_all_of_type);
_outputStr pushBack (["EdCat_CUP_Structures_ME", "EdSubcat_Religious", "religious", "middle_east"] call _get_all_of_type);

// Cup misc
_outputStr pushBack (["EdCat_CUP_Structures_Misc", "EdSubcat_Residential_City", "city", "misc"] call _get_all_of_type);
_outputStr pushBack (["EdCat_CUP_Structures_Misc", "EdSubcat_Shops", "city", "misc"] call _get_all_of_type);
_outputStr pushBack (["EdCat_CUP_Structures_Misc", "EdSubcat_Industrial", "industrial", "misc"] call _get_all_of_type);
_outputStr pushBack (["EdCat_CUP_Structures_Misc", "EdSubcat_Religious", "religious", "misc"] call _get_all_of_type);

// Get special stuff 
systemchat "Getting special stuff";
private _special_output = [];
{
    private _objectClass = _x;
    private _object = createVehicle [_objectClass, [0, 0]];
    private _bbr = 0 boundingBoxReal vehicle _object;
    private _p1 = _bbr select 0;
    private _p2 = _bbr select 1;
    private _maxWidth = abs ((_p2 select 0) - (_p1 select 0));
    private _maxLength = abs ((_p2 select 1) - (_p1 select 1));
    private _maxHeight = abs ((_p2 select 2) - (_p1 select 2));
    deleteVehicle _object;
    _special_output pushBack [_objectClass, _maxWidth, _maxLength, _maxHeight];
} forEach SPECIAL_WHITELIST;
_outputStr pushBack ["city", "east_europe", _special_output];



systemchat "Done";
copyToClipboard str _outputStr;