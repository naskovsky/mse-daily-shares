class Kurs:

    def __init__(self, _oznaka, _cena):
        self.oznaka = _oznaka
        self.cena = _cena

    def vrati_oznaka(self):
        return self.oznaka

    def vrati_cena(self):
        return self.cena

    def pecati_dvete(self):
        return self.oznaka + " " + self.cena