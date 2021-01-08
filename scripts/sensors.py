def soilMoisture(min, max, analog):
    return (1 - (analog - min)/(max - min)) * 100
    
# print(soilMoisture(246, 510, 444))