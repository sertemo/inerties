import streamlit as st
import secciones as sc
import graficar as gf

def reset_todo(rerun_app:bool=True)->None:
    """Borra todas las secciones
    """
    if st.session_state.get("secciones",None) is not None:
        del st.session_state["secciones"]
    if st.session_state.get("seccion_compuesta",None) is not None:
        del st.session_state["seccion_compuesta"]
    if rerun_app:
        st.experimental_rerun()

def cargar_seccion_compuesta()->None:
    """Carga la lista de secciones independientes en la clase SeccionCompuesta y lo añade
    a la sesión
    """
    if len(st.session_state["secciones"]) > 0:
        st.session_state["seccion_compuesta"] = sc.SeccionCompuesta(st.session_state["secciones"])

def dibujar_seccion(img)->None:
    """Dibuja la sección compuesta que esté cargada en la sesion en "seccion_compuesta"
    """
    if st.session_state.get("seccion_compuesta",None) is not None:
        gf.GraficarSeccion().fit(seccion=st.session_state["seccion_compuesta"]).dibujar_seccion(img)