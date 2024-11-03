import instaloader
from urllib.parse import urlparse
from loguru import logger

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
        # Извлекаем короткий код из URL пост
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
# print(download_instagram_post('https://www.instagram.com/reel/DBwxztSsXK9/?igsh=am9lODZvdmd6b2U='))
# print(download_instagram_post('https://www.instagram.com/reel/DBwOUQdxiu6/?igsh=MWhjMm45cTQzZDNzcg=='))
