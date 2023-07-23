import streamlit as st
import cv2 as cv
import numpy as np
import secciones as sc
import graficar as gf
import pandas as pd

st.set_page_config(
    page_title="Calculer Sections Multiples",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="auto",
)

## CONSTANTES ##
SECTION_MAPPING = {
    "Tube Carré" : sc.SeccionCuadradoHueco,
    "Carré plein" : sc.SeccionCuadradoMacizo,
    "Tube Rectangle" : sc.SeccionRectangularHueco,
    "Rectangle plein" : sc.SeccionRectangularMacizo,
    "Tube Rond" : sc.SeccionCircularHueco,
    "Rond Plein" : sc.SeccionCircularMacizo,
}

## FUNCIONES ##
def init_sesion(contenedor)->None:
    """Inicializa las variables de sesión
    """
    st.session_state["secciones"] = st.session_state.get("secciones",[])
    if st.session_state.get("seccion_compuesta",None) is None:
        img = np.zeros((800,800,3),dtype=np.uint8)
        gf.GraficarSeccion()._dibujar_ejes_coord(img)
        contenedor.image(img)

def borrar_contenedor(contenedor)->None:
    contenedor.empty()

def get_section_names(section_mapping:dict)->list[str]:
    """Devuelve una lista de las secciones para el selectbox

    Parameters
    ----------
    section_mapping : dict
        _description_

    Returns
    -------
    list[str]
        _description_
    """
    return [sec for sec in section_mapping.keys()]

def dibujar_seccion()->None:
    """Dibuja la sección compuesta que esté cargada en la sesion en "seccion_compuesta"
    """
    if st.session_state.get("seccion_compuesta",None) is not None:
        gf.GraficarSeccion().fit(seccion=st.session_state["seccion_compuesta"]).dibujar_seccion()

def mostrar_secciones_cargadas()->None:
    """Itera sobre las secciones cargadas y las muestra en pantalla
    """
    for idx, seccion in enumerate(st.session_state["secciones"],start=1):
        section = seccion["seccion"]
        coordo = seccion["ubicacion"]
        f"**{idx}** - {section} - Coord:{coordo} "

def cargar_seccion_compuesta()->None:
    """Carga la lista de secciones independientes en la clase SeccionCompuesta y lo añade
    a la sesión
    """
    if len(st.session_state["secciones"]) > 0:
        st.session_state["seccion_compuesta"] = sc.SeccionCompuesta(st.session_state["secciones"])

def _get_color():
    for _ in range(100):
        red = np.random.randint(50,200)
        green = np.random.randint(50,200)
        blue = np.random.randint(50,200)
        return (red, green, blue)

def agregar_seccion(
        seccion:str,
        dimensiones:list[float],
        coord_x:float,
        coord_y:float)->None:
    """ Agrega la sección a la variable de sesión  """
    #Sacamos la clase correspondiente a la seccion
    clase_seccion = SECTION_MAPPING[seccion]
    #Filtramos las dimensiones
    dimensiones = [dim for dim in dimensiones if dim is not None]
    st.session_state["secciones"].append({
        "seccion" : clase_seccion(dimensiones),
        "ubicacion" : (coord_x,coord_y),
        "color" : _get_color()
    })

def borrar_seccion()->None:
    if len(st.session_state["secciones"]) > 0:        
        if len(st.session_state["secciones"]) == 1:
            del st.session_state["seccion_compuesta"]
        st.session_state["secciones"].pop()
        st.experimental_rerun()
    else:
        st.error("La liste de sections est déjà vide")
    
def validacion():
    "validar inputs"
    "⛔"
    pass

def cargar_dataframe()->None:
    """Carga DataFrame con los datos más relevantes de la sección compuesta.
    """
    secc_compuesta:sc.SeccionCompuesta = st.session_state["seccion_compuesta"]
    area, centroide_posicion = secc_compuesta.area_centroide
    Ix, Iy = secc_compuesta.momentos_inercia
    Wx, Wy = secc_compuesta.modulos_resistentes
    df = pd.DataFrame(
        [
            {
                "Surface Totale (mm2)" : f"{area:.1f}",
                "Position x cdm (mm)" : f"{centroide_posicion[0]:.2f}",
                "Position y cdm (mm)" : f"{centroide_posicion[1]:.2f}",
                "Ix (cm4)" : f"{Ix/1e4:.1f}",
                "Iy (cm4)" : f"{Iy/1e4:.1f}",
                "Wx (cm3)" : f"{Wx/1e3:.1f}",
                "Wy (cm3)" : f"{Wy/1e3:.1f}"
                }
        ],
        index=["Composition"]
    )

    st.dataframe(df,use_container_width=True)

def mostrar_opciones_seccion(seccion:str)->None:
    """Muestra los campos de texto para rellenar los parametros de la seccion.

    Parameters
    ----------
    seccion : str
        _description_

    Returns
    -------
    _type_
        Retorna los valores de x, y, e
    """
    x,y,e = None, None, None

    if "Carré" in seccion:
        x = st.number_input(
            "côtés (x) en mm",
            step=10.0,
            value=25.0,
            min_value=20.0,
            max_value=200.0,
            format="%.1f"
            #key="x",
        )
        if "Tube" in seccion:
            e = st.number_input(
                "épaisseur du carré (e) en mm",
                step=1.0,
                value=0.5,
                min_value=0.5,
                max_value=10.0,
                format="%.1f"
                #key="e",
            )
    if "Rectangle" in seccion:
        x = st.number_input(
            "longueur (x) en mm",
            step=10.0,
            format="%.1f",
            value=25.0,
            min_value=1.0,
            max_value=200.0,
            #key="x",
        )
        y = st.number_input(
            "largeur (y) en mm",
            step=10.0,
            format="%.1f",
            value=25.0,
            min_value=1.0,
            max_value=200.0,
            #key="y",
        )
        if "Tube" in seccion:
            e = st.number_input(
                "épaisseur du rectangle (e) en mm",
                step=1.0,
                value=0.5,
                min_value=0.5,
                max_value=10.0,
                format="%.1f",
                #key="e",
            )
    if "Rond" in seccion:
        x = st.number_input(
            "ø (d) en mm",
            step=10.0,
            value=25.0,
            min_value=25.0,
            max_value=200.0,
            format="%.1f"
            #key="x",
        )
        x = x / 2
        if "Tube" in seccion:
            e = st.number_input(
                "épaisseur du rond (e) en mm",
                step=1.0,
                value=0.5,
                min_value=0.5,
                max_value=10.0,
                format="%.1f"
                #key="e",
            )
    return x, y, e

def reset_todo()->None:
    """Borra todas las secciones
    """
    if st.session_state.get("secciones",None) is not None:
        del st.session_state["secciones"]
    if st.session_state.get("seccion_compuesta",None) is not None:
        del st.session_state["seccion_compuesta"]
    st.experimental_rerun()

if __name__ == '__main__':
    st.title("Sections Composées - Propriétés mécaniques")
    contenedor = st.empty()
    #Inicializamos variables de sesion necesarias
    init_sesion(contenedor)

    with st.sidebar:
        st.header("🖊 Options")
        st.subheader("1- Choisir section 📐")

        seccion = st.selectbox(
            "Type de section",
            get_section_names(SECTION_MAPPING),
        )

        x, y, e = mostrar_opciones_seccion(seccion)

        st.subheader("2- Choisir emplacement ⬇➡")
        coord_x = st.number_input(
            "Coordonnée x (mm) (vers la droite)",
            step=10.0,
            format="%.1f",
            help="Coordonnée x du coin supérieur gauche si\
                \nla section est un carré ou rectangle. Coordonné x\
                \ndu centre du cercle si section rond."
            #key="x",
        )
        coord_y = st.number_input(
            "Coordonnée y (mm) (vers le bas)",
            step=10.0,
            format="%.1f",
            help="Coordonnée y du coin supérieur gauche si\
                \nla section est un carré ou rectangle. Coordonné y\
                \ndu centre du cercle si section rond."
            #key="x",
        )
        col1, col2, col3 = st.columns(3)
        with col1:
            agregar = st.button(
                "Ajouter section",
                help="Ajoute la section"
            )
        with col2:
            borrar = st.button(
                "Effacer section",
                help="Efface la dernière section ajoutée"
            )
        
        with col3:
            borrar_todo = st.button(
                "Effacer Tout",
                help="Efface tout pour recommencer",
            )

        if agregar:
            borrar_contenedor(contenedor)
            agregar_seccion(seccion,[x,y,e],coord_x,coord_y)
        if borrar:
            borrar_seccion()
        if borrar_todo:
            reset_todo()

        mostrar_secciones_cargadas()
        st.caption("STM 2023")
    cargar_seccion_compuesta()
    dibujar_seccion()
    if st.session_state.get("seccion_compuesta",None) is not None:
        cargar_dataframe()
    #st.session_state
