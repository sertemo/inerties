import streamlit as st
import secciones as sc
import graficar as gf
import traducciones as tr

def reset_todo(rerun_app:bool=True)->None:
    """Borra todas las secciones
    """
    if st.session_state.get("secciones",None) is not None:
        del st.session_state["secciones"]
    if st.session_state.get("seccion_compuesta",None) is not None:
        del st.session_state["seccion_compuesta"]
    if st.session_state.get("vent_x",None) is not None:
        del st.session_state["vent_y"]
        del st.session_state["numerar_secciones"]
        del st.session_state["color_homogeneo"]
        del st.session_state["vent_x"]
    if rerun_app:
        st.experimental_rerun()

def cargar_seccion_compuesta()->None:
    """Carga la lista de secciones independientes en la clase SeccionCompuesta y lo añade
    a la sesión
    """
    if len(st.session_state["secciones"]) > 0:
        st.session_state["seccion_compuesta"] = sc.SeccionCompuesta(st.session_state["secciones"])

def dibujar_seccion(img,color_homogeneo,numerar_secciones)->None:
    """Dibuja la sección compuesta que esté cargada en la sesion en "seccion_compuesta"
    """
    if st.session_state.get("seccion_compuesta",None) is not None:
        gf.GraficarSeccion().fit(seccion=st.session_state["seccion_compuesta"]).dibujar_seccion(img,color_homogeneo,numerar_secciones)
