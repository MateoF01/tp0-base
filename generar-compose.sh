#!/bin/bash
echo "Generando..."
echo "El archivo de salida: $1"
echo "Para la cantidad de clientes: $2"

python3 generador-compose.py "$1" $2
