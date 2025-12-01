from main import GmlReader

if __name__ == "__main__":
    path = 'C:\\uni\\5sem\\kataster\\proj2\\dane\\Zbiór danych GML ZSK 2025.gml.txt'

    points = 0
    reader = GmlReader(path)
    for member in reader.members:
        if member.geometry_type == 'Polygon':
            points += 1
    print(f'Number of Polygon geometries: {points}')
    for member in reader.members:
        if member.geometry_type == 'Point':
            points += 1
    print(f'Number of Point geometries: {points}')
    for member in reader.members:
        if member.geometry_type == 'LineString':
            points += 1
    print(f'Number of LineString geometries: {points}')