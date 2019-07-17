#!/bin/bash
#para usarse ./exec.sh IP  (numero de azules) (puerto de nodo naranja)
#si le sale que no tiene permiso le da chmod 755

echo creando
IP=$1
cantidadAZULES=$2
PuertoN=$3


echo "Ip:$IP  Cantidad de Azules:$cantidadAZULES Puerto Naranja: $PuertoN "

counter=1
puerto=7000
until [ $counter -gt $cantidadAZULES ]
do
echo creo Nodo Azul numero: $counter
((counter++))
((puerto++))
echo $puerto
gnome-terminal -- python3 FastmainAzul.py $IP $puerto $IP $puertoN

done
echo All done
