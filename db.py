from pymongo import MongoClient
import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

db_client = MongoClient(os.environ["DB_MONGO"])

database = db_client["INERTIES"]

def get_database()-> MongoClient:
    return database

def sacar_secciones_db()->list:
    """Carga en la sesion "secciones_db" todas las secciones
    guardadas en base de datos.
    OJO: función duplicada en "Definir section"

    Returns
    -------
    list
        _description_
    """
    secciones = list(database.SeccionesCompuestas.find().sort("nombre_seccion"))
    #Borramos el id
    for seccion in secciones:
        del seccion["_id"]
    st.session_state["secciones_db"] = secciones
    return secciones