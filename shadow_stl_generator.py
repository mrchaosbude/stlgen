import numpy as np
from PIL import Image
from stl import mesh

def image_to_shadow_stl(image_path, output_path, pixel_size=1.0, max_height=30.0, min_height=1.0):
    # Bild laden und in Graustufen konvertieren
    img = Image.open(image_path).convert('L')
    img = img.resize((100, 100))  # Für schnelleren Test, anpassbar
    pixels = np.array(img)
    pixels = 255 - pixels  # Schwarz = hoch, Weiß = niedrig
    
    # Normiere Höhen
    heights = min_height + (pixels / 255.0) * (max_height - min_height)
    
    # Erstelle eine Liste der Quader
    cubes = []
    for i in range(pixels.shape[0]):
        for j in range(pixels.shape[1]):
            h = heights[i, j]
            x = i * pixel_size
            y = j * pixel_size
            z = 0
            # Quader an Position (x, y, z) mit Höhe h
            cubes.append(create_cube(x, y, z, pixel_size, h))
    
    # Alle Quader zu einer Mesh kombinieren
    all_cubes = np.concatenate(cubes)
    body = mesh.Mesh(np.zeros(all_cubes.shape[0], dtype=mesh.Mesh.dtype))
    for i, f in enumerate(all_cubes):
        for j in range(3):
            body.vectors[i][j] = f[j]
    body.save(output_path)
    print(f"STL gespeichert als {output_path}")

def create_cube(x, y, z, size, height):
    # Gibt die 12 Dreiecke eines Quaders zurück
    p = np.array([
        [x, y, z],
        [x + size, y, z],
        [x + size, y + size, z],
        [x, y + size, z],
        [x, y, z + height],
        [x + size, y, z + height],
        [x + size, y + size, z + height],
        [x, y + size, z + height],
    ])
    faces = np.array([
        [p[0], p[3], p[1]], [p[1], p[3], p[2]],  # bottom
        [p[4], p[5], p[7]], [p[5], p[6], p[7]],  # top
        [p[0], p[1], p[4]], [p[1], p[5], p[4]],  # front
        [p[1], p[2], p[5]], [p[2], p[6], p[5]],  # right
        [p[2], p[3], p[6]], [p[3], p[7], p[6]],  # back
        [p[3], p[0], p[7]], [p[0], p[4], p[7]],  # left
    ])
    return faces

if __name__ == "__main__":
    # Beispielaufruf: Passe die Bilddatei und Ausgabe an
    image_to_shadow_stl("input.png", "shadowlamp.stl")