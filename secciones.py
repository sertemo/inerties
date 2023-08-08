import math
from typing import Union, Iterable

class Seccion:
  def __init__(self,dimensiones:list[Union[float,int],Union[float,int,None],Union[float,int,None]]):
    if not isinstance(dimensiones,Iterable):
      raise TypeError("Las dimensiones deben ser una lista o una tupla")
    self.dimensiones = dimensiones

    if "CircularMacizo" in self.__class__.__name__ :
      assert len(dimensiones) == 1, "(radio)"
      self.r = dimensiones[0]
      self.e, self.angulo = None, None
      self.y = self.x = self.r
      self.descripcion = f"(radio = {self.r} mm)"

    elif "CircularHueco" in self.__class__.__name__ :
      assert len(dimensiones) == 2, "(radio, espesor)"
      self.r, self.e = dimensiones
      self.x = self.y = self.r
      self.angulo = None
      self.descripcion = f"(radio = {self.r} mm, espesor = {self.e} mm)"

    elif "RectangularMacizo" in self.__class__.__name__ :
      assert len(dimensiones) == 3, "(longitud, ancho,ángulo)"
      self.x, self.y, self.angulo =  dimensiones
      self.r, self.e = None, None
      self.descripcion = f"(longitud = {self.x} mm, ancho = {self.y} mm, ángulo = {self.angulo}º)"

    elif "RectangularHueco" in self.__class__.__name__ :
      assert len(dimensiones) == 4, "(longitud, ancho, espesor,ángulo)"
      self.x, self.y, self.e, self.angulo =  dimensiones
      self.r = None
      self.descripcion = f"(longitud = {self.x} mm, ancho = {self.y} mm, espesor = {self.e} mm, ángulo = {self.angulo}º)"

  @property
  def tipo(self):
    return f"{self.__class__.__name__}"
  
  def to_dict(self):
    """Función para transformar a dict la información necesaria para\
    guardar en base de datos y posteriormente poder reconstruir la clase
    """
    seccion_dict = {
      "tipo_seccion" : self.__class__.__name__,
      "dimensiones" : self.dimensiones
    }
    return seccion_dict

  def __repr__(self):
    lista_params = [p for p in [self.x,self.y,self.e, self.angulo] if p is not None]
    return f'''{self.__class__.__name__}{lista_params}'''

class SeccionRectangularMacizo(Seccion):
  def __init__(self,dimensiones:tuple[Union[float,int],Union[float,int,None],Union[float,int,None]]):
    ''' El eje x es el eje horizontal,\n
    el eje y es el eje vertical.\n
    Para las dimensiones escribir siempre (x,y) en este orden.'''
    super().__init__(dimensiones)

  @property
  def area_centroide(self):
    ''' Centroide referido ahora siempre al centro del rectangulo.'''
    area = self.x * self.y
    centroide = (0,0)
    return area, centroide

  @property
  def momentos_inercia(self):
    ''' Devuelve los momentos de inercia de la seccion con respecto
    al centroide de la sección. en mm4 '''
    Ix = (self.x * self.y ** 3) / 12
    Iy = (self.y * self.x ** 3) / 12

    #Lógica para saber si está girado
    theta = math.radians(self.angulo)
    Ixx = Ix * math.cos(theta)**2 + Iy * math.sin(theta)**2
    Iyy = Ix * math.sin(theta)**2 + Iy * math.cos(theta)**2
    return Ixx, Iyy

  @property
  def modulos_resistentes(self):
    ''' Devuelve los modulos resistentes Wx, Wy de la seccion
    con respecto al centroide '''
    Ix, Iy = self.momentos_inercia
    Wx = Ix / (self.y/2)
    Wy = Iy / (self.x/2)
    # Calcular los módulos resistentes en la dirección x e y
    theta = math.radians(self.angulo)
    Wxx = Wx * math.cos(theta) ** 2 + Wy * math.sin(theta) ** 2
    Wyy = Wx * math.sin(theta) ** 2 + Wy * math.cos(theta) ** 2
    return Wx, Wy

class SeccionRectangularHueco(Seccion):
  def __init__(self,dimensiones:tuple[Union[float,int],Union[float,int,None],Union[float,int,None]]):
    ''' El eje x es el eje horizontal,\n
    el eje y es el eje vertical.\n
    e es el espesor.
    (longitud,ancho,espesor,ángulo)
    Para las dimensiones escribir siempre (x,y,e,alpha) en este orden.'''
    super().__init__(dimensiones)

  @property
  def area_centroide(self):
    ''' Devuelve el area y la posición del centroide respecto a la
    esquina superior izquierda. Siempre en mm.'''
    area_total = self.x * self.y
    area_hueco = (self.x - 2 * self.e) * (self.y - 2 * self.e)
    area = area_total - area_hueco
    centroide = (0,0)
    return area, centroide

  @property
  def momentos_inercia(self):
    ''' Devuelve los momentos de inercia de la seccion con respecto
    al centroide de la sección. en mm4 '''
    Ix_total = (self.x * self.y ** 3) / 12
    Iy_total = (self.y * self.x ** 3) / 12
    longitud_hueco = self.x - 2 * self.e
    ancho_hueco = self.y - 2 * self.e
    Ix_hueco = (longitud_hueco * ancho_hueco ** 3) / 12
    Iy_hueco = (ancho_hueco * longitud_hueco ** 3) / 12
    Ix = Ix_total - Ix_hueco
    Iy = Iy_total - Iy_hueco

    #Lógica para saber si está girado
    theta = math.radians(self.angulo)
    Ixx = Ix * math.cos(theta)**2 + Iy * math.sin(theta)**2
    Iyy = Ix * math.sin(theta)**2 + Iy * math.cos(theta)**2
    return Ixx, Iyy

  @property
  def modulos_resistentes(self):
    ''' Devuelve los modulos resistentes Wx, Wy de la seccion
    con respecto al centroide '''
    Ix, Iy = self.momentos_inercia
    _, (x, y) = self.area_centroide
    Wx = Ix / (self.y/2)
    Wy = Iy / (self.x/2)
    # Calcular los módulos resistentes en la dirección x e y
    theta = math.radians(self.angulo)
    Wxx = Wx * math.cos(theta) ** 2 + Wy * math.sin(theta) ** 2
    Wyy = Wx * math.sin(theta) ** 2 + Wy * math.cos(theta) ** 2
    return Wxx, Wyy

class SeccionCircularHueco(Seccion):
  ''' Introducir el radio de la sección. '''
  def __init__(self,dimensiones:tuple[Union[float,int],Union[float,int,None],Union[float,int,None]]):
    ''' El eje x es el eje horizontal,\n
    el eje y es el eje vertical.\n
    e es el espesor.
    (longitud,ancho,espesor)
    Para las dimensiones escribir siempre (x,y,e) en este orden.'''
    super().__init__(dimensiones)

  @property
  def area_centroide(self):
    ''' Devuelve el area y la posición del centroide respecto al
    centro de la circunferencia. Siempre en mm.'''
    radio_interior = self.r - self.e
    area_total = math.pi * self.r ** 2
    area_hueco = math.pi * radio_interior ** 2
    area = area_total - area_hueco
    centroide = (0, 0)
    return area, centroide

  @property
  def momentos_inercia(self):
    ''' Devuelve los momentos de inercia de la seccion con respecto
    al centroide de la sección. '''
    radio_hueco = self.r - self.e
    Ix_total = Iy_total = (math.pi * self.r ** 4) / 4
    Ix_hueco = Iy_hueco = (math.pi * radio_hueco ** 4) / 4
    Ix = Ix_total - Ix_hueco
    Iy = Iy_total - Iy_hueco
    return Ix, Iy

  @property
  def modulos_resistentes(self):
    ''' Devuelve los modulos resistentes Wx, Wy de la seccion
    con respecto al centroide '''
    Ix, Iy = self.momentos_inercia
    x, y = self.centroide
    Wx = Wy = Ix / self.r
    return Wx, Wy

class SeccionCircularMacizo(Seccion):
  ''' Introducir el radio de la sección. '''
  def __init__(self,dimensiones:tuple[Union[float,int],Union[float,int,None],Union[float,int,None]]):
    ''' El eje x es el eje horizontal,\n
    el eje y es el eje vertical.\n
    e es el espesor.
    (longitud,ancho,espesor)
    Para las dimensiones escribir siempre (x,y,e) en este orden.'''
    super().__init__(dimensiones)

  @property
  def area_centroide(self):
    ''' Devuelve el area y la posición del centroide respecto al
    centro de la circunferencia. Siempre en mm.'''
    area = math.pi * self.r ** 2
    self.centroide = (0, 0)
    return area, self.centroide

  @property
  def momentos_inercia(self):
    ''' Devuelve los momentos de inercia de la seccion con respecto
    al centroide de la sección. '''
    Ix = Iy = (math.pi * self.r ** 4) / 4
    return Ix, Iy

  @property
  def modulos_resistentes(self):
    ''' Devuelve los modulos resistentes Wx, Wy de la seccion
    con respecto al centroide '''
    Ix, Iy = self.momentos_inercia
    x, y = self.centroide
    Wx = Wy = Ix / self.r
    return Wx, Wy

class SeccionCompuesta:
    def __init__(self, secciones:list[dict]):
        self.secciones = secciones

    @property
    def area_centroide(self):
        ''' Devuelve la posición (x,y) del centroide de la sección compuesta en mm.
        La referencia es el centro de la sección. '''

        area_total = 0
        centroide_total_x = 0
        centroide_total_y = 0

        for seccion in self.secciones:
            ubicacion = seccion['ubicacion']

            area, centroide = seccion["seccion"].area_centroide

            area_total += area
            centroide_total_x += (centroide[0] + ubicacion[0]) * area
            centroide_total_y += (centroide[1] + ubicacion[1]) * area

        centroide_composicion = (centroide_total_x / area_total, centroide_total_y / area_total)

        return area_total,centroide_composicion

    @property
    def momentos_inercia(self):
      _,centroid_composicion = self.area_centroide

      Ix_total = 0
      Iy_total = 0

      for seccion in self.secciones:
          ubicacion = seccion['ubicacion']

          area, centroide_seccion = seccion["seccion"].area_centroide
          Ix, Iy = seccion["seccion"].momentos_inercia

          # Aplicar el teorema del eje paralelo
          dx = abs(centroid_composicion[0] - (ubicacion[0]+centroide_seccion[0]))
          dy = abs(centroid_composicion[1] - (ubicacion[1]+centroide_seccion[1]))

          Ix += area * dy ** 2
          Iy += area * dx ** 2

          Ix_total += Ix
          Iy_total += Iy

      return Ix_total, Iy_total

    @property
    def modulos_resistentes(self):
      #calculamos los puntos mas alejados del centroide
      #Para la inercia Ix, calculamos los puntos y
      _,(x_centroide, y_centroide) = self.area_centroide
      puntos_alejados_x = []
      puntos_alejados_y = []

      for seccion in self.secciones:
        #En el caso de seccion circular el centroide y la referencia de la ubicacion coinciden
        puntos_alejados_x.append(abs(seccion["ubicacion"][1] + seccion["seccion"].y/2 - y_centroide))
        puntos_alejados_y.append(abs(seccion["ubicacion"][0] + seccion["seccion"].x/2 - x_centroide))

      Ix, Iy = self.momentos_inercia
      Wx = Ix / max(puntos_alejados_x)
      Wy = Iy / max(puntos_alejados_y)
      return Wx, Wy

    def __repr__(self):
      informacion_secciones = "SeccionCompuesta(\n"
      for idx,seccion in enumerate(self.secciones,start=1):
        informacion_secciones += f"\t{idx}-" + seccion["seccion"].tipo + seccion["seccion"].descripcion + "\n"
      informacion_secciones + ")\n"

      informacion_secciones += f'''\n---- Propiedades mecánicas ----
      \nReferencia (0,0) desde la esquina superior izquierda
      \n---- Área y centroide ----\nArea Total: {self.area_centroide[0]:.1f} mm2\nPosición centroide (x,y): {self.area_centroide[1]}
      \n---- Inercias ----\nIx: {self.momentos_inercia[0]/1e4:,.1f} cm4\nIy: {self.momentos_inercia[1]/1e4:,.1f} cm4
      \n---- Modulos resistentes ----\nWx: {self.modulos_resistentes[0]/1e3:,.1f} cm3\nWy: {self.modulos_resistentes[1]/1e3:,.1f} cm3
      \n------------
      '''
      return informacion_secciones