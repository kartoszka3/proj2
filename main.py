class GmlFeatureMember:
    def __init__(self, feature_type, feature_data):
        self.feature_type = feature_type
        self.feature_data = feature_data
        self.geometry_type = None
        self.geometry = None
        self.gml_id = None
        self.area = None
        self.classuse = []
        self.classify()

    def classify(self):
        if self.feature_type == "egb:EGB_Budynek":
            self.geometry_type = "Polygon"
            for line in self.feature_data:
                if "gml:posList" in line:
                    self.geometry = line[line.find('>') + 1:line.find('</')]
                if 'gml:id=' in line and self.gml_id is None:
                    start = line.find('gml:id="') + 8
                    end = line.find('"', start)
                    if start > 7 and end > start:
                        self.gml_id = line[start:end]

        if self.feature_type == "egb:EGB_DzialkaEwidencyjna":
            self.geometry_type = "Polygon"
            current_klasouzytek = {}
            
            for i, line in enumerate(self.feature_data):
                if "gml:posList" in line:
                    self.geometry = line[line.find('>') + 1:line.find('</')]
                
                if 'gml:id=' in line and self.gml_id is None:
                    start = line.find('gml:id="') + 8
                    end = line.find('"', start)
                    if start > 7 and end > start:
                        self.gml_id = line[start:end]
                
                if '<egb:poleEwidencyjne' in line:
                    start = line.find('>') + 1
                    end = line.find('</')
                    if start > 0 and end > start:
                        try:
                            self.pole_ewidencyjne = float(line[start:end])
                        except:
                            pass
                
                if '<egb:klasouzytek>' in line:
                    current_klasouzytek = {}
                
                if '<egb:OFU>' in line:
                    start = line.find('>') + 1
                    end = line.find('</')
                    if start > 0 and end > start:
                        current_klasouzytek['OFU'] = line[start:end]
                
                if '<egb:OZU>' in line:
                    start = line.find('>') + 1
                    end = line.find('</')
                    if start > 0 and end > start:
                        current_klasouzytek['OZU'] = line[start:end]
                
                if '<egb:OZK>' in line:
                    start = line.find('>') + 1
                    end = line.find('</')
                    if start > 0 and end > start:
                        current_klasouzytek['OZK'] = line[start:end]
                
                if '<egb:powierzchnia' in line:
                    start = line.find('>') + 1
                    end = line.find('</')
                    if start > 0 and end > start:
                        try:
                            current_klasouzytek['powierzchnia'] = float(line[start:end])
                        except:
                            current_klasouzytek['powierzchnia'] = 0.0
                
                if '</egb:klasouzytek>' in line and current_klasouzytek:
                    # Dodaj kompletny klasoużytek do listy
                    self.klasouzytki.append({
                        'OFU': current_klasouzytek.get('OFU', ''),
                        'OZU': current_klasouzytek.get('OZU', ''),
                        'OZK': current_klasouzytek.get('OZK', ''),
                        'powierzchnia': current_klasouzytek.get('powierzchnia', 0.0)
                    })
                    current_klasouzytek = {}
                

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