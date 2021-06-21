params [
    ["_bottomLeft", [0, 0]],
    ["_debug", false]
];
CITY_SCRIPT_DEBUG = _debug;
private _objects = [THE_BUILD_ARRAY];
systemChat "Building city";
allCityObjects = missionNamespace getVariable ["allCityObjects", []];
allCityMarkers = missionNameSpace getVariable ["allCityMarkers", []];
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
    "Done deleting old markers";
};
allCityMarkers = [];
allCityObjects = [];

private _minX = 1e39;
private _minY = 1e39;
{
    _minX = _x#1#0 min _minX;
    _minY = _x#1#1 min _minY;
} forEach _objects;
minVec = [_minX, _minY];
systemChat "Building new objects";
if (is3DEN) then {
    collect3denhistory {
        {
            _x spawn {
                params ["_class", "_pos", "_dir"];
                _pos = _pos vectorDiff minVec;
                _object = createVehicle [_class, _pos, [], 0, "CAN_COLLIDE"];

                // Fucking retarded hack for fixing objects in 3den not being created in the right place
                // Bohemia are dumb
                _object setDir _dir;
                _object setPos _pos;
                _pos = getPosWorld _object;
                deleteVehicle _object;
                
                _entity = create3DENEntity ["Object", _class, [0, 0, 0]];
                _entity set3DENAttribute ["rotation", [0, 0, _dir]];
                _entity set3DENAttribute ["position", [_pos#0, _pos#1, 0]]; // Roads aren't actually placed where you got dang say

                if (CITY_SCRIPT_DEBUG) then {
                    _marker = createMarker [format["marker_%1", str _entity], _pos];
                    _marker setMarkerType "hd_dot";
                    _marker setMarkerColor "ColorWhite";
                    allCityMarkers pushBack _marker;
                };
                
                allCityObjects pushBack _entity;
            };
        } forEach _objects;
    };
} else {
    {
        _x spawn {
            params ["_class", "_pos", "_dir"];
            _pos = _pos vectorDiff minVec;
            _object = createVehicle [_class, _pos, [], 0, "CAN_COLLIDE"];
            _object setDir _dir;
            _object setPos _pos; // Roads aren't actually placed where you got dang say
            if (CITY_SCRIPT_DEBUG) then {
                _marker = createMarker [format["marker_%1", str _object], _pos];
                _marker setMarkerType "hd_dot";
                _marker setMarkerColor "ColorWhite";
                allCityMarkers pushBack _marker;
            };
            allCityObjects pushBack _object;
        };
    } forEach _objects;
    systemChat "Done building new objects"
}