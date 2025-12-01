from main import GmlReader

def geom_type_tester(reader):
    points = 0
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

def geom_read_tester(reader):
    return



if __name__ == "__main__":
    path = 'C:\\uni\\5sem\\kataster\\proj2\\dane\\Zbiór danych GML ZSK 2025.gml.txt'

    reader = GmlReader(path)

    geom_type_tester(reader)

    