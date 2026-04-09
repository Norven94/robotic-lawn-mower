import matplotlib.pyplot as plt 

#Dimensioner
ROBOT_WIDTH = 0.537
ROBOT_LENGHT = 0.415
PLOT_WIDTH = 30
PLOT_HEIGHT = 30

#Mindre köryta, robotens bredd
OFFSET = ROBOT_WIDTH

#Yttregräns
YTTRE_X = [0,PLOT_WIDTH,PLOT_WIDTH,0,0]
YTTRE_Y = [0,0,PLOT_HEIGHT,PLOT_HEIGHT,0]

#Köryta
INRE_X = [OFFSET,PLOT_WIDTH-OFFSET,PLOT_WIDTH-OFFSET,OFFSET,OFFSET]
INRE_Y = [OFFSET,OFFSET,PLOT_HEIGHT-OFFSET,PLOT_HEIGHT-OFFSET,OFFSET]

plt.plot(YTTRE_X,YTTRE_Y, color='black', label='Tomtgräns')
plt.plot(INRE_X,INRE_Y, color='green', label= "Köryta")

plt.show()