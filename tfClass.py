class TransferFunction():
    def __init__(self, D=None, G=None):
        if G is None:
            G = [[1], [1]]
        if D is None:
            D = [[1], [1]]

        self.Dfunc = D
        self.Gfunc = G

    def D(self, s):
        valNum = 0
        valDen = 0
        for i in range(len(self.Dfunc[0]) - 1, -1, -1):
            valNum += s ** i * self.Dfunc[0][i]
        for i in range(len(self.Dfunc[1]) - 1, -1, -1):
            valDen += s ** i * self.Dfunc[1][i]

        if valNum == 0 or valDen == 0:
            return 0
        else:
            return valNum / valDen

    def G(self, s):
        valNum = 0
        valDen = 0
        for i in range(len(self.Gfunc[0]) - 1, -1, -1):
            valNum += s ** i * self.Gfunc[0][i]

        for i in range(len(self.Gfunc[1]) - 1, -1, -1):
            valDen += s ** i * self.Gfunc[1][i]
        if valNum == 0 or valDen == 0:
            return 0
        else:
            return valNum / valDen

    def DsGs(self, s):
        return self.D(s) * self.G(s)
