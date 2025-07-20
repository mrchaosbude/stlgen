# STL Generator

This repository contains utilities to convert images into 3D printable STL files.

## disk_shadow_stl_generator.py

`disk_shadow_stl_generator.py` creates a round plate with a central hole large
enough for an E27 bulb. The relief heights on the plate are derived from a
provided grayscale image so that illuminated shadows reproduce the original
picture.

Basic usage:
```
python disk_shadow_stl_generator.py input.png output.stl \
    --outer_radius 60 --hole_radius 20
```

The script depends on `numpy` and `Pillow` being available in the Python
environment.

