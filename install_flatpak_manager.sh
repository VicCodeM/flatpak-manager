#!/bin/bash
# Script de instalación para Flatpak Manager

# Crear directorios necesarios
sudo mkdir -p /usr/local/bin/
sudo mkdir -p /usr/local/lib/flatpak-manager/
sudo mkdir -p /usr/share/applications/

# Copiar archivos
sudo cp flatpak_manager_improved.py /usr/local/lib/flatpak-manager/

# Crear archivo ejecutable
sudo bash -c 'cat > /usr/local/bin/flatpak-manager << EOL
#!/bin/bash
python3 /usr/local/lib/flatpak-manager/flatpak_manager_improved.py
EOL'

# Hacer ejecutable
sudo chmod +x /usr/local/bin/flatpak-manager

# Crear acceso directo
sudo bash -c 'cat > /usr/share/applications/flatpak-manager.desktop << EOL
[Desktop Entry]
Type=Application
Name=Flatpak Manager
Comment=Gestiona tus aplicaciones Flatpak
Exec=flatpak-manager
Icon=flatpak
Categories=System;Utility;
Terminal=false
EOL'

echo "Instalación completada. Puedes ejecutar el programa con: flatpak-manager"
