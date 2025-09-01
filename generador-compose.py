import sys

nombre_archivo = sys.argv[1]  
n_clientes = sys.argv[2]

#Construyo seccion de clientes

clientes = ''

for i in range(1, int(n_clientes) + 1):
    clientes += f"""  client{i}:
    container_name: client{i}
    image: client:latest
    entrypoint: /client
    environment:
      - CLI_ID={i}
      - CLI_DATASET=/data/agency.csv
      - CLI_CONFIG=/config.yaml
    volumes:
      - ./client/config.yaml:/config.yaml:ro
      - ./.data/agency-{i}.csv:/data/agency.csv:ro
    networks:
      - testing_net
    depends_on:
      - server

"""



#Defino archivo base
archivo_base = f"""name: tp0
services:
  server:
    container_name: server
    image: server:latest
    entrypoint: python3 /main.py
    environment:
      - PYTHONUNBUFFERED=1
      - EXPECTED_AGENCIES={n_clientes}
    volumes:
      - ./server/config.ini:/config.ini:ro
    networks:
      - testing_net

--clients--
networks:
  testing_net:
    ipam:
      driver: default
      config:
        - subnet: 172.25.125.0/24
"""



#Agrego los clientes al archivo base
archivo_final = archivo_base.replace('--clients--', clientes)


#Contruyo YAML
with open(nombre_archivo, "w") as f:
    f.write(archivo_final)