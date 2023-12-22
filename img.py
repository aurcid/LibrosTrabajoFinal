import os
import requests
from mimetypes import guess_extension
from PIL import Image


def convertir_a_jpg(nombre_imagen):
    try:
        imagen = Image.open("images/" + nombre_imagen)

        nuevo_nombre = 'images/' + os.path.splitext(nombre_imagen)[0] + '.jpg'

        imagen.convert('RGB').save(nuevo_nombre, 'JPEG')

        imagen.close()

        if os.path.splitext(nombre_imagen)[1] != '.jpg':
            os.remove("images/" + nombre_imagen)

        print(f'La imagen fue convertida y guardada como: {nuevo_nombre}')

    except Exception as e:
        print(f'Ocurrió un error: {e}')


def download_save_images(url, dest_folder, file_name):
    try:
        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)

        respuesta = requests.get(url)

        if respuesta.status_code == 200:
            content_type = respuesta.headers.get('content-type')
            if 'image' in content_type:
                extension = guess_extension(content_type.split(';')[0])

                file_name_with_extension = f"{file_name}{extension}"
                base_directory = os.getcwd()

                ruta_completa = os.path.join(
                    base_directory, dest_folder, file_name_with_extension)

                with open(ruta_completa, 'wb') as archivo:
                    archivo.write(respuesta.content)

                convertir_a_jpg(file_name + extension)

                print(f'Imagen descargada y guardada en: {ruta_completa}')
            else:
                print(
                    f'El recurso no es una imagen. Tipo de contenido: {content_type}')
        else:
            print(
                f'Error al descargar la imagen. Código de estado: {respuesta.status_code}')

    except Exception as e:
        print(f'Ocurrió un error: {e}')
