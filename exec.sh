#!/bin/bash
#para usarse ./exec.sh IP (id de narnaja papa q se va a hacer) (numero de azules)
#si le sale que no tiene permiso le da chmod 755

echo creando
IP=$1
id=$2
cantidadAZULES=$3


echo "Ip:$IP ID naranja:$id Cantidad de Azules:$cantidadAZULES"

python3 fastMain.py $id

counter=0
puerto=8888
puertoN=8888
until [ $counter -gt $cantidadAZULES ]
do
echo creo Nodo Azul numero: $counter
((counter++))
((puerto=puerto+counter))
gnome-terminal -- python3 FastmainAzul.py $ip $puerto $ip $puertoN

done
echo All done
