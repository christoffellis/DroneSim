
class GraphicsHandler:
    class drawItem:
        def __init__(self, instruction):
            self.instruction = instruction

        def draw(self):
            self.instruction()

    def __init__(self):
        self.drawList = []

    def draw(self, phiAngle, thetaAngle, zoomMultiplier, dronePosition):
        #self.sortDrawList(phiAngle, thetaAngle, zoomMultiplier, dronePosition)
        for item in self.drawList:
            item.draw()

    def addDrawItem(self, instruction):
        self.drawList.append(self.drawItem(instruction))


    def sortDrawList(self,phiAngle, thetaAngle, zoomMultiplier, dronePosition):
        pass