import math
from typing import List, Tuple

import numpy as np
import struct
from PIL import Image


Vertex = Tuple[float, float, float]
Face = Tuple[Vertex, Vertex, Vertex]

def create_cube(x: float, y: float, z: float, size: float, height: float) -> List[Face]:
    p = [
        (x, y, z),
        (x + size, y, z),
        (x + size, y + size, z),
        (x, y + size, z),
        (x, y, z + height),
        (x + size, y, z + height),
        (x + size, y + size, z + height),
        (x, y + size, z + height),
    ]
    return [
        (p[0], p[3], p[1]), (p[1], p[3], p[2]),
        (p[4], p[5], p[7]), (p[5], p[6], p[7]),
        (p[0], p[1], p[4]), (p[1], p[5], p[4]),
        (p[1], p[2], p[5]), (p[2], p[6], p[5]),
        (p[2], p[3], p[6]), (p[3], p[7], p[6]),
        (p[3], p[0], p[7]), (p[0], p[4], p[7]),
    ]

def _normal(v1: Vertex, v2: Vertex, v3: Vertex) -> Tuple[float, float, float]:
    ux, uy, uz = (v2[0] - v1[0], v2[1] - v1[1], v2[2] - v1[2])
    vx, vy, vz = (v3[0] - v1[0], v3[1] - v1[1], v3[2] - v1[2])
    nx = uy * vz - uz * vy
    ny = uz * vx - ux * vz
    nz = ux * vy - uy * vx
    length = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
    return nx / length, ny / length, nz / length


def write_binary_stl(faces: List[Face], filename: str) -> None:
    with open(filename, "wb") as f:
        header = b"Created by disk_shadow_generator".ljust(80, b" ")
        f.write(header)
        f.write(len(faces).to_bytes(4, byteorder="little"))
        for v1, v2, v3 in faces:
            nx, ny, nz = _normal(v1, v2, v3)
            f.write(struct.pack("<3f", nx, ny, nz))
            for v in (v1, v2, v3):
                f.write(struct.pack("<3f", *v))
            f.write((0).to_bytes(2, byteorder="little"))

def image_to_shadow_disk(
    image_path: str,
    output_path: str,
    outer_radius: float = 50.0,
    hole_radius: float = 20.0,
    base_thickness: float = 1.0,
    max_relief: float = 5.0,
    resolution: int = 200,
) -> None:
    img = Image.open(image_path).convert("L")
    img = img.resize((resolution, resolution))
    pixels = np.array(img)
    pixels = 255 - pixels

    pixel_size = 2 * outer_radius / resolution
    faces: List[Face] = []
    for i in range(resolution):
        x = i * pixel_size - outer_radius
        for j in range(resolution):
            y = j * pixel_size - outer_radius
            r = math.hypot(x + pixel_size / 2, y + pixel_size / 2)
            if hole_radius <= r <= outer_radius:
                h = base_thickness + (pixels[j, i] / 255.0) * max_relief
                faces.extend(create_cube(x, y, 0.0, pixel_size, h))
    write_binary_stl(faces, output_path)
    print(f"STL saved to {output_path}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate disk shadow STL")
    parser.add_argument("image", help="input image file")
    parser.add_argument("output", help="output STL file")
    parser.add_argument("--outer_radius", type=float, default=50.0)
    parser.add_argument("--hole_radius", type=float, default=20.0)
    parser.add_argument("--base_thickness", type=float, default=1.0)
    parser.add_argument("--max_relief", type=float, default=5.0)
    parser.add_argument("--resolution", type=int, default=200)
    args = parser.parse_args()

    image_to_shadow_disk(
        args.image,
        args.output,
        outer_radius=args.outer_radius,
        hole_radius=args.hole_radius,
        base_thickness=args.base_thickness,
        max_relief=args.max_relief,
        resolution=args.resolution,
    )
