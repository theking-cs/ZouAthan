#!/bin/sh
# Instalador para ZouAthan PRO - theking-cs

echo "********************************************************"
echo "* Instalando ZouAthan PRO                             *"
echo "********************************************************"

PLUGIN_NAME="ZouAthan"
PLUGIN_PATH="/usr/lib/enigma2/python/Plugins/Extensions/$PLUGIN_NAME"

# Limpiar carpetas previas
rm -rf $PLUGIN_PATH
rm -rf /tmp/ZouAthan.zip
rm -rf /tmp/ZouAthan-*

echo "> Descargando desde GitHub..."
wget --no-check-certificate https://github.com/theking-cs/ZouAthan/archive/refs/heads/main.zip -O /tmp/ZouAthan.zip

echo "> Extrayendo archivos..."
unzip -q /tmp/ZouAthan.zip -d /tmp/

# Mover la carpeta extraída de GitHub directamente a la ruta de Enigma2
echo "> Instalando en el sistema..."
mv /tmp/ZouAthan-main $PLUGIN_PATH

# Dar permisos
echo "> Configurando permisos..."
chmod -R 755 $PLUGIN_PATH

# Limpieza
rm -rf /tmp/ZouAthan.zip

echo "********************************************************"
echo "* INSTALACIÓN COMPLETADA - REINICIANDO ENIGMA2       *"
echo "********************************************************"
killall -9 enigma2

exit 0