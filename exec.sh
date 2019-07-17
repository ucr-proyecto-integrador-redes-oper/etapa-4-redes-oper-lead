#!/bin/bash
#para usarse ./exec.sh IP  (numero de azules) (puerto de nodo naranja)
#si le sale que no tiene permiso le da chmod 755

echo creando
IP=$1
cantidadAZULES=$2
PuertoN=$3
Puerto=$4

echo "Ip:$IP  Cantidad de Azules:$cantidadAZULES Puerto Naranja: $PuertoN Puerto Azul inicial: $Puerto"

counter=1

until [ $counter -gt $cantidadAZULES ]
do
echo creo Nodo Azul numero: $counter
((counter++))
((Puerto++))
echo $Puerto
gnome-terminal -- python3 FastmainAzul.py $IP $Puerto $IP $PuertoN

done
echo All done
