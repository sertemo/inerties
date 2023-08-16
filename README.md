# Graphicator
## Sections Composées - Propriétés mécaniques
Enlace a la app: [Graphicator](https://graphicator.streamlit.app/)

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
-12/08/2023 - Creado sistema sencillo de registro y autenticación y bases de datos para que cada usuario pueda guardar sus propias secciones. Se ha puesto un límite de 5 secciones máximas para guardar de momento. Al registrarse el usuario está inactivo, se envía un mail al administrador que deberá activar manualmente al usuario para que pueda usar la aplicación.
- 14/08/2023 - Posibilidad de cambiar idioma de los textos

## Ideas para implementar
- Mejorar el código para el cálculo de Wx e Wy
- Terminar traducciones
