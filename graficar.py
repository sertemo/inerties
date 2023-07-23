import cv2 as cv
import numpy as np
from typing import Iterable, Union
import secciones as sc
import streamlit as st

class GraficarSeccion:

    def __init__(
            self,
            pad_ventana:tuple[int,int]=(50,50),
            factor_escala:int=5,
            ):
        
        self.PAD_VENTANA = pad_ventana
        self.COLOR_VENTANA = (0,0,0)
        self.ESC = factor_escala
        self.COLOR_BLACK = (0,0,0)
        self.COLOR_WHITE = (255,255,255)
        self.COLOR_RED = (248,10,0)
        self.FONT = cv.FONT_HERSHEY_COMPLEX_SMALL

    def fit(self,seccion:sc.SeccionCompuesta):
        self.seccion = seccion
        return self

    def _definir_dimensiones_ventana(self):
        vent_x = max([ seccion["seccion"].x for seccion in self.seccion.secciones])
        vent_y = max([ seccion["seccion"].y for seccion in self.seccion.secciones])
        vent_x += 2 * self.PAD_VENTANA[0]
        vent_y += 2 * self.PAD_VENTANA[1]
        return self._escalar((vent_y, vent_x))

    def _escalar(self,valores:Union[Iterable,int])->list:
        #escala y transforma en int para poder dibujarlo
        if not isinstance(valores,Iterable):
            return int(valores * self.ESC)
        else:
            output = []
            for valor in valores:
                output.append(int(self.ESC * valor))
            return output

    def _dibujar_centroide(self,img:np.ndarray,coord:tuple[int,int])->None:
        #Añadimos el padding
        x = coord[0] + self.PAD_VENTANA[0]
        y = coord[1] + self.PAD_VENTANA[1]
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

    def _dibujar_ejes_coord(self,img:np.ndarray)->None:
        ''' Dibuja los ejes de coordenadas x e y de referencia de la figura completa '''
        long_ejes = self._escalar(10)
        x, y = self._escalar(self.PAD_VENTANA)
        #Eje x
        cv.arrowedLine(img,pt1=(x,y), pt2=(x+long_ejes,y),color=self.COLOR_WHITE,thickness=3)
        cv.putText(img,'x',(x+long_ejes,y+self._escalar(-3)), self.FONT, self._escalar(0.25),self.COLOR_WHITE,1,cv.LINE_AA)
        #Eje y
        cv.arrowedLine(img,pt1=(x,y), pt2=(x,y+long_ejes),color=self.COLOR_WHITE,thickness=3)
        cv.putText(img,'y',(x - self._escalar(5),y+long_ejes + self._escalar(5)), self.FONT, self._escalar(0.25),self.COLOR_WHITE,1,cv.LINE_AA)

    def dibujar_seccion(self):
        img = np.zeros((*(self._definir_dimensiones_ventana()),3),dtype=np.uint8)
        for seccion in self.seccion.secciones:
            #ubicacion de la seccion
            x = seccion["ubicacion"][0]
            y = seccion["ubicacion"][1]
            color = seccion["color"]
            tipo_seccion = seccion["seccion"].tipo
            #añadimos el padding
            x += self.PAD_VENTANA[0]
            y += self.PAD_VENTANA[1]

            if "Rectangular" in tipo_seccion or "Cuadrado" in tipo_seccion:
                dx, dy = seccion["seccion"].x, seccion["seccion"].y
                x, y, dx, dy = self._escalar((x,y,dx,dy))
                cv.rectangle(img= img,pt1= (x,y),pt2= (x+dx,y+dy), color=color,thickness=-1)
                if "Hueco" in tipo_seccion:
                    e = self._escalar(seccion["seccion"].e)
                    cv.rectangle(img=img, pt1=(x+e,y+e), pt2=(x+dx-e,y+dy-e),color=self.COLOR_BLACK,thickness=-1)

            if "Circular" in tipo_seccion:
                radio = seccion["seccion"].x
                x, y, radio = self._escalar((x,y,radio))
                cv.circle(img= img,center= (x,y),radius=radio, color=color,thickness=-1)
                if "Hueco" in tipo_seccion:
                    e = self._escalar(seccion["seccion"].e)
                    cv.circle(img=img, center=(x,y), radius=radio-e,color=self.COLOR_BLACK,thickness=-1)

        #Dibujamos el centroide de la seccion compuesta
        self._dibujar_centroide(img,self.seccion.area_centroide[1])
        self._dibujar_ejes_coord(img)

        st.image(img)
