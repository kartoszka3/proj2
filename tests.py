from main import GmlReader


def geom_read_tester(reader):
    return

def type_test(reader):
    types = {}
    for member in reader.members:
        if member.feature_type not in types:
            types[member.feature_type] = 0
        types[member.feature_type] += 1
    for feature_type, count in types.items():
        print(f'Feature Type: {feature_type}, Count: {count}')

def budynek_geom_test(reader):
    for member in reader.members:
        if member.feature_type == "egb:EGB_Budynek":
            print(f'Geometry Type: {member.geometry_type}')
            print(f'Geometry: {member.geometry}')
        if member.feature_type == "egb:EGB_DzialkaEwidencyjna":
            print(f'Geometry Type: {member.geometry_type}')
            print(f'Geometry: {member.geometry}')


if __name__ == "__main__":
    path = 'C:\\uni\\5sem\\kataster\\proj2\\dane\\Zbiór danych GML ZSK 2025.gml.txt'

    reader = GmlReader(path)
    type_test(reader)
    # budynek_geom_test(reader)
