import math
import struct
from typing import Tuple, List

import numpy as np
from PIL import Image

Vector = np.ndarray
Triangle = Tuple[Vector, Vector, Vector]

def load_binary_stl(filename: str) -> List[Triangle]:
    with open(filename, 'rb') as f:
        f.read(80)  # header
        count = struct.unpack('<I', f.read(4))[0]
        tris = []
        for _ in range(count):
            data = struct.unpack('<12fH', f.read(50))
            v1 = np.array(data[3:6])
            v2 = np.array(data[6:9])
            v3 = np.array(data[9:12])
            tris.append((v1, v2, v3))
    return tris

def ray_triangle_intersect(orig: Vector, dir: Vector, tri: Triangle) -> float:
    v0, v1, v2 = tri
    eps = 1e-6
    edge1 = v1 - v0
    edge2 = v2 - v0
    h = np.cross(dir, edge2)
    a = np.dot(edge1, h)
    if -eps < a < eps:
        return math.inf
    f = 1.0 / a
    s = orig - v0
    u = f * np.dot(s, h)
    if u < 0.0 or u > 1.0:
        return math.inf
    q = np.cross(s, edge1)
    v = f * np.dot(dir, q)
    if v < 0.0 or u + v > 1.0:
        return math.inf
    t = f * np.dot(edge2, q)
    if t > eps:
        return t
    return math.inf

def make_shadow_image(tris: List[Triangle], light: Vector, plane_z: float,
                       size: float, resolution: int) -> Image.Image:
    half = size / 2.0
    img = np.zeros((resolution, resolution), dtype=np.uint8) + 255
    for iy in range(resolution):
        y = (iy / (resolution - 1) - 0.5) * size
        for ix in range(resolution):
            x = (ix / (resolution - 1) - 0.5) * size
            target = np.array([x, y, plane_z])
            dir = target - light
            dist = np.linalg.norm(dir)
            dir /= dist
            blocked = False
            for tri in tris:
                t = ray_triangle_intersect(light, dir, tri)
                if t < dist:
                    blocked = True
                    break
            if blocked:
                img[iy, ix] = 0
    return Image.fromarray(img)

def make_render_image(tris: List[Triangle], light: Vector, camera: Vector,
                      resolution: int, fov: float = math.pi / 3) -> Image.Image:
    aspect = 1.0
    screen_dist = 1.0 / math.tan(fov / 2.0)
    img = np.zeros((resolution, resolution), dtype=np.uint8)
    for iy in range(resolution):
        py = (1 - 2 * (iy + 0.5) / resolution)
        for ix in range(resolution):
            px = (2 * (ix + 0.5) / resolution - 1) * aspect
            dir = np.array([px, py, -screen_dist])
            dir = dir / np.linalg.norm(dir)
            dir_world = dir  # camera at origin looking along -z
            orig = camera
            nearest_t = math.inf
            nearest_tri = None
            for tri in tris:
                t = ray_triangle_intersect(orig, dir_world, tri)
                if t < nearest_t:
                    nearest_t = t
                    nearest_tri = tri
            if nearest_tri is not None:
                point = orig + dir_world * nearest_t
                normal = np.cross(nearest_tri[1]-nearest_tri[0], nearest_tri[2]-nearest_tri[0])
                normal = normal / (np.linalg.norm(normal) or 1.0)
                light_dir = light - point
                light_dir /= np.linalg.norm(light_dir)
                intensity = max(0.0, np.dot(normal, light_dir))
                img[iy, ix] = int(255 * intensity)
    return Image.fromarray(img)

def verify(stl_path: str, shadow_output: str, render_output: str,
           plane_z: float = 100.0, size: float = 100.0,
           resolution: int = 256) -> None:
    tris = load_binary_stl(stl_path)
    light = np.array([0.0, 0.0, 0.0])
    cam = np.array([0.0, 0.0, 80.0])
    shadow = make_shadow_image(tris, light, plane_z, size, resolution)
    shadow.save(shadow_output)
    render = make_render_image(tris, light, cam, resolution)
    render.save(render_output)
    print(f"Shadow saved to {shadow_output}")
    print(f"Render saved to {render_output}")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Raytrace STL to verify shadow')
    parser.add_argument('stl', help='input STL file')
    parser.add_argument('--shadow_output', default='shadow.png')
    parser.add_argument('--render_output', default='render.png')
    parser.add_argument('--plane_z', type=float, default=100.0)
    parser.add_argument('--size', type=float, default=100.0)
    parser.add_argument('--resolution', type=int, default=256)
    args = parser.parse_args()
    verify(args.stl, args.shadow_output, args.render_output,
           plane_z=args.plane_z, size=args.size, resolution=args.resolution)
