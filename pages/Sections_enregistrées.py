import streamlit as st
import numpy as np
import secciones as sc
import graficar as gf
import pandas as pd
import db
import aux_functions as af

st.set_page_config(
    page_title="Calculer Sections Multiples",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="auto",
)

## CONSTANTES ##
DATABASE = db.get_database()
SECTION_MAPPING = {
    "SeccionRectangularHueco" : sc.SeccionRectangularHueco,
    "SeccionRectangularMacizo" : sc.SeccionRectangularMacizo,
    "SeccionCircularHueco" : sc.SeccionCircularHueco,
    "SeccionCircularMacizo" : sc.SeccionCircularMacizo,
}

## FUNCIONES ##
def visualizar_secciones_db()->None:
    """Visualiza en forma de DataFrame las secciones compuestas
    asi como cada uno de sus secciones con sus caracteristicas.
    Tambien muestra 2 botones para gestionar la seccion
    """
    for idx,seccion in enumerate(st.session_state["secciones_db"],start=1):
        nombre_seccion = seccion["nombre_seccion"]
        st.header(f":violet[{idx} - {nombre_seccion}]")

        lista_tipo_secciones = []
        lista_ubicaciones = []
        lista_indices = []
        for indice, sec_simple in enumerate(seccion["secciones"],start=1):
            tipo_seccion = sec_simple["seccion"]["tipo_seccion"] + str(sec_simple["seccion"]["dimensiones"])            
            ubicacion = "x= " + str(sec_simple["ubicacion"][0]) + " , " + "y= " + str(sec_simple["ubicacion"][1])
            indices = f"Section {indice}"
            lista_tipo_secciones.append(tipo_seccion)
            lista_ubicaciones.append(ubicacion)
            lista_indices.append(indices)

        df = pd.DataFrame(
            {
                "Géométrie section" : lista_tipo_secciones,
                "Emplacement (mm)" : lista_ubicaciones,
                }
        ,
        index=lista_indices
        )
        st.dataframe(df,use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            st.button(
                "Dessiner section",
                help="Récupère et dessine la section",
                key="dibujar_"+nombre_seccion,
            )
        with col2:
            st.button(
                "Effacer section",
                help="Efface la section pour toujours",
                key="borrar_"+nombre_seccion,
            )

def comprobar_boton_pulsado()->list[str,str]:
    """Recorre la sesion state y comprueba si alguno de los botones
    de las opciones de cada seccion ha sido pulsado. Devuelve la accion a realizar
    y sobre qué sección compuesta

    Returns
    -------
    tuple[str,str]
        retorna "borrar" o "dibujar" junto con el nombre de la seccion
        para buscarla en la base de datos 
    """
    for valor in st.session_state:
        if valor.startswith("borrar") or valor.startswith("dibujar"):
            if st.session_state[valor]:
                return valor.split("_")
    return None, None

def recuperar_seccion(nombre_seccion:str)->list:
    """Itera sobre secciones_db y vuelve a montar las clases de la secciones.
    Posteriormente copia a la seccion "secciones" de la sesion para poder dibujarla

    Parameters
    ----------
    seccion : str
        _description_

    Returns
    -------
    list
        _description_
    """
    #Iteramos sobre secciones_db para encontrar la seccion que queremos dibujar
    lista_secciones = []
    for seccion_compuesta in st.session_state["secciones_db"]:
        if seccion_compuesta["nombre_seccion"] == nombre_seccion:
            for seccion_simple in seccion_compuesta["secciones"]:

                recu_sec = {
                    "seccion" : SECTION_MAPPING[seccion_simple["seccion"]["tipo_seccion"]](seccion_simple["seccion"]["dimensiones"]),
                    "ubicacion" : seccion_simple["ubicacion"],
                    "color" : seccion_simple["color"],
                }
                lista_secciones.append(recu_sec)
            
            #Cargamos a sesión las variables de visualización
            params = ["vent_x","vent_y","numerar_secciones","color_homogeneo"]
            for param in params:
                st.session_state[param] = seccion_compuesta[param]
    
    return lista_secciones

if __name__ == '__main__':
    st.title("Liste de sections enregistrées")

    if len(st.session_state.get("secciones_db",[])) > 0:
        visualizar_secciones_db()

    accion, seccion = comprobar_boton_pulsado()
    if accion == "borrar":
        DATABASE["SeccionesCompuestas"].delete_one({"nombre_seccion" : seccion})
        db.sacar_secciones_db()
        st.experimental_rerun()
    elif accion == "dibujar":
        af.reset_todo(rerun_app=False)
        st.session_state["secciones"] = recuperar_seccion(seccion)
        af.cargar_seccion_compuesta()
        with st.sidebar:
            st.success("Section chargée correctement")

    #st.session_state
