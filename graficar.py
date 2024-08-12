import cv2 as cv
import numpy as np
from typing import Iterable, Union
import secciones as sc
import streamlit as st

class GraficarSeccion:

    def __init__(
            self,
            *,
            pad_ventana:tuple[int,int]=(50,35),
            factor_escala:int=5,
            pad_ejes:tuple[int,int]=(0,0),
            ):
        self.PAD_EJES = pad_ejes
        self.PAD_VENTANA = pad_ventana
        self.COLOR_VENTANA = (0,0,0)
        self.ESC = factor_escala
        self.COLOR_BLACK = (0,0,0)
        self.COLOR_WHITE = (255,255,255)
        self.COLOR_RED = (248,10,0)
        self.BLUE_DODGER = (30,144,255)
        self.FONT = cv.FONT_HERSHEY_COMPLEX_SMALL
        self.FONT_2 = cv.FONT_HERSHEY_COMPLEX

    def fit(self,seccion:sc.SeccionCompuesta):
        self.seccion = seccion
        return self
    
    def _escalar(self,valores:Union[Iterable,int],inverse:bool=False)->list: #inverse para desescalar
        #escala y transforma en int para poder dibujarlo
        if not isinstance(valores,Iterable):
            if inverse:
                return int(valores/self.ESC)
            return int(valores * self.ESC)
        else:
            output = []
            for valor in valores:
                if inverse:
                    output.append(int(valor/self.ESC))
                else:
                    output.append(int(self.ESC * valor))
            return output

    def _dibujar_centroide(self,img:np.ndarray,coord:tuple[int,int])->None:
        #Añadimos el padding
        x, y = coord 
        #Escalamos y pasamos a int
        x, y = self._escalar((x,y))
        r = self._escalar(3)
        cv.circle(img,center=(x,y),radius=r,color=self.COLOR_WHITE,thickness=-1)
        cv.ellipse(img,(x, y), (r, r), 0, 90, 180, self.COLOR_RED, cv.FILLED)
        cv.ellipse(img,(x, y), (r, r), 0, 270, 360, self.COLOR_RED, cv.FILLED)
        long_ejes = self._escalar(10)
        Ix, Iy = self.seccion.momentos_inercia
        Ix, Iy = Ix/1e4, Iy/1e4
        #Eje x
        cv.arrowedLine(img,pt1=(x,y), pt2=(x+long_ejes,y),color=self.COLOR_RED,thickness=2)
        cv.putText(img,f'Ix = {Ix:.1f} cm4',(x+long_ejes,y + self._escalar(-3)), self.FONT, self._escalar(0.25),self.COLOR_RED,1,cv.LINE_AA)
        #Eje y
        cv.arrowedLine(img,pt1=(x,y), pt2=(x,y+long_ejes),color=self.COLOR_RED,thickness=2)        
        cv.putText(img,f'Iy = {Iy:.1f} cm4',(x,y+long_ejes+ self._escalar(5)), self.FONT, self._escalar(0.25),self.COLOR_RED,1,cv.LINE_AA)

    def _dibujar_regla(self,img:np.ndarray)->None:
        """Dibuja una regla en la imagen en el sentido x e y

        Parameters
        ----------
        img : np.ndarray
            _description_
        """
        x, y = self.PAD_EJES #Definimos el origen
        dx, dy = self._escalar(self.PAD_VENTANA)

        dim_ventana = self._escalar(img.shape)
        vent_x, vent_y, _ = dim_ventana

        #Dibujamos la cuadrilla        
        step = self._escalar(10)
        #Eje X
        cv.line(img,pt1=(x,y), pt2=(x+vent_x+dx,y),color=self.COLOR_WHITE,thickness=1)   
        for i in range(0,vent_y,step):
            cv.line(img,pt1=(x,y+i), pt2=(x+vent_x+dx,y+i),color=self.COLOR_WHITE,thickness=1)
            cv.putText(img,str(self._escalar(i,inverse=True)),(x+8,y+i-6), self.FONT, self._escalar(0.2),self.COLOR_WHITE,1,cv.LINE_AA)
        #Eje Y
        cv.line(img,pt1=(x,y), pt2=(x,y+vent_y+dy),color=self.COLOR_WHITE,thickness=1)
        for i in range(0,vent_x+1,step):
            cv.line(img,pt1=(x+i,y), pt2=(x+i,y+vent_y+dy),color=self.COLOR_WHITE,thickness=1)
            cv.putText(img,str(self._escalar(i,inverse=True)),(x+i,y+30), self.FONT, self._escalar(0.2),self.COLOR_WHITE,1,cv.LINE_AA)

    def _dibujar_ejes_coord(self,img:np.ndarray)->None:
        ''' Dibuja los ejes de coordenadas x e y de referencia de la figura completa '''
        long_ejes = self._escalar(10)
        #x, y = self._escalar(self.PAD_VENTANA)
        x, y = self.PAD_EJES
        #Eje x
        cv.arrowedLine(img,pt1=(x,y), pt2=(x+long_ejes,y),color=self.BLUE_DODGER,thickness=3)
        cv.putText(img,'x',(x+long_ejes,y+self._escalar(3)), self.FONT, self._escalar(0.25),self.BLUE_DODGER,1,cv.LINE_AA)
        #Eje y
        cv.arrowedLine(img,pt1=(x,y), pt2=(x,y+long_ejes),color=self.BLUE_DODGER,thickness=3)
        cv.putText(img,'y',(x + self._escalar(1),y+long_ejes + self._escalar(3)), self.FONT, self._escalar(0.25),self.BLUE_DODGER,1,cv.LINE_AA)

    def _draw_rotated_rectangle(self,img, center, width, height, angle, color, thickness):
        # Construimos la caja del rectángulo
        box = cv.boxPoints(((center[0], center[1]), (width, height), angle))
        box = np.int(box)  # Aseguramos que las coordenadas sean enteras

        # Dibujamos el rectángulo en la imagen
        cv.drawContours(img, [box], 0, color, thickness)
        return img

    def dibujar_seccion(self,img,color_homogeneo:bool,numerar_secciones:bool)->None:
        self._dibujar_regla(img)

        for idx,seccion in enumerate(self.seccion.secciones,start=1):
            #ubicacion de la seccion
            x = seccion["ubicacion"][0]
            y = seccion["ubicacion"][1]
            color = seccion["color"]
            if color_homogeneo:
                color = self.BLUE_DODGER
            tipo_seccion = seccion["seccion"].tipo

            #instanciamos espesor para usar en padding de numero de seccion
            e = self._escalar(seccion["seccion"].e if seccion["seccion"].e is not None else 1)
            dx, dy = seccion["seccion"].x, seccion["seccion"].y
            x, y, dx, dy = self._escalar((x,y,dx,dy))
            angulo = seccion["seccion"].angulo

            if "Rectangular" in tipo_seccion:
                if "Macizo" in tipo_seccion:
                    self._draw_rotated_rectangle(img,(x,y),dx,dy,angulo,color,-1)
                else:
                    e = self._escalar(seccion["seccion"].e)
                    self._draw_rotated_rectangle(img,(x,y),dx,dy,angulo,color,e)

            elif "Circular" in tipo_seccion:                
                if "Macizo" in tipo_seccion:
                    cv.circle(img= img,center= (x,y),radius=dx, color=color,thickness=-1)
                elif "Hueco" in tipo_seccion:                                       
                    e = self._escalar(seccion["seccion"].e)
                    cv.circle(img=img, center=(x,y), radius=dx-e,color=color,thickness=e)

            if numerar_secciones:
                if "Macizo" in tipo_seccion:              
                        cv.putText(img,f"{idx}",(x+self._escalar(4),y+self._escalar(5)), self.FONT_2, self._escalar(0.3),self.COLOR_RED,1,cv.LINE_AA)
                else:
                    if "Circular" in tipo_seccion:
                        cv.putText(img,f"{idx}",(x+dx-self._escalar(2),y+self._escalar(5)), self.FONT_2, self._escalar(0.3),self.COLOR_RED,1,cv.LINE_AA)
                    else:
                        cv.putText(img,f"{idx}",(x+dx//2-e,y+dy//2-e), self.FONT_2, self._escalar(0.3),self.COLOR_RED,1,cv.LINE_AA)

        #Dibujamos el centroide de la seccion compuesta
        self._dibujar_centroide(img,self.seccion.area_centroide[1])
        self._dibujar_ejes_coord(img)
        st.image(img)
