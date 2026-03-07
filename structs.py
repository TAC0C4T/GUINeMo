# Each object of this class is a single simulation
class paramSet:
    def __init__(self,
                angle: int, 
                pulseWidth: float, 
                pulseLength: float, 
                ipi: float, 
                numPulse: int, 
                pulseType: str, 
                timeStep: float, 
                firedLow: int, 
                firedHigh: int, 
                firedTolerance: int, 
                neuronPos: tuple[float, float, float], 
                neuronOrientation: tuple[float, float, float], 
                coilPos: tuple[float, float, float], 
                neuronAxis: tuple[float, float, float]):
        self.angle = angle
        self.pulseWidth = pulseWidth / 1000
        self.pulseLength = pulseLength / 1000
        self.ipi = ipi / 1000
        self.numPulse = numPulse
        self.pulseType = pulseType
        self.neuronPos = list(neuronPos)
        self.neuronOrientation = list(neuronOrientation)
        self.coilPos = list(coilPos)
        self.timeStep = timeStep / 1000
        self.firedLow = firedLow
        self.firedHigh = firedHigh
        self.firedTolerance = firedTolerance
        self.neuronAxis = list(neuronAxis)


class paramSetUniform:
    def __init__(self,
            angle: int, 
            pulseWidth: float, 
            pulseLength: float, 
            ipi: float, 
            numPulse: int, 
            pulseType: str, 
            timeStep: float, 
            firedLow: int, 
            firedHigh: int, 
            firedTolerance: int,):
        self.angle = angle
        self.pulseWidth = pulseWidth / 1000
        self.pulseLength = pulseLength / 1000
        self.ipi = ipi / 1000
        self.numPulse = numPulse
        self.pulseType = pulseType
        self.timeStep = timeStep / 1000
        self.firedLow = firedLow
        self.firedHigh = firedHigh
        self.firedTolerance = firedTolerance