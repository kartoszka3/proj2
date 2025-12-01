class GmlFeatureMember:
    def __init__(self, feature_type, feature_data):
        self.feature_type = feature_type
        self.feature_data = feature_data

class GmlReader:
    def __init__(self, path):
        self.path = path
        self.members = []

        with open(self.path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line.startswith('<gml:featureMember>'):
                    feature_data = []
                    feature_type = None
                    while not line.startswith('</gml:featureMember>'):
                        line = next(file).strip()
                        if line.startswith('<') and not line.startswith('</'):
                            tag_end = line.find('>')
                            tag_name = line[1:tag_end].split()[0]
                            if feature_type is None:
                                feature_type = tag_name
                        feature_data.append(line)
                    self.members.append(GmlFeatureMember(feature_type, feature_data))
    
if __name__ == "__main__":
    path = 'C:\\uni\\5sem\\kataster\\proj2\\dane\\Zbiór danych GML ZSK 2025.gml.txt'

    reader = GmlReader(path)
    print(reader.members[672].feature_type)


