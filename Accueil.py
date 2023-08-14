import streamlit as st
import db
import time
import yagmail
import os
import traducciones as tr

st.set_page_config(
    page_title="Calculer Sections Multiples",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="auto",
)

#Constantes
GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
YAG = yagmail.SMTP("tejedor.moreno.dev@gmail.com",GOOGLE_API_KEY)
LANG_MAPPING = {
    "es" : 0,
    "fr" : 1,
    "en" : 2
}

#Funciones
def mandar_email(usuario:db.UsuarioRegistro)->None:
    """Función para enviar por email con yagmail un mail para avisar de que un usuario
    se ha registrado

    Parameters
    ----------
    email : str
        el email del receptor
    text : str
        El body del email
    """
    text = f""" Se ha registrado el siguiente usuario:\n
    nombre:{usuario.nombre}\n
    usuario: {usuario.usuario}\n
    fecha alta: {usuario.fecha_alta}\n

    Pincha aqui para ir a la base da datos : https://cloud.mongodb.com/
    """

    YAG.send(
    to="tejedor.moreno@gmail.com",
    subject=f"Dar de alta {usuario.usuario} en aplicación INERTIES",
    contents=text, 
)

if __name__ == '__main__':  

    with st.sidebar:
        idioma = st.radio(
            "Idioma",
            ("es","fr","en"),
            index=LANG_MAPPING[st.session_state.get("idioma","fr")]
        )

    st.session_state["idioma"] = idioma

    st.title(tr.TRANS_MAPPING["Accueil_title"].get(idioma,""))

    #Formulario para autenticarse
    if not st.session_state.get("usuario",""):
        with st.form("S'identifier"):
            st.write("Rentrez votre utilisateur et mot de passe pour continuer")
            user = st.text_input("Utilisateur")
            password = st.text_input("Mot de passe",type="password")
            submit = st.form_submit_button("Envoyer")

            if submit and user and password:
                #Verificamos que usuario exista en db
                usuario:db.Usuario = db.existe_usuario_en_db(user)
                if not usuario:
                    st.error("Cet utilisateur n'existe pas.")
                else:
                    if not db.verificar_contraseña(password,usuario.contraseña):
                        st.error("Le mot de pass n'est pas correcte.")
                    else:
                        if not usuario.activo:
                            st.warning("Le compte est inactif. Demandez à l'administrateur de l'activer.")
                        else:
                            st.success("OK")
                            st.session_state["usuario"] = user
                            with st.spinner("En train de charger vos données.."):
                                time.sleep(2)
                                st.experimental_rerun()

        #Formulario para registrarse
        st.caption("Pas enregistré(e) encore ? Remplissez le formulaire plus bas")
        with st.expander("S'inscrire dans la base de données pour pouvoir dessiner des sections"):
            with st.form("S'inscrire"):
                reg_nombre_usuario = st.text_input("Prénom et nom de l'utilisateur")
                reg_user = st.text_input("Utilisateur",help="L'utilisateur ne peut pas avoir d'espaces vides et devra comporter plus de 5 lettres")
                reg_password = st.text_input("Mot de passe",type="password")
                reg_submit = st.form_submit_button("S'inscrire")
                st.write("Quand vous enregistrez le compte votre utilisateur sera créé mais votre compte sera inactif.")

                if reg_submit:
                    #Verificar user y password válido
                    usuario_valido, error_usuario = db.validar_usuario(reg_user)
                    if not usuario_valido:
                        st.error(error_usuario)
                        st.stop()
                    contraseña_valida, hash_pass_o_error = db.validar_contraseña(reg_password)
                    if not contraseña_valida:
                        st.error(hash_pass_o_error)
                        st.stop()              
                    #Verificar que ese user no exista en base de datos
                    if db.existe_usuario_en_db(reg_user):
                        st.error("Cet utilisateur existe déjà.")
                        st.stop()
                    #Mostrar mensaje de que registro correcto
                    usuario_db = {"nombre" : reg_nombre_usuario, "usuario" : reg_user, "contraseña" : hash_pass_o_error}
                    try:
                        db.insertar_usuario_en_db(db.UsuarioRegistro(**usuario_db))                        
                        st.success("Enregistrement correcte. L'administrateur activera votre compte dans les plus brefs délais.")
                    except Exception as exc:
                        st.error(f"Une erreur s'est produite: {exc}")
                    #Enviamos mail al admin para avisar del registro
                    mandar_email(db.UsuarioRegistro(**usuario_db))

    else:
        #TODO: mostrar información de la app si es usuario ya está autenticado
        st.header("""
        Utilisation""")
        st.markdown(f"""
                1. Aller à 'Définir section'
                2. Lire les 'informations importantes'
                3. Dessiner une section simple ou composée
                4. Vous avez le droit d'enregistrer jusqu'à {db.NUM_SECCIONES} sections différentes
                5. Dans 'Sections enregistrées' vous pouvez dessiner et gérer les sections que vous avez enregistrés.""")
        
        st.caption("Done by STM w/💗 2023")

    #st.session_state