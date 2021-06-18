private _objects = [THE_BUILD_ARRAY];

{
    _x spawn {deleteVehicle _this};
} forEach (allMissionObjects "All") - [player];
{
    _x spawn {deleteMarker _this};
} forEach allMapMarkers;
private _minX = 1e39;
private _minY = 1e39;
{
    _minX = _x#1#0 min _minX;
    _minY = _x#1#1 min _minY;
} forEach _objects;
minVec = [_minX, _minY];
{
    _x spawn {
        params ["_class", "_pos", "_dir"];
        _pos = _pos vectorDiff minVec;
        _road = createVehicle [_class, _pos, [], 0, "CAN_COLLIDE"];
        _road setDir _dir;
        _road setPos _pos; // Roads aren't actually placed where you got dang say
        _marker = createMarker [format["marker_%1", str _road], _pos];
        _marker setMarkerType "hd_dot";
        _marker setMarkerColor "ColorWhite";
    };
} forEach _objects;