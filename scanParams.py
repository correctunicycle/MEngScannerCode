#function that calculates secondary scanning parameters based on the scanning parameters inputted by the user
#to understand the expressions see software appendix uploaded with this code
def calculateParameters(parameterDictionary):
    samplingFrequency = 1/(parameterDictionary["samplingPeriod"] * parameterDictionary["picoTimebase"])
    yTotalSteps = parameterDictionary["mmMovedY"] *200
    yIncrements =  parameterDictionary["mmMovedY"]/parameterDictionary["yResolutionMm"]
    yStepIncrement = yTotalSteps/yIncrements
    print(yStepIncrement)


    pulseDiv = 4 
    numerator = (16 * 10e6 * parameterDictionary["motorSpeed"])
    denom = (2**pulseDiv)*2048*32
    vpps = (numerator/denom)/10

    microsteps = 8
    rps = (vpps)/(200*microsteps)

    speed = rps * 8

    numberofsteps = 35500

    numberofsteps = int(parameterDictionary["mmMovedX"]*200)  #return
    time =parameterDictionary["mmMovedX"]/speed
    NumberOfSamples = round(time * samplingFrequency)  #return this value
    PixelsPerSample = NumberOfSamples/(parameterDictionary["mmMovedX"]*(1/parameterDictionary['xResolutionMm']))
    PixelsPerSample = round(PixelsPerSample) #return
    

    print(numberofsteps)
    print(NumberOfSamples)
    print(PixelsPerSample)
    return numberofsteps, NumberOfSamples, PixelsPerSample, yStepIncrement, yIncrements,samplingFrequency



