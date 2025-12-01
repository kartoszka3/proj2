class GmlFeatureMember:
    def __init__(self, feature_type, feature_data):
        self.feature_type = feature_type
        self.feature_data = feature_data
        self.geometry_type = None
        self.geometry = None
        self.classify_geometry()

    def classify_geometry(self):
        for line in self.feature_data:
            if '<gml:Point' in line:
                self.geometry_type = 'Point'
                for l in self.feature_data:
                    if '<gml:pos>' in l:
                        self.geometry = l.strip()
                        break
            if '<gml:Curve' in line or '<gml:LineString' in line:
                self.geometry_type = 'LineString'
                for l in self.feature_data:
                    if '<gml:posList>' in l:
                        self.geometry = l.strip()
                        break
                return
            if '<gml:Polygon' in line:
                self.geometry_type = 'Polygon'
                for l in self.feature_data:
                    if '<gml:posList>' in l:
                        self.geometry = l.strip()
                        break
                return

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

#DZIAŁKI I UŻYTKI TYLKO