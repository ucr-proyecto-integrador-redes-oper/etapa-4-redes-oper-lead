#!/bin/bash
#para usarse ./exec.sh IP (numero de azules) (puerto de nodo naranja) (PuertoAzul) (IPNaranja) (PuertoNaranja)
#si le sale que no tiene permiso le da chmod 755

echo creando
IPAzul=$1
cantidadAZULES=$2
PuertoAzul=$3
IPNaranja=$4
PuertoNaranja=$5

echo "Ip:$IPAzul  Cantidad de Azules:$cantidadAZULES Puerto Naranja: $PuertoNaranja Puerto Azul inicial: $PuertoAzul"

counter=1

until [ $counter -gt $cantidadAZULES ]
do
echo creo Nodo Azul numero: $counter
((counter++))
((PuertoAzul++))
echo $PuertoAzul
gnome-terminal -- python3 FastmainAzul.py $IPAzul $PuertoAzul $IPNaranja $PuertoNaranja

done
echo All done
