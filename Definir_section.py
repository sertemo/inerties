import streamlit as st
import numpy as np
import secciones as sc
import graficar as gf
import pandas as pd
import aux_functions as af
import db
import time

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
DATABASE = db.get_database()

## FUNCIONES ##
def init_sesion(contenedor,img)->None:
    """Inicializa las variables de sesión
    """
    st.session_state["secciones"] = st.session_state.get("secciones",[])
    if st.session_state.get("seccion_compuesta",None) is None:
        gf.GraficarSeccion()._dibujar_ejes_coord(img)
        gf.GraficarSeccion()._dibujar_regla(img)
        contenedor.image(img)
    st.session_state["secciones_db"] = st.session_state.get("secciones_db",[])

@st.cache_data
def definir_ventana_personalizada(vent_x:int,vent_y:int)->np.ndarray:
    """Dadas las dimensionesde la ventana, retorna la imagen

    Parameters
    ----------
    vent_x : int
        _description_
    vent_y : int
        _description_

    Returns
    -------
    np.ndarray
        _description_
    """
    #!Hay que es escalar los valores de la ventana, no tengo muy claro por qué aún
    vent_x, vent_y = gf.GraficarSeccion()._escalar((vent_x,vent_y))
    img = np.zeros((vent_x,vent_y,3),dtype=np.uint8)
    img[::] = 180
    return img

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

def mostrar_secciones_cargadas()->None: #!No se usa
    """Itera sobre las secciones cargadas y las muestra en pantalla
    """
    for idx, seccion in enumerate(st.session_state["secciones"],start=1):
        section = seccion["seccion"]
        coordo = seccion["ubicacion"]
        f"**{idx}** - {section} - Coord:{coordo} "

def _get_color():
    #for _ in range(100):
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
            max_value=300.0,
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
            max_value=300.0,
            #key="x",
        )
        y = st.number_input(
            "largeur (y) en mm",
            step=10.0,
            format="%.1f",
            value=25.0,
            min_value=1.0,
            max_value=300.0,
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

def secciones_to_dict(nombre_seccion:str)->dict:
    """Devuelve el dict para meter en la base de datos,
    transformando cada clase en st.session_state por un dict

    Parameters
    ----------
    nombre_seccion : str
        _description_

    Returns
    -------
    dict
        _description_
    """
    #Primero tenemos que transformar las clases secciones de st.session_state en dict
    list_secciones_dict = [ 
        {
            "seccion" : sec["seccion"].to_dict(),
            "ubicacion" : sec["ubicacion"],
            "color" : sec["color"]

            }
            for sec in st.session_state.get("secciones",{})]
    
    return {
        "nombre_seccion" : nombre_seccion,
        "secciones" : list_secciones_dict,
    }

def insertar_db_seccion_compuesta(dict_seccion:dict)->None:
    """Recibe un dict que representa la seccion compuesta
    e inserta en db 

    Parameters
    ----------
    dict_seccion : dict
        _description_

    Returns
    -------
    _type_
        _description_
    """

    DATABASE["SeccionesCompuestas"].insert_one(dict_seccion)

def nombre_seccion_valido(nombre_seccion:str)->tuple[bool,str]:
    """Función para validar que el nombre de la sección no existe ya en la base de datos
    Si existe devuelve un error

    Parameters
    ----------
    nombre_seccion : str
        _description_
    """
    #Validamos que no esté vacío
    if nombre_seccion == "":
        return False, "Le nom de la section ne peut pas être vide."
    #Validamos que haya una seccion cargada
    if len(st.session_state.get("secciones",[])) == 0:
        return False, "Aucune section pour enregistrer"
    #Validamos que el nombre no exista ya:
    if DATABASE["SeccionesCompuestas"].find_one({"nombre_seccion" : nombre_seccion}) is not None:
        return False, "Le nom de la section existe déjà."

    return True, ""

if __name__ == '__main__':
    st.title("Sections Composées - Propriétés mécaniques")
    with st.expander("🟡 Informations Importantes"):
        st.markdown("""
                - Les distances :green[**x**] et :green[**y**] sont en :red[mm].
                - Le repère pour placer les sections non circulaires :green[à épaisseur] est \
                    le :red[centre] de l'épaisseur du coin :red[**gauche supérieur**].
                - Le repère pour placer les sections non circulaires :green[pleines] est le coin :red[**supérieur gauche**].
                - Le repère pour placer les sections circulaires est le :red[**centre**] du cercle.""")
    contenedor = st.empty()

    with st.sidebar:
        st.header("#️⃣ Choisir dimensions de la grille")

        vent_y = st.number_input(
            "Dimension x",
            step=10,
            help="Dimension x de la fenêtre",
            value=260,
            min_value=100,
            max_value=500,
        )
    
        vent_x = st.number_input(
            "Dimension y",
            step=10,
            help="Dimension x de la fenêtre",
            value=160,
            min_value=100,
            max_value=500,
        )
    img = definir_ventana_personalizada(vent_x,vent_y)
    #Inicializamos variables de sesion necesarias
    init_sesion(contenedor,img)
    db.sacar_secciones_db()

    with st.sidebar:
        st.header("🖊 Dessiner la section")
        st.subheader("1- Choisir géométrie 📐")

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
            af.reset_todo()

        with st.expander("Enregistrer la section 💾"):
            nombre_seccion = st.text_input(
                "Nom de la section",
            )
            guardar = st.button(
                "Enregistrer",
            )

            if guardar:
                nombre_valido, error_nombre = nombre_seccion_valido(nombre_seccion)
                if not nombre_valido:
                    st.error(f"{error_nombre}")
                                    
                else:
                    to_db = secciones_to_dict(nombre_seccion)
                    
                    try:
                        insertar_db_seccion_compuesta(to_db)
                        st.success("Enregistrement correct.")
                        time.sleep(2)
                        st.experimental_rerun()

                    except Exception as exc:
                        st.error("Une erreur s'est produite lors de l'enregistrement.")

        with st.expander("Voir sections dessinées"):
            mostrar_secciones_cargadas()

        st.caption("Done by STM w/💗 2023")
    af.cargar_seccion_compuesta()
    af.dibujar_seccion(img)
    
    if st.session_state.get("seccion_compuesta",None) is not None:
        cargar_dataframe()
    #st.session_state
