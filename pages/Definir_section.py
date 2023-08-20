import streamlit as st
import numpy as np
import secciones as sc
import graficar as gf
import pandas as pd
import aux_functions as af
import db
import time
import traducciones as tr

from collections import defaultdict

#Cargamos el idioma de la sesión para traducir los textos
idioma = st.session_state.get("idioma","fr")

st.set_page_config(
    page_title=tr.TRANS_MAPPING["page_title"][idioma],
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="auto",
)

## CONSTANTES ##
SECTION_MAPPING_FR = {
    "Tube Rectangle" : sc.SeccionRectangularHueco,
    "Rectangle plein" : sc.SeccionRectangularMacizo,
    "Tube Rond" : sc.SeccionCircularHueco,
    "Rond Plein" : sc.SeccionCircularMacizo,
}
SECTION_MAPPING_ES = {
    "Tubo Rectangular" : sc.SeccionRectangularHueco,
    "Rectangulo macizo" : sc.SeccionRectangularMacizo,
    "Tubo redondo" : sc.SeccionCircularHueco,
    "Redondo macizo" : sc.SeccionCircularMacizo,
}
DATABASE = db.get_database()

## FUNCIONES ##
def init_sesion(contenedor,img)->None:
    """Inicializa las variables de sesión
    """
    st.session_state["secciones"] = st.session_state.get("secciones",[])
    if st.session_state.get("seccion_compuesta") is None:
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

def mostrar_secciones_cargadas()->None:
    """Itera sobre las secciones cargadas y las muestra en pantalla
    """
    for idx, seccion in enumerate(st.session_state["secciones"],start=1):
        section = seccion["seccion"]
        coordo = seccion["ubicacion"]
        f"**{idx}** - {section} - Coord:{coordo} "

def _get_color():
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
    if idioma == "fr":        
        clase_seccion = SECTION_MAPPING_FR[seccion]
    elif idioma == "es":
        clase_seccion = SECTION_MAPPING_ES[seccion]
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
        st.error("La liste de sections est déjà vide") #TODO traduccion
    
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

    if "Rectang" in seccion:
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
        angulo = st.number_input(
            "angle (α) en º",
            step=1,
            value=0,
            min_value=-360,
            max_value=360,
            format="%d",
            help="Angle en sens anti-horaire par rapport à l'horizontale."
        )
        if "Tub" in seccion:
            e = st.number_input(
                "épaisseur du rectangle (e) en mm",
                step=1.0,
                value=0.5,
                min_value=0.5,
                max_value=10.0,
                format="%.1f",
                #key="e",
            )
    if "Rond" in seccion or "Redondo" in seccion:
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
        angulo = None
        if "Tub" in seccion:
            e = st.number_input(
                "épaisseur du rond (e) en mm",
                step=1.0,
                value=0.5,
                min_value=0.5,
                max_value=10.0,
                format="%.1f"
                #key="e",
            )
    return x, y, e, angulo

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

def insertar_db_seccion_compuesta(dict_seccion:dict,usuario_sesion:str)->None:
    """Recibe el dict de la seccion compuesta y el usuario y guarda la seccion
    en la db del usuario para poder recuperarla mas adelante

    Parameters
    ----------
    dict_seccion : dict
        _description_
    usuario_sesion : str
        _description_
    """

    DATABASE[usuario_sesion].insert_one(dict_seccion)

def nombre_seccion_valido(nombre_seccion:str,usuario_sesion:str)->tuple[bool,str]:
    """Función para validar que el nombre de la sección no existe ya en la base de datos
    Si existe devuelve un error

    Parameters
    ----------
    nombre_seccion : str
        _description_
    """
    #Validamos que no esté vacío
    if not nombre_seccion:
        return False, "Le nom de la section ne peut pas être vide."
    #Validamos que haya una seccion cargada
    if not st.session_state.get("secciones",[]):
        return False, "Aucune section pour enregistrer"
    #Validamos que el nombre no exista ya:
    if DATABASE[usuario_sesion].find_one({"nombre_seccion" : nombre_seccion}) is not None:
        return False, "Le nom de la section existe déjà."

    return True, ""

def añadir_configuraciones_a_dict(
        to_db: dict,
        *,
        dim_ventana: tuple[int,int],
        numerar_secciones: bool,
        color_homogeneo: bool)->dict:
    """Recoge el dict preparado para la db con los datos de sección
    y añade datos de configuración de visualizacion como dimensiones de pantalla
    y color de seccion o numeracion de las secciones
    to_dic
    """
    vent_x, vent_y = dim_ventana
    to_db["vent_x"] = vent_x
    to_db["vent_y"] = vent_y
    to_db["numerar_secciones"] = numerar_secciones
    to_db["color_homogeneo"] = color_homogeneo

    return to_db

if __name__ == '__main__':
    #Verificamos que haya usuario en sesión
    usuario_sesion = st.session_state.get("usuario","")
    if not usuario_sesion:
        st.warning(tr.TRANS_MAPPING["registrarse_mensaje"][idioma])
        st.stop()
    
    with st.expander("🟡 Informations Importantes"):
        st.markdown("""
                - Les distances :green[**x**] et :green[**y**] sont en :red[mm].
                - Le repère pour placer :green[**toutes**] les sections est le :red[**centre**] de la section.
                - Le sens de l'angle est :green[**anti-horaire**] par rapport à :red[**l'horizontale.**]
                - :red[**Attention!**] les :green[Wx et Wx] des sections compossées sont :red[**à revoir!**]""")
    contenedor = st.empty()

    with st.sidebar:
        st.header("#️⃣ Choisir dimensions de la grille")

        vent_y = st.number_input(
            "Dimension x",
            step=10,
            help="Dimension x de la fenêtre",
            value=st.session_state.get("vent_y",260), #prioriza valor cargado en sesion
            min_value=100,
            max_value=500,
        )
    
        vent_x = st.number_input(
            "Dimension y",
            step=10,
            help="Dimension x de la fenêtre",
            value=st.session_state.get("vent_x",160),
            min_value=100,
            max_value=500,
        )
    img = definir_ventana_personalizada(vent_x,vent_y)
    #Inicializamos variables de sesion necesarias
    init_sesion(contenedor,img)
    #Sacamos todas las secciones de la db de ese usuario
    db.sacar_secciones_db(usuario_sesion)

    with st.sidebar:
        st.header("🖊 Dessiner la section")
        st.subheader("1- Choisir géométrie 📐")

        numerar_secciones = st.checkbox(
            "Montrer numéros des sections",
            value=st.session_state.get("numerar_secciones",True),
        )
        color_homogeneo = st.checkbox(
            "Mono couleur",
            value=st.session_state.get("color_homogeneo",False),
        )

        seccion = st.selectbox(
            "Type de section",
            get_section_names(SECTION_MAPPING_FR if idioma == "fr" else SECTION_MAPPING_ES),
        )

        x, y, e, angulo = mostrar_opciones_seccion(seccion)

        st.subheader("2- Choisir emplacement ⬇➡")
        coord_x = st.number_input(
            "Coordonnée x (mm) (vers la droite)",
            step=10.0,
            value=vent_y/2,
            format="%.1f",
            help="Coordonnée x du centre de la section."
            #key="x",
        )
        coord_y = st.number_input(
            "Coordonnée y (mm) (vers le bas)",
            step=10.0,
            value=vent_x/2,
            format="%.1f",
            help="Coordonnée y du centre de la section."
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
            agregar_seccion(seccion,[x,y,e,angulo],coord_x,coord_y)
        if borrar:
            borrar_seccion()
        if borrar_todo:
            af.reset_todo()

        with st.expander("Enregistrer la section 💾"):
            st.write(f"Sections disponibles pour :blue[*{usuario_sesion}*] : {db._devolver_secciones_restantes(usuario_sesion)}")
            nombre_seccion = st.text_input(
                "Nom de la section",
            )
            guardar = st.button(
                "Enregistrer",
            )

            if guardar:
                nombre_valido, error_nombre = nombre_seccion_valido(nombre_seccion,usuario_sesion)
                if not nombre_valido:
                    st.error(f"{error_nombre}")
                                    
                else:
                    if not db.verificar_secciones_restantes(usuario_sesion):
                        st.error("Vous ne pouvez plus enregistrer de sections. Vous avez atteint la limite")
                    else:
                        to_db = secciones_to_dict(nombre_seccion)
                        #Guardamos la configuración de la pantalla y las opciones de visualización
                        to_db = añadir_configuraciones_a_dict(
                            to_db,
                            dim_ventana=(vent_x,vent_y),
                            numerar_secciones=numerar_secciones,
                            color_homogeneo=color_homogeneo)                        
                        
                        try:
                            insertar_db_seccion_compuesta(to_db,usuario_sesion)
                            st.success("Enregistrement correct.")
                            db.reducir_secciones_restantes(usuario_sesion)
                            with st.spinner("Patientez..."):
                                time.sleep(2)
                            st.experimental_rerun()

                        except Exception as exc:
                            st.error(f"Une erreur s'est produite lors de l'enregistrement: {exc}")

        with st.expander("Voir sections dessinées"):
            mostrar_secciones_cargadas()
        
    af.cargar_seccion_compuesta()
    af.dibujar_seccion(img,numerar_secciones=numerar_secciones,color_homogeneo=color_homogeneo)
    
    if st.session_state.get("seccion_compuesta",None) is not None:
        cargar_dataframe()
    
#st.session_state