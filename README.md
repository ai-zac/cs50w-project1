` <header> `
  # Project-01 WEB50

  ## Web donde puedes hacer reseñas a algunos 5000 libros, "one book per person" o así es en ingles.
` </header> `


` <body> `
### La estructura de la web es la que usa Flask de toda la vida:
```
directory/
├── application.py      
├── requirements.txt 
├── static/     
│   └── css/ 
└── templates/  
```
---
Se agregan cosas como:
---
> Funcionalidad de login_required en el archivo (valgame la redundancia) login_required.py
----
> Un import.py, por si gustas insertar más libros (Hay un limite de libros, pero no creo que sea un problema)
---
> Y un archivo oculto llamado .env, para cargar automáticamente algunas variables para el inicio de Flask
---
### Notas: 
requirements.txt tiene algunos requerimientos que no se como llegaron a estar ahí (seguro serán dependencias de algun programa ahi mismo), y al intentar dar ```pip freeze``` siempre me devuelve la misma lista, asi que no se asusten al ver tantos programas en esa lista

Hiba a añadir un esquema visual sobre el diseño de la base de datos, pero como no es un diseño muy complejo, lo descarte, y pues de ahí, no hay mucho que explicar acerca de este repo/proyecto, seguro le agregue más actualizaciones en un futuro muy lejano.

` </body> `


` <footer> `

  Todos los derechos reservados a quien sea, copypaste 2022 por ai-zac.inc

  Project1 - Books | Fuente de CS50w Harvard
  
` </footer> `
