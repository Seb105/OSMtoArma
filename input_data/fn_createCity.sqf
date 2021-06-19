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
{
    _x spawn {
        params ["_class", "_pos", "_dir"];
        _pos = _pos vectorDiff minVec;
        _object = createVehicle [_class, _pos, [], 0, "CAN_COLLIDE"];
        _object setDir _dir;
        _object setPos _pos; // Roads aren't actually placed where you got dang say
        _marker = createMarker [format["marker_%1", str _object], _pos];
        _marker setMarkerType "hd_dot";
        _marker setMarkerColor "ColorWhite";
        allCityObjects pushBack _object;
        allCityMarkers pushBack _marker;
    };
} forEach _objects;
systemChat "Done building new objects"