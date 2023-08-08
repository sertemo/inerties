# Sections Composées - Propriétés mécaniques
Enlace a la app: [inerties](https://inerties.streamlit.app/)

- App creada para calcular los momentos de inercia y módulos resistentes de secciones compuestas.
Las secciones suelen ser rectangulares, cuadradas y circulares. Se pueden representar asimismo secciones de tipo C o U como combinación de secciones rectangulares macizas.
- App realizada gracias a Streamlit y OpenCV

## Actualizaciones
- 28/07/2023 - Añadida la posibilidad de guardar las secciones
- 28/07/2023 - Añadida posbilidad de recuperar y dibujar secciones guardadas
- 28/07/2023 - Añadida una cuadrícula cada 10 mm reales
- 30/07/2023 - Añadida personalización de la cuadrícula
- 08/08/2023 - Añadidos:
    - Posibilidad de rotación de las secciones
    - Cambiado el centro de referencia para la inserción al centro de la sección para todas las secciones
    - Añadidas dos opciones de visualización: Monocolor y numerar las secciones
    - Añadida la posibilidad de guardar y cargar las opciones de visualización a la vez que las secciones

## Ideas para implementar
- Averiguar por qué las secciones circulares no se dibujan..
- Crear perfiles de usuarios de tal manera que cada uno pueda guardar sus secciones en una base de datos personal. Contraseñas y nombres de usuarios asi como validaciones. Si no estás registrado no te deja guardar la sección.
- Crear página 'Accueil' en la que puedes solicitar registrarte: envio de mail a mi correo para confirmar. El usuario se da de alta pero la cuenta no está activa. Yo la tengo que activar manualmente cambiando 'activa' = `True` por ejemplo.