import math
import random
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

def create_pyramid(x: float, y: float, z: float, size: float, height: float) -> List[Face]:
    base = [
        (x, y, z),
        (x + size, y, z),
        (x + size, y + size, z),
        (x, y + size, z),
    ]
    apex = (x + size / 2, y + size / 2, z + height)
    return [
        (base[0], base[1], base[2]), (base[0], base[2], base[3]),
        (base[0], base[1], apex), (base[1], base[2], apex),
        (base[2], base[3], apex), (base[3], base[0], apex),
    ]

def create_cylinder(x: float, y: float, z: float, size: float, height: float, segments: int = 12) -> List[Face]:
    radius = size / 2
    cx = x + radius
    cy = y + radius
    faces: List[Face] = []
    for i in range(segments):
        a1 = 2 * math.pi * i / segments
        a2 = 2 * math.pi * (i + 1) / segments
        p1 = (cx + radius * math.cos(a1), cy + radius * math.sin(a1), z)
        p2 = (cx + radius * math.cos(a2), cy + radius * math.sin(a2), z)
        p1_top = (p1[0], p1[1], z + height)
        p2_top = (p2[0], p2[1], z + height)
        faces.append(((cx, cy, z), p2, p1))
        faces.append(((cx, cy, z + height), p1_top, p2_top))
        faces.append((p1, p2, p1_top))
        faces.append((p2, p2_top, p1_top))
    return faces

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
    shape: str = "cube",
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
                shape_sel = shape
                if shape == "mixed":
                    shape_sel = random.choice(["cube", "cylinder", "pyramid"])
                if shape_sel == "cube":
                    faces.extend(create_cube(x, y, 0.0, pixel_size, h))
                elif shape_sel == "cylinder":
                    faces.extend(create_cylinder(x, y, 0.0, pixel_size, h))
                elif shape_sel == "pyramid":
                    faces.extend(create_pyramid(x, y, 0.0, pixel_size, h))
                else:
                    raise ValueError(f"Unknown shape type: {shape_sel}")
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
    parser.add_argument("--shape", choices=["cube", "cylinder", "pyramid", "mixed"], default="cube")
    args = parser.parse_args()

    image_to_shadow_disk(
        args.image,
        args.output,
        outer_radius=args.outer_radius,
        hole_radius=args.hole_radius,
        base_thickness=args.base_thickness,
        max_relief=args.max_relief,
        resolution=args.resolution,
        shape=args.shape,
    )
