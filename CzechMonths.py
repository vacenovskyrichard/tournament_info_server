class CzechMonths:
    def __init__(self,name):
        self.name = name
    def to_number(self):
        if "led" in self.name.lower(): return 1
        if "únor" in self.name.lower() or "unor" in self.name.lower():return 2
        if "břez" in self.name.lower() or "brez" in self.name.lower():return 3
        if "dub" in self.name.lower():return 4
        if "květ" in self.name.lower() or "kvet" in self.name.lower():return 5
        if "červenec" in self.name.lower() or "července" in self.name.lower() or "cervenec" in self.name.lower() or "cervence" in self.name.lower():return 7
        if "červen" in self.name.lower() or "června" in self.name.lower() or "cerven" in self.name.lower() or "cervna" in self.name.lower():return 6
        if "srp" in self.name.lower():return 8
        if "září" in self.name.lower() or "zari" in self.name.lower():return 9
        if "říj" in self.name.lower() or "řij" in self.name.lower():return 10
        if "listop" in self.name.lower():return 11
        if "pros" in self.name.lower():return 12
        return-1