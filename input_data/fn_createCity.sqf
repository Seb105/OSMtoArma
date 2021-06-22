params [
    ["_bottomLeft", [0, 0]],
    ["_debug", false]
];
if (missionNamespace getVariable ["CITY_SCRIPT_RUNNING", false]) exitWith {};
CITY_SCRIPT_RUNNING = true;

CITY_SCRIPT_DEBUG = _debug;
private _objects = [THE_BUILD_ARRAY];
systemChat "Building city";
allCityObjects = missionNamespace getVariable ["allCityObjects", []];
allCityMarkers = missionNameSpace getVariable ["allCityMarkers", []];
allCityEntities = missionNameSpace getVariable ["allCityEntities", []];
_objectsToDelete = +allCityObjects;
_markersToDelete = +allCityMarkers;
0 = _objectsToDelete spawn {
systemChat "Deleting old objects";
{
    _x spawn {deleteVehicle _this};
} forEach _this;
systemChat "Done deleting old objects";

};
0 = _markersToDelete spawn {
    systemChat "Deleting old markers";
    {
        _x spawn {deleteMarker _this};
    } forEach _this;
systemChat "Done deleting old markers";

if (is3DEN) then {
    systemChat "Deleting Eden entities";
    delete3DENEntities allCityEntities;
    allCityEntities = [];
    systemChat "Done deleting eden entities";
}
};
allCityMarkers = [];
allCityObjects = [];

private _minX = 1e39;
private _minY = 1e39;
{
    _minX = _x#1#0 min _minX;
    _minY = _x#1#1 min _minY;
} forEach _objects;
minVec = [_minX, _minY] vectorAdd _bottomLeft;
systemChat "Building new objects";
{
    _x spawn {
        params ["_class", "_pos", "_dir"];
        _pos = _pos vectorDiff minVec;
        _object = createVehicle [_class, _pos, [], 0, "CAN_COLLIDE"];
        _object setDir _dir;
        _object setPos _pos; // Roads aren't actually placed where you got dang say
        allCityObjects pushBack _object;
        if (CITY_SCRIPT_DEBUG) then {
            _marker = createMarker [format["marker_%1", str _object], _pos];
            _marker setMarkerType "hd_dot";
            _marker setMarkerColor "ColorWhite";
            allCityMarkers pushBack _marker;
        };
    };
} forEach _objects;
waitUntil {sleep 1; count allCityObjects == count _objects};
systemChat "Done building new objects";
// You might as well do it in 2 steps, as you need to use getPosWorld as creating an 3den entity /set3DENAttribute the pos doesn't work properly
if (is3DEN) then {
    systemChat "Eden detected. Converting all objects to Eden entities. This will take a long time.";
    private _todo = +allCityObjects;
    {
        _x spawn {
            params ["_object"];
            private _class = typeOf _object;
            private _pos =  getPosWOrld _object;
            private _dir = getDir _object;
            _object spawn {deleteVehicle _this};
            _entity = create3DENEntity ["Object", _class, _pos];
            _entity set3DENAttribute ["rotation", [0, 0, _dir]];
            _entity set3DENAttribute ["position", [_pos#0, _pos#1, 0]];            
            allCityEntities pushBack _entity;
        };
    } forEach _todo;
    allCityObjects = [];
    systemChat "Done";
} else {
    systemChat "Done"
};

CITY_SCRIPT_RUNNING = false;