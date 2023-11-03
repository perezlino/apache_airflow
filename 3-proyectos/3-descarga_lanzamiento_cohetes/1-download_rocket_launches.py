import json
from pathlib import Path

import airflow
import requests
import requests.exceptions as requests_exceptions
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

# Colocamos "schedule_interval" en "None". Esto significa que el DAG no se ejecutará automáticamente. 
# Por ahora, podemos activarlo manualmente desde la interfaz de usuario de Airflow.
dag = DAG(
    dag_id="listing_2_02",
    start_date=airflow.utils.dates.days_ago(14),
    schedule_interval=None,
)

# Esta tarea realiza la descarga de los datos json de la URL a nuestra máquina con el nombre de "launches.json"
download_launches = BashOperator(
    task_id="download_launches",
    bash_command="curl -o /tmp/launches.json -L 'https://ll.thespacedevs.com/2.2.0/launch/upcoming'",
    dag=dag,
)

def _get_pictures():
    # Creamos el subdirectorio "images"
    Path("/tmp/images").mkdir(parents=True, exist_ok=True)

    # Descargar todas las imágenes en launches.json
    with open("/tmp/launches.json") as f:
        launches = json.load(f)
        image_urls = [launch["image"] for launch in launches["results"]] # Se crea una lista 
        '''
        print(image_urls)

        ['https://spacelaunchnow-prod-east.nyc3.digitaloceanspaces.com/media/launcher_images/falcon_9_block__image_20210506060831.jpg', 
         'https://spacelaunchnow-prod-east.nyc3.digitaloceanspaces.com/media/launcher_images/rs1_image_20211102160004.jpg', 
         'https://spacelaunchnow-prod-east.nyc3.digitaloceanspaces.com/media/launcher_images/falcon_9_block__image_20210506060831.jpg', 
         'https://spacelaunchnow-prod-east.nyc3.digitaloceanspaces.com/media/launcher_images/falcon_heavy_image_20220129192819.jpeg', 
         'https://spacelaunchnow-prod-east.nyc3.digitaloceanspaces.com/media/launcher_images/falcon_9_block__image_20210506060831.jpg', 
         'https://spacelaunchnow-prod-east.nyc3.digitaloceanspaces.com/media/launcher_images/h-iia2520202_image_20190222031201.jpeg', 
         'https://spacelaunchnow-prod-east.nyc3.digitaloceanspaces.com/media/launch_images/falcon2520925_image_20221009234147.png', 
         'https://spacelaunchnow-prod-east.nyc3.digitaloceanspaces.com/media/launch_images/falcon2520925_image_20221215080414.png', 
         'https://spacelaunchnow-prod-east.nyc3.digitaloceanspaces.com/media/launch_images/falcon2520925_image_20221102115051.png', 
         'https://spacelaunchnow-prod-east.nyc3.digitaloceanspaces.com/media/launcher_images/terran_1_image_20220129191632.jpg']
        '''
        for image_url in image_urls:
            try:
                response = requests.get(image_url)
                image_filename = image_url.split("/")[-1]
                '''
                print(image_filename)

                falcon_9_block__image_20210506060831.jpg
                rs1_image_20211102160004.jpg
                falcon_9_block__image_20210506060831.jpg
                falcon_heavy_image_20220129192819.jpeg
                falcon_9_block__image_20210506060831.jpg
                h-iia2520202_image_20190222031201.jpeg
                falcon2520925_image_20221009234147.png
                falcon2520925_image_20221215080414.png
                falcon2520925_image_20221102115051.png
                terran_1_image_20220129191632.jpg
                '''
                target_file = f"/tmp/images/{image_filename}"

                # No entendi estas dos lineas
                # Sin embargo, si comento estas dos lineas no se descargan en el directorio las imagenes
                # Según el libro: 
                with open(target_file, "wb") as f: # ❺ Abre el handle del archivo de destino.
                    f.write(response.content)      # ❻ Escribe la imagen en la ruta del archivo.
                    
                print(f"Downloaded {image_url} to {target_file}")
                '''
                Downloaded https://spacelaunchnow-prod-east.nyc3.digitaloceanspaces.com/media/launcher_images/falcon_9_block__image_20210506060831.jpg to /tmp/images/falcon_9_block__image_20210506060831.jpg
                Downloaded https://spacelaunchnow-prod-east.nyc3.digitaloceanspaces.com/media/launcher_images/rs1_image_20211102160004.jpg to /tmp/images/rs1_image_20211102160004.jpg
                Downloaded https://spacelaunchnow-prod-east.nyc3.digitaloceanspaces.com/media/launcher_images/falcon_9_block__image_20210506060831.jpg to /tmp/images/falcon_9_block__image_20210506060831.jpg
                Downloaded https://spacelaunchnow-prod-east.nyc3.digitaloceanspaces.com/media/launcher_images/falcon_heavy_image_20220129192819.jpeg to /tmp/images/falcon_heavy_image_20220129192819.jpeg
                Downloaded https://spacelaunchnow-prod-east.nyc3.digitaloceanspaces.com/media/launcher_images/falcon_9_block__image_20210506060831.jpg to /tmp/images/falcon_9_block__image_20210506060831.jpg
                Downloaded https://spacelaunchnow-prod-east.nyc3.digitaloceanspaces.com/media/launcher_images/h-iia2520202_image_20190222031201.jpeg to /tmp/images/h-iia2520202_image_20190222031201.jpeg
                Downloaded https://spacelaunchnow-prod-east.nyc3.digitaloceanspaces.com/media/launch_images/falcon2520925_image_20221009234147.png to /tmp/images/falcon2520925_image_20221009234147.png
                Downloaded https://spacelaunchnow-prod-east.nyc3.digitaloceanspaces.com/media/launch_images/falcon2520925_image_20221215080414.png to /tmp/images/falcon2520925_image_20221215080414.png
                Downloaded https://spacelaunchnow-prod-east.nyc3.digitaloceanspaces.com/media/launch_images/falcon2520925_image_20221102115051.png to /tmp/images/falcon2520925_image_20221102115051.png
                Downloaded https://spacelaunchnow-prod-east.nyc3.digitaloceanspaces.com/media/launcher_images/terran_1_image_20220129191632.jpg to /tmp/images/terran_1_image_20220129191632.jpg
                '''
            except requests_exceptions.MissingSchema:
                print(f"{image_url} appears to be an invalid URL.")
            except requests_exceptions.ConnectionError:
                print(f"Could not connect to {image_url}.")


get_pictures = PythonOperator(
    task_id="get_pictures", 
    python_callable=_get_pictures, 
    dag=dag
)

notify = BashOperator(
    task_id="notify",
    bash_command='echo "There are now $(ls /tmp/images/ | wc -l) images."',
    dag=dag,
)

download_launches >> get_pictures >> notify