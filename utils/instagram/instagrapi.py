from aiograpi import Client
from instagrapi.exceptions import (
    BadPassword,
    ChallengeRequired,
    FeedbackRequired,
    LoginRequired,
    PleaseWaitFewMinutes,
    RecaptchaChallengeForm,
    ReloginAttemptExceeded,
    SelectContactPointRecoveryForm,
)


class Account:
    # Классовые атрибуты
    proxy_url = "http://JBNqnFXL:MxWfQpTj@45.147.244.65:63826"
    session_file = "insta_session.json"
    
    def __init__(self):
        self.client = None
    
    async def get_client(self):
        from config.config import settings
        self.client = Client()
        self.client.handle_exception = self.handle_exception
        self.client.set_proxy(self.proxy_url)
        self.client.load_settings(self.session_file)
        await self.client.login(settings.LOGIN, settings.PASSWORD)
        await self.client.get_timeline_feed()  # проверка сессии
        return self.client

    def handle_exception(self, e):
        if isinstance(e, BadPassword):
            self.client.logger.exception(e)
            self.client.set_proxy(self.next_proxy().href)
            if self.client.relogin_attempt > 0:
                self.freeze(str(e), days=7)
                raise ReloginAttemptExceeded(e)
            self.client.settings = self.rebuild_client_settings()
            return self.update_client_settings(self.client.get_settings())
        elif isinstance(e, LoginRequired):
            self.client.logger.exception(e)
            self.client.relogin()
            return self.update_client_settings(self.client.get_settings())
        elif isinstance(e, ChallengeRequired):
            api_path = self.client.last_json.get("challenge", {}).get("api_path")
            if api_path == "/challenge/":
                self.client.set_proxy(self.next_proxy().href)
                self.client.settings = self.rebuild_client_settings()
            else:
                try:
                    self.client.challenge_resolve(self.client.last_json)
                except ChallengeRequired as ex:
                    self.freeze("Manual Challenge Required", days=2)
                    raise ex
                except (
                    ChallengeRequired,
                    SelectContactPointRecoveryForm,
                    RecaptchaChallengeForm,
                ) as ex:
                    self.freeze(str(ex), days=4)
                    raise ex
                self.update_client_settings(self.client.get_settings())
            return True
        elif isinstance(e, FeedbackRequired):
            message = self.client.last_json["feedback_message"]
            if "This action was blocked. Please try again later" in message:
                self.freeze(message, hours=12)
            elif "We restrict certain activity to protect our community" in message:
                self.freeze(message, hours=12)
            elif "Your account has been temporarily blocked" in message:
                self.freeze(message)
        elif isinstance(e, PleaseWaitFewMinutes):
            self.freeze(str(e), hours=1)
            
        raise e

    async def download_instagram(self, post_url: str) -> dict[str, str]:
        upload_file = {}
        media_pk = await self.client.media_pk_from_url(post_url)
        media_info = await self.client.media_info(media_pk)

        # Проверяем тип медиа и формируем словарь с URL-ами
        if media_info.media_type == 8:  # Carousel
            for index, obj in enumerate(media_info.resources, start=1):
                media_type = "Видео" if obj.media_type == 2 else "Изображение"
                media_url = obj.video_url if media_type == "Видео" else obj.thumbnail_url
                upload_file[f"{index}. {media_type}"] = str(media_url)
        else:
            media_type = "Видео" if media_info.media_type == 2 else "Изображение"
            media_url = media_info.video_url if media_type == "Видео" else media_info.thumbnail_url
            upload_file[f"1. {media_type}"] = str(media_url)

        return upload_file

