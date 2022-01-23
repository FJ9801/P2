import cv2  # importar computer vision
import numpy as np
import serial
import time

vid = cv2.VideoCapture(0)  # capturar video desde la camara
vid.set(3, 320)  # adjust width
vid.set(4, 240)  # adjust height
vid.set(10, 140)  # adjust brillo


# funcion vacia para los trackbar
def empty(a):
    pass

time.sleep(3)
 
# ventana para controlar la cantidad de lineas en la imagen de siluetas
cv2.namedWindow("Parameters")
cv2.resizeWindow("Parameters", 400, 200)
cv2.createTrackbar("Threshold1", "Parameters", 0,255,empty)
cv2.createTrackbar("Threshold2", "Parameters", 255,255,empty)
cv2.createTrackbar("Threshold3", "Parameters", 255,255,empty)
cv2.createTrackbar("Threshold4", "Parameters", 255,255,empty)

ErrorLilas = [0, 0]
ErrorObs = [0, 0]
CentroLilas = [0, 0]
CentroObs = [0, 0]
LilasXY = [0, 0]
ObsXY = [0, 0]
Velocidad = [0, 0, 0, 0] # motorizq, motorder, frontal, conveyor
Detectado = False




# dibujarle un contorno a las lilas
def getcontours(imagen,imgCountour):
    contours, hierarchy = cv2.findContours(imagen, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 400:
            cv2.drawContours(imgCountour, cnt, -1, (0, 0, 255), 3)
            peri = cv2.arcLength(cnt, True)  # desde aqui se calcula el perimetro para enjaular la figura
            aprox = cv2.approxPolyDP(cnt, 0.06 * peri, True)
            #print(len(aprox))
            x, y, w, h = cv2.boundingRect(aprox)  # coordenadas del rectangulo que lo cubre
            cv2.rectangle(imgContour, (x, y), (x + w, y + h), (255,100,0), 2)
            # poner el nombre de lilas
            cv2.putText(imgContour, "Lilas", (x + int(w/8), y + int(h/1.5) ), cv2.FONT_ITALIC, 0.7, (0, 255, 0), 2)
            if((x + int(w/2) != None) or (y + int(h/2) != None)):
                CentroLilas[0] = x + int(w/2)
                CentroLilas[1] = y + int(h / 2)
                return CentroLilas[0], CentroLilas[1]


# dibujarle un contorno a los obstaculos
def getcontoursOBS(imagen,imgCountour):
    contours, hierarchy = cv2.findContours(imagen, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE, )
    for cnt in contours:
         area = cv2.contourArea(cnt)
         if area > 1600:
             cv2.drawContours(imgCountour, cnt, -1, (255, 0, 0), 3)
             peri = cv2.arcLength(cnt, False)  # desde aqui se calcula el perimetro para enjaular la figura
             if peri >= 0:
                #print(peri)
                #print("peri")
                aprox = cv2.approxPolyDP(cnt, 0.06 * peri, False)
                x, y, w, h = cv2.boundingRect(aprox)  # coordenadas del rectangulo que lo cubre
                cv2.rectangle(imgContour, (x, y), (x + w, y + h), (255,100,0), 2)
                # poner el nombre 2de obstaculos
                cv2.putText(imgContour, "Obstaculo", (x + int(w/8), y + int(h/1.5)), cv2.FONT_ITALIC, 0.7, (0, 255, 0), 2)
                if((x + int(w/2) != None) or (y + int(h/2) != None)):
                    CentroObs[0] = x + int(w/2)
                    CentroObs[1] = y + int(h / 2)
                    return CentroObs[0], CentroObs[1]


while True:

    success, img = vid.read()  # crear un loop para mostrar todos los frames del video

    imgContour = img.copy()
    imgBlur = cv2.GaussianBlur(img, (9,9), 15)
    imgBlur = cv2.line(imgBlur, (0, 0), (320, 0), (0,0,0), 15)
    imgBlur = cv2.line(imgBlur, (0, 0), (0, 240), (0,0,0), 15)
    imgBlur = cv2.line(imgBlur, (320, 0), (320, 240), (0,0,0), 15)
    imgBlur = cv2.line(imgBlur, (0, 240), (320, 240), (0,0,0), 15)
    # imgGray = cv2.cvtColor(imgBlur, cv2.COLOR_BGR2GRAY)

    hsv_frame = cv2.cvtColor(imgBlur, cv2.COLOR_BGR2HSV)

    # detectar todos los colores
    low_all = np.array([0, 0, 0])
    high_all = np.array([179, 255, 255])
    all_mask = cv2.inRange(hsv_frame, low_all, high_all)

    # detectar color azul
    low_blue = np.array([100, 15, 25])
    high_blue = np.array([150, 255, 255])
    blue_mask = cv2.inRange(hsv_frame, low_blue, high_blue)

    # detectar color verde
    low_green = np.array([50, 25, 5])
    high_green = np.array([100, 255, 255])
    green_mask = cv2.inRange(hsv_frame, low_green, high_green)

    blue = cv2.bitwise_and(imgBlur, imgBlur, mask=blue_mask)
    green = cv2.bitwise_and(imgBlur, imgBlur, mask=green_mask)
    all_colors = cv2.bitwise_and(imgBlur, imgBlur, mask= all_mask-green_mask-blue_mask) # SE CAMBIO DE IMG A IMGBLUR

    # aqui va el codigo para detectar el objeto
    threshold1 = cv2.getTrackbarPos("Threshold1", "Parameters")
    threshold2 = cv2.getTrackbarPos("Threshold2", "Parameters")
    threshold3 = cv2.getTrackbarPos("Threshold3", "Parameters")
    threshold4 = cv2.getTrackbarPos("Threshold4", "Parameters")
    imgCannyLilas = cv2.Canny(green, threshold1, threshold2)
    imgCannyObs = cv2.Canny(all_colors, threshold3, threshold4)
    kernel = np.ones((1,1))
    kernel2 = np.ones((1,1))
    imgDilatedLilas = cv2.dilate(imgCannyLilas, kernel, iterations=1)
    imgDilatedObs = cv2.dilate(imgCannyObs, kernel2, iterations=1)

    # encontrar el centro de los objetos


    LilasXY = getcontours(imgDilatedLilas,imgContour)
    ObsXY= getcontoursOBS(imgDilatedObs, all_colors)
    #print(LilasXY)
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=0)
    if(LilasXY != None):
        Detectado = True
        #print(LilasXY[0])
        #print(LilasXY[1])
        ErrorLilas[0] = LilasXY[0] - 160
        ErrorLilas[1] = 240 - LilasXY[1]
        print("Error es: ", ErrorLilas[0], " , ", ErrorLilas[1])
        if (Detectado):
            if (ErrorLilas[0] <= 50) and (ErrorLilas[0] >= -50): # esta alineado?
                x = int(ErrorLilas[1] * 1.5)
                if(ErrorLilas[1] <= 25):            # esta cerca?
                    Velocidad = [x, x, 30, 30]
                else:                               # no esta cerca
                    Velocidad = [x, x, 0, 0]
            else:                   # no esta alineado
                y = int(ErrorLilas[0] * 1)
                Velocidad[0] = y
                Velocidad[1] = -y
        print("Velocidad: ", Velocidad[0], ",", Velocidad[1])
    else:
        Detectado = False
        Velocidad = [-60, 60, 0, 0]
    
    msg = b'%i,%i,%i,%i\n' % (Velocidad[0],Velocidad[1],Velocidad[2] ,Velocidad[3])
    print(msg)
    ser.flush()
    ser.write(msg)
    time.sleep(.1)
    #tempo = ser.readline().decode('utf-8').rstrip()
    #   print(tempo)
    print("OK")
    # mostrar imagenes
    #cv2.imshow("Video", img)
    #cv2.imshow("Blur", imgBlur)
    cv2.imshow("Green", green)
    cv2.imshow("CannyLilas", imgCannyLilas)
    #cv2.imshow("DilatedLilas", imgDilatedLilas)
    cv2.imshow("Contour", imgContour)
    #cv2.imshow("Azul", blue)
    #cv2.imshow("DilatedObs", imgDilatedObs)
    #cv2.imshow("Todo", all_colors)

    # mantener el loop hasta que se presione la letra s
    if cv2.waitKey(1) & 0xFF == ord('s'):
        break
