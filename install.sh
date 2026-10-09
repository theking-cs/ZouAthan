#!/bin/bash

PLUGIN_NAME="ZouAthan"
PLUGIN_PATH="/usr/lib/enigma2/python/Plugins/Extensions/$PLUGIN_NAME"
REPO_URL="https://github.com/theking-cs/ZouAthan-"

echo "=========================================="
echo "  Instalando ZouAthan PRO para Enigma2..."
echo "=========================================="

# 1. Crear directorio del plugin si no existe
mkdir -p "$PLUGIN_PATH"

# 2. Descargar los archivos necesarios usando wget o curl
echo "[*] Descargando archivos desde GitHub..."
cd "$PLUGIN_PATH"

FILES=("plugin.py" "__init__.py" "plugin.png" "background.png" "athan.wav")

for file in "${FILES[@]}"; do
    echo "Descargando $file..."
    wget -q --no-check-certificate "$REPO_URL/main/$file" -O "$file" || curl -s -L "$REPO_URL/main/$file" -o "$file"
done

# 3. Reiniciar Enigma2
echo "[*] Instalación completada."
echo "[*] Reiniciando la interfaz de Enigma2..."
killall -9 enigma2

exit 0
