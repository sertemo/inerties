from pymongo import MongoClient
import os
from dotenv import load_dotenv
import streamlit as st
from pydantic import BaseModel, Field
from datetime import datetime
import pytz
from bson import ObjectId
from passlib.context import CryptContext #Para hashear passwords. Ojo: no es posible desencriptar con passlib
from typing import Optional, Union, Any

load_dotenv()

#Constantes
db_client = MongoClient(os.environ["DB_MONGO"])
NUM_SECCIONES = 5
database = db_client["INERTIES"]
hashear_password = CryptContext(schemes=["bcrypt"], deprecated= "auto") 

#Funciones
def get_database()-> MongoClient:
    return database

def format_datetime():
    return datetime.strftime(datetime.now(tz=pytz.timezone('Europe/Madrid')),format="%d-%m-%Y %H:%M:%S")

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")
    
    @classmethod #método agregado de GPT-4 para solucionar un problema a la hora de desplegar el script en Streamlit
    def __get_pydantic_core_schema__(cls, handler: Any) -> Any:
        return {"type": "string"}

class MongoBaseModel(BaseModel):
    id: PyObjectId = Field(default_factory = PyObjectId, alias="_id")

    class Config:
        json_encoders = {ObjectId : str} #Esto se usa para serializar el json

class UsuarioRegistro(MongoBaseModel):
    nombre:Optional[str]
    usuario:str
    contraseña:str
    fecha_alta: datetime = Field(default_factory=format_datetime)
    secciones_restantes: int = NUM_SECCIONES
    activo:bool = False

class Usuario(MongoBaseModel):
    usuario:str
    contraseña:str
    secciones_restantes:int
    activo:bool

def sacar_secciones_db(usuario:str)->list:
    """Carga en la sesion "secciones_db" todas las secciones
    guardadas en base de datos para un determinado usuario
    OJO: función duplicada en "Definir section"

    Returns
    -------
    list
        _description_
    """
    #secciones = list(database.SeccionesCompuestas.find().sort("nombre_seccion")) Código original

    secciones = list(database[usuario].find().sort("nombre_seccion"))

    #Borramos el id
    for seccion in secciones:
        del seccion["_id"]
    st.session_state["secciones_db"] = secciones
    return secciones

def insertar_usuario_en_db(usuario:UsuarioRegistro)->bool:
    try:
        database["usuarios"].insert_one(usuario.dict(by_alias=True))
        return True, ""
    except Exception as exc:
        return False, f"Se ha producido el siguiente error: {exc}"

def validar_contraseña(contraseña:str)->tuple[bool,str]:
    """Verificar que la contraseña cumpla ciertos criterios
    como >5 char para el registro
    Devuelve si la contraseña es válida y si lo es devuelve la contraseña hasheada,
    sino devuelve False y un mensaje de error
    """
    if len(contraseña) < 5:
        return False, "Le mot de pass doit avoir au moins 5 lettres."
    
    return True, hashear_password.hash(contraseña)

def validar_usuario(usuario:str)->tuple[bool,str]:
    if not usuario:
        return False, "L'utilisateur ne peut pas être vide."
    splitear = usuario.encode("utf-8").split()
    if len(splitear[0]) < 5:
        return False, "L'utilisateur doit avoir au moins 5 lettres"
    return True, ""

def existe_usuario_en_db(usuario:str)->Union[dict,bool]:
    if user:= database["usuarios"].find_one({"usuario": usuario}):
        return Usuario(**user)
    return False

def verificar_contraseña(contraseña:str,hash_pass:str)->bool:
    return hashear_password.verify(contraseña,hash_pass)

def _devolver_secciones_restantes(usuario:str)->int:
    usuario_db: Usuario = existe_usuario_en_db(usuario)
    return usuario_db.secciones_restantes

def reducir_secciones_restantes(usuario:str):
    query = {"usuario" : usuario}
    nuevos_valores = {"$inc" : {"secciones_restantes" : -1}}
    database["usuarios"].update_one(query,nuevos_valores)

def aumentar_secciones_restantes(usuario:str):
    query = {"usuario" : usuario}
    nuevos_valores = {"$inc" : {"secciones_restantes" : 1}}
    database["usuarios"].update_one(query,nuevos_valores)

def verificar_secciones_restantes(usuario:str)->bool:
    if seccion := _devolver_secciones_restantes(usuario) > 0:
        return True
    return False