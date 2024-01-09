# BECAS

The structural properties in the WindIO file are based on BECAS using the meshes in this folder.

The meshes were generated using DTU's AESOpt framework that features a relatively simple cross-sectional mesher.

## Coordinate systems

The coordinate system for the cross-sectional meshes follows a right-handed system
with x+ towards the leading edge, y+ towards the airfoil suction side, and z+ towards the blade tip.
The meshes are placed in the local chord reference frame with the reference axis defined in the WindIO file at the origin.
To transform the resulting stiffness and inertia matrices to WindIO, the 6x6 matrices need to be rotated +90 degrees.
