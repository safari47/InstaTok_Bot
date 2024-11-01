import instaloader
from urllib.parse import urlparse
from loguru import logger
import functools, time
import requests
import json
def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        val = func(*args, **kwargs)
        end = time.perf_counter()
        work_time = end - start
        print(f'Время выполнения {func.__name__}: {round(work_time, 4)} сек.')
        return val
    return wrapper


def get_shortcode(post_url):
    parsed_url = urlparse(post_url)
    path_parts = parsed_url.path.strip("/").split("/")

    if len(path_parts) > 2:
        short_code = path_parts[2]
    else:
        short_code = path_parts[1]

    return short_code


def download_instagram_post(post_url: str) -> dict[str]:
    """Функция для получения фото, видео контента из постов инстаграм"""
    upload_file = {}

    L = instaloader.Instaloader()

    try:
        # Извлекаем короткий код из URL поста

        short_code = get_shortcode(post_url)

        # Загружаем пост
        post = instaloader.Post.from_shortcode(L.context, short_code)

        if post.typename == "GraphSidecar":
            # Если пост карусельный, обрабатываем все элементы
            sidecar_nodes = post.get_sidecar_nodes()
            for index, sidecar_node in enumerate(sidecar_nodes, start=1):
                media_type = "Видео" if sidecar_node.is_video else "Изображение"
                media_url = (
                    sidecar_node.video_url
                    if sidecar_node.is_video
                    else sidecar_node.display_url
                )
                upload_file[f"{index}. {media_type}"] = media_url

        else:
            # Обрабатываем одиночный пост, если он не является каруселью
            media_type = "Видео" if post.is_video else "Изображение"
            media_url = post.video_url if post.is_video else post.url
            upload_file[f"1. {media_type}"] = media_url

    except instaloader.exceptions.InstaloaderException as e:
        logger.error(f"Ошибка Instaloader: {e}")
        logger.info(f"Ошибка возникла с URL: {post_url}")
        return f"Произошла неожиданная ошибка, обратитесь к администратору"
    except IndexError as e:
        logger.error(f"Ошибка: Некорректный формат URL - {e}")
        logger.info(f"Ошибка возникла с URL: {post_url}")
        return f"Ошибка: Некорректный формат URL"
    except Exception as e:
        logger.error(f"Произошла неожиданная ошибка: {e}")
        logger.info(f"Ошибка возникла с URL: {post_url}")
        return f"Произошла неожиданная ошибка, обратитесь к администратору"

    return upload_file


# Пример использования:
# download_instagram_post('https://www.instagram.com/adrenaline.sneaker/p/C6sqENGrHgr/')
# download_instagram_post('https://www.instagram.com/p/C6sqENGrHgr/?igsh=amdzdWxxNm8xdWo4')


def download_tiktok_video(post_url: str) -> str:
    url = "https://tiktok-video-no-watermark2.p.rapidapi.com/"

    # Убедитесь, что post_url действителен
    valid_url = post_url.split('?')[0]
    querystring = {"url": valid_url, "hd": "1"}

    headers = {
        "x-rapidapi-key": "068d6445bfmsha0b99aa25d14099p10e252jsn186ab3ad20ad",
        "x-rapidapi-host": "tiktok-video-no-watermark2.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()  # Raises an error for bad responses

        # Получаем JSON ответ
        response_data = response.json()

        # Извлекаем значение 'play' из 'data'
        play_url = response_data.get("data", {}).get("hdplay", None)

        if play_url:
            return play_url
        else:
            return "Play URL not found in response data."

    except requests.exceptions.RequestException as e:
        # Обработка исключений сетевого уровня
        print(f"An error occurred: {e}")
        return "Failed to download video."


