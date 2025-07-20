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


## raytrace_verify.py

`raytrace_verify.py` performs a minimal ray tracing step to validate that the
generated STL actually casts the intended shadow. It places a point light in the
center of the hole and renders both the resulting shadow on a plane and an
angled view of the geometry.

Example:

```
python raytrace_verify.py output.stl --shadow_output shadow.png --render_output render.png
```

Both scripts require `numpy` and `Pillow` to run.
