import streamlit as st
import db
import time
import yagmail
import os
import traducciones as tr

st.set_page_config(
    page_title="Graphicator by STM",
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
    #"en" : 2
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
            label="Idioma",
            options=("es","fr"),
            index=LANG_MAPPING[st.session_state.get("idioma","fr")],
            label_visibility="hidden",
        )

    st.session_state["idioma"] = idioma

    st.title(tr.TRANS_MAPPING["Accueil_title"][idioma])
    st.subheader(tr.TRANS_MAPPING["Accueil_descripcion"][idioma])

    #Formulario para autenticarse
    if not st.session_state.get("usuario",""):
        with st.form("identificarse",clear_on_submit=True):
            st.write(tr.TRANS_MAPPING["formulario_autenticar"][idioma])
            user = st.text_input(tr.TRANS_MAPPING["formulario_usuario"][idioma])
            password = st.text_input(tr.TRANS_MAPPING["formulario_contraseña"][idioma],type="password")
            submit = st.form_submit_button(tr.TRANS_MAPPING["formulario_enviar"][idioma])

            if submit and user and password:
                #Verificamos que usuario exista en db
                usuario:db.Usuario = db.existe_usuario_en_db(user)
                if not usuario:
                    st.error(tr.TRANS_MAPPING["usuario_no_existe"][idioma])
                else:
                    if not db.verificar_contraseña(password,usuario.contraseña):
                        st.error(tr.TRANS_MAPPING["contraseña_incorrecta"][idioma])
                    else:
                        if not usuario.activo:
                            st.warning(tr.TRANS_MAPPING["cuenta_inactiva"][idioma])
                        else:
                            st.success("OK")
                            st.session_state["usuario"] = user
                            with st.spinner(tr.TRANS_MAPPING["cargar_datos"][idioma]):
                                time.sleep(2)
                                st.experimental_rerun()

        #Formulario para registrarse
        st.caption(tr.TRANS_MAPPING["pregunta_registrar"][idioma])
        with st.expander(tr.TRANS_MAPPING["frase_expander_registrar"][idioma]):
            with st.form("registrarse", clear_on_submit=True):
                reg_nombre_usuario = st.text_input(tr.TRANS_MAPPING["nombre_usuario"][idioma])
                reg_user = st.text_input(tr.TRANS_MAPPING["formulario_usuario"][idioma],help=tr.TRANS_MAPPING["ayuda_nombre_usuario"][idioma])
                reg_password = st.text_input(tr.TRANS_MAPPING["formulario_contraseña"][idioma],type="password")
                reg_submit = st.form_submit_button(tr.TRANS_MAPPING["boton_registrarse"][idioma])
                st.info(tr.TRANS_MAPPING["info_registrarse"][idioma])

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
                        st.error(tr.TRANS_MAPPING["usuario_ya_existe"][idioma])
                        st.stop()
                    #Mostrar mensaje de que registro correcto
                    usuario_db = {"nombre" : reg_nombre_usuario, "usuario" : reg_user, "contraseña" : hash_pass_o_error}
                    try:
                        db.insertar_usuario_en_db(db.UsuarioRegistro(**usuario_db))                        
                        st.success(tr.TRANS_MAPPING["usuario_ya_existe"][idioma])
                    except Exception as exc:
                        st.error(tr.TRANS_MAPPING["usuario_ya_existe"][idioma]+f"{exc}")
                    #Enviamos mail al admin para avisar del registro
                    mandar_email(db.UsuarioRegistro(**usuario_db))

    else:
        #Información al usuario autenticado
        st.header(
        tr.TRANS_MAPPING["header_utilizacion"][idioma])
        st.markdown(tr.TRANS_MAPPING["info_utilizacion"][idioma])
        
        st.caption("Done by STM w/💗 2023")
    #st.session_state