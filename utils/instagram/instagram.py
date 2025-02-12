import instaloader
from urllib.parse import urlparse
# from config.config import L


def get_shortcode(post_url):
    parsed_url = urlparse(post_url)
    path_parts = parsed_url.path.strip("/").split("/")

    if len(path_parts) > 2:
        short_code = path_parts[2]
    else:
        short_code = path_parts[1]

    return short_code


def download_instagram_post(post_url: str) -> dict[str, str]:
    """Функция для получения фото, видео контента из постов Instagram."""
    upload_file = {}

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

    return upload_file


# Пример использования:
# print(download_instagram_post('https://www.instagram.com/reel/DBwxztSsXK9/?igsh=am9lODZvdmd6b2U='))
# print(download_instagram_post('https://www.instagram.com/reel/DBwOUQdxiu6/?igsh=MWhjMm45cTQzZDNzcg=='))
# print(download_instagram_post('https://www.instagram.com/reel/DE2pnu8qdRb/?igsh=ZWpneHd1d3NhcTVi'))
# print(download_instagram_post('https://www.instagram.com/share/_gVY_y61P'))