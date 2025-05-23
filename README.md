# Flatpak Manager

![Flatpak Manager](screenshot.png)

Un gestor de aplicaciones Flatpak con interfaz gráfica desarrollado en Python y PyQt6. Permite gestionar fácilmente tus aplicaciones Flatpak desde una interfaz amigable.

## Características

- 📦 Listar aplicaciones Flatpak instaladas
- 🔄 Buscar y aplicar actualizaciones
- 🧹 Limpiar caché de Flatpak
- 🔧 Reparar instalaciones de Flatpak
- 📊 Ver información del sistema
- 🎨 Soporte para temas claros y oscuros
- 📥 Exportar lista de aplicaciones instaladas
- 🖥️ Ejecución en segundo plano con bandeja del sistema

## Requisitos

- Python 3.8 o superior
- PyQt6
- Flatpak instalado en el sistema
- Sistema operativo Linux

## Instalación

### Método 1: Usando el script de instalación (Recomendado)

1. Clona el repositorio:
   ```bash
   git clone https://github.com/tuusuario/flatpak-manager.git
   cd flatpak-manager
   ```

2. Crea un entorno virtual (opcional pero recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Linux/macOS
   # o
   .\venv\Scripts\activate  # En Windows
   ```

3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Ejecuta el instalador:
   ```bash
   chmod +x install_flatpak_manager.sh
   sudo ./install_flatpak_manager.sh
   ```

### Método 2: Instalación manual

1. Instala las dependencias:
   ```bash
   sudo apt install python3 python3-pip python3-venv
   pip install PyQt6
   ```

2. Clona el repositorio:
   ```bash
   git clone https://github.com/tuusuario/flatpak-manager.git
   cd flatpak-manager
   ```

3. Ejecuta la aplicación:
   ```bash
   python flatpak_manager_improved.py
   ```

## Uso

1. **Interfaz Principal**
   - Usa las pestañas para navegar entre las diferentes secciones
   - La pestaña principal muestra información del sistema y acciones rápidas
   - La pestaña de configuración permite personalizar la apariencia

2. **Gestión de Aplicaciones**
   - Lista todas las aplicaciones Flatpak instaladas
   - Busca actualizaciones disponibles
   - Limpia la caché para liberar espacio
   - Repara instalaciones dañadas

3. **Personalización**
   - Cambia entre temas claro y oscuro
   - Ajusta el tamaño de la fuente
   - Configura preferencias de actualización

## Capturas de Pantalla

![Pantalla Principal](screenshots/main_window.png)
*Vista principal de la aplicación*

![Configuración](screenshots/settings.png)
*Panel de configuración*

## Estructura del Proyecto

```
flatpak-manager/
├── flatpak_manager_improved.py  # Código fuente principal
├── install_flatpak_manager.sh    # Script de instalación
├── requirements.txt              # Dependencias de Python
├── README.md                     # Este archivo
└── screenshots/                 # Capturas de pantalla
    ├── main_window.png
    └── settings.png
```

## Contribución

Las contribuciones son bienvenidas. Por favor, sigue estos pasos:

1. Haz un fork del proyecto
2. Crea una rama para tu característica (`git checkout -b feature/nueva-caracteristica`)
3. Haz commit de tus cambios (`git commit -am 'Añade nueva característica'`)
4. Haz push a la rama (`git push origin feature/nueva-caracteristica`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia GPL v3. Consulta el archivo [LICENSE](LICENSE) para más detalles.

## Créditos

- Desarrollado por VicCodeV y VicCodeM
- Iconos por [Font Awesome](https://fontawesome.com/)
- Basado en PyQt6

## Soporte

Si encuentras algún problema o tienes alguna sugerencia, por favor abre un [issue](https://github.com/tuusuario/flatpak-manager/issues) en el repositorio.

---

¡Gracias por usar Flatpak Manager! Si te gusta el proyecto, considera darle una ⭐ en GitHub.
