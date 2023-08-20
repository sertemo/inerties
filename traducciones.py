import db

TRANS_MAPPING = {
    "Accueil_title" : {
        "fr" : "🧮 Graphicator",
        "es" : "🧮 Graphicator",
        "en" : ""
    },
    "Accueil_descripcion" : {
        "fr" : "Application pour dessiner des sections et calculer leurs propriétés mécaniques",
        "es" : "Aplicación para dibujar secciones y calcular sus propiedades mecánicas",
        "en" : ""
    },
    "page_title" : {
        "fr" : "Graphicator by STM",
        "es" : "Graphicator by STM",
        "en" : "Graphicator"
    },
    "registrarse_mensaje" : {
        "fr" : "Inscrivez vous en allant sur Accueil",
        "es" : "Régistrate en la sección Inicio",
        "en" : ""
    },
    "dataframe_geometria" : {
        "fr" : "Géométrie section",
        "es" : "Geometría de la sección",
        "en" : ""
    },
    "dataframe_emplazamiento" : {
        "fr" : "Emplacement (mm)",
        "es" : "Posición (mm)",
        "en" : ""
    },
    "boton_dibujar_Seccion" : {
        "fr" : "Dessiner section",
        "es" : "Dibujar sección",
        "en" : ""
    },
    "boton_dibujar_Seccion_ayuda" : {
        "fr" : "Récupère et dessine la section",
        "es" : "Recupera y dibuja la sección",
        "en" : ""
    },
    "boton_borrar_Seccion" : {
        "fr" : "Effacer section",
        "es" : "Borrar sección",
        "en" : ""
    },
    "boton_borrar_Seccion_ayuda" : {
        "fr" : "Efface la section pour toujours",
        "es" : "Borra la sección de manera irreversible",
        "en" : ""
    },
    "secciones_guardadas_titulo" : {
        "fr" : "Liste de sections enregistrées pour ",
        "es" : "Lista de secciones guardadas para ",
        "en" : ""
    },
    "formulario_autenticar" : {
        "fr" : "Rentrez votre utilisateur et mot de passe pour continuer",
        "es" : "Escribe tu nombre de usuario y contraseña para continuar",
        "en" : ""
    },
    "formulario_usuario" : {
        "fr" : "Utilisateur",
        "es" : "Usuario",
        "en" : ""
    },
    "formulario_contraseña" : {
        "fr" : "Mot de passe",
        "es" : "Contraseña",
        "en" : ""
    },
    "formulario_enviar" : {
        "fr" : "Envoyer",
        "es" : "Enviar",
        "en" : ""
    },
    "usuario_no_existe" : {
        "fr" : "Cet utilisateur n'existe pas.",
        "es" : "El usuario no existe.",
        "en" : ""
    },
    "contraseña_incorrecta" : {
        "fr" : "Le mot de pass n'est pas correcte.",
        "es" : "La contraseña es incorrecta.",
        "en" : ""
    },
    "cuenta_inactiva" : {
        "fr" : "Le compte est inactif. Demandez à l'administrateur de l'activer.",
        "es" : "La cuenta está inactiva. Pide al administrador activarla.",
        "en" : ""
    },
    "cargar_datos" : {
        "fr" : "En train de charger vos données..",
        "es" : "Cargando tus datos..",
        "en" : ""
    },
    "pregunta_registrar" : {
        "fr" : "Pas enregistré(e) encore ? Remplissez le formulaire plus bas",
        "es" : "Todavía no estás registrad@ ? Rellena el formulario más abajo",
        "en" : ""
    },
    "frase_expander_registrar" : {
        "fr" : "S'inscrire pour pouvoir dessiner des sections",
        "es" : "Registrarse para poder dibujar secciones",
        "en" : ""
    },
    "nombre_usuario" : {
        "fr" : "Prénom et nom de l'utilisateur",
        "es" : "Nombre y apellidos del usuario",
        "en" : ""
    },
    "ayuda_nombre_usuario" : {
        "fr" : "L'utilisateur ne peut pas avoir d'espaces vides et devra comporter plus de 5 lettres",
        "es" : "El nombre de usuario no puede tener espacios y deberá tener más de 5 caracteres",
        "en" : ""
    },
    "boton_registrarse" : {
        "fr" : "S'inscrire",
        "es" : "Registrarse",
        "en" : ""
    },
    "info_registrarse" : {
        "fr" : "Quand vous enregistrez le compte, votre utilisateur sera créé mais votre compte sera inactif. Un mail sera envoyé à l'administrateur.",
        "es" : "Al registrarte, tu cuenta estará inactiva. Un email será enviado al administrador para activarla.",
        "en" : ""
    },
    "usuario_ya_existe" : {
        "fr" : "Cet utilisateur existe déjà. Choisissez un autre.",
        "es" : "El usuario ya existe. Escoge otro nombre de usuario.",
        "en" : ""
    },
    "registro_correcto" : {
        "fr" : "Enregistrement correcte. L'administrateur activera votre compte dans les plus brefs délais.",
        "es" : "Registro correcto. El administrador activará tu cuenta próximamente.",
        "en" : ""
    },
    "registro_error" : {
        "fr" : "Une erreur s'est produite: ",
        "es" : "Se ha producido el siguiente error: ",
        "en" : ""
    },
    "header_utilizacion" : {
        "fr" : "Utilisation",
        "es" : "Utilización",
        "en" : ""
    },
    "info_utilizacion" : {
        "fr" : f"""
                1. Allez à 'Definir section'
                2. Lire les informations importatnes
                3. Dessiner une section simple ou composée
                4. Vous pouvez enregistrer jusqu'à {db.NUM_SECCIONES} sections différentes
                5. Dans 'Sections enregistrées' vous pouvez récupérer, dessiner et supprimer les sections enregistrées""",
        "es" : f"""
                1. Ir a 'Definir section'
                2. Leer las informaciones importantes
                3. Dibujar una sección simple o compuesta
                4. Puedes guardar hasta {db.NUM_SECCIONES} secciones diferentes
                5. En el apartado 'Sections enregistrées' puedes recuperar, dibujar y borrar las secciones guardadas""",
        "en" : ""
    },
  

}