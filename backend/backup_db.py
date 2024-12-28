"""Модуль для генерации копии базы данных, расположенной в docker-контейнере
и извлечением файла в корень проекта."""

import os
import subprocess
from datetime import datetime
import yaml
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, '.env'))


def execute_command(command):
    """Функция для выполнения shell-команд с выводом результата."""
    try:
        print(f"Выполняется команда: {command}")
        result = subprocess.run(
            command, shell=True, check=True, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        print(result.stdout)
    except subprocess.CalledProcessError as er:
        print(f"Ошибка при выполнении команды: {er.stderr}")
        exit(1)


def get_container_name_from_compose(service_name, compose_file):
    """Функция получения имя контейнера из файла docker-compose.yml."""
    with open(compose_file, 'r') as file:
        compose_data = yaml.safe_load(file)

    try:
        container_name = compose_data['services'][service_name]['container_name']
        return container_name
    except KeyError:
        print(f"Ошибка: Сервис 'service_name' или параметр 'container_name' "
              f"не найден в 'compose_file'.")
        exit(1)


def create_and_extract_dump(container_name, db_name, db_user, dump_file):
    """Функция создания дампа базы данных в контейнере и извлечение его
    в корень проекта."""
    # создание дампа базы данных внутри контейнера
    create_dump_cmd = (
        f'sudo docker exec -it {container_name} '
        f'bash -c \"pg_dump -U {db_user} -F c -d {db_name} -f /{dump_file}"'
    )
    execute_command(create_dump_cmd)
    # копирование дампа из контейнера в корень проекта
    extract_dump_cmd = (
        f'sudo docker cp {container_name}:/{dump_file} '
        f'{BASE_DIR}/{dump_file}'
    )
    execute_command(extract_dump_cmd)
    # удаление временного дампа в контейнере
    clean_up_cmd = f'sudo docker exec -it {container_name} rm /{dump_file}'
    execute_command(clean_up_cmd)

    print(
        f"Файл дампа '{dump_file}' успешно извлечён в директорию: {BASE_DIR}"
    )


if __name__ == '__main__':
    COMPOSE_FILE = os.path.join(BASE_DIR,'docker-compose.yml')
    SERVICE_NAME = 'db'
    CONTAINER_NAME = get_container_name_from_compose(SERVICE_NAME,
                                                     COMPOSE_FILE)
    DB_NAME = os.getenv('POSTGRES_DB')
    DB_USER = os.getenv('POSTGRES_USER')
    # проверка наличия обязательных параметров
    if not all([CONTAINER_NAME, DB_NAME, DB_USER]):
        print(
            "Ошибка: Убедитесь, что DB_NAME b DB_USER указаны в файле '.env',"
            " а CONTAINER_NAME извлечён из 'docker-compose.yml'."
        )
        exit(1)
    # генерация имени файла дампа
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    DUMP_FILE = f'backup_{timestamp}.dump'
    # создание и извлечение дампа
    create_and_extract_dump(CONTAINER_NAME, DB_NAME, DB_USER, DUMP_FILE)