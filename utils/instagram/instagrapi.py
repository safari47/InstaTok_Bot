from config.config import cl


def download_instagram(post_url: str) -> dict[str, str]:
    upload_file = {}
    media_pk = cl.media_pk_from_url(post_url)
    media_info = cl.media_info(media_pk).dict()
    if media_info["media_type"] == 8:
        for index, obj in enumerate(media_info["resources"], start=1):
            media_type = "Видео" if obj["media_type"] == 2 else "Изображение"
            upload_file[f"{index}. {media_type}"] = str(obj["thumbnail_url"])
    else:
        media_type = "Видео" if media_info.get("media_type") == 2 else "Изображение"
        if media_type == "Видео":
            media_url = media_info.get("video_url")
        elif media_type == "Изображение":
            media_url = media_info.get("thumbnail_url")
        upload_file[f"1. {media_type}"] = str(media_url)
    return upload_file
