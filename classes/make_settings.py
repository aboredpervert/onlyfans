import copy
import uuid as uuid
from pathlib import Path
from typing import Any, Literal, Tuple, get_args

from yarl import URL

site_name_literals = Literal["OnlyFans", "Fansly", "StarsAVN"]
site_names: Tuple[site_name_literals, ...] = get_args(site_name_literals)

current_version = None


def fix(config: dict[str, Any] = {}):
    global current_version
    if config:
        info = config.get("info", {})
        if not info:
            print(
                "If you're not using >= v7 release, please download said release so the script can properly update your config. \nIf you're using >= v7 release or you don't care about your current config settings, press enter to continue. If script crashes, delete config."
            )
            input()
        current_version = info["version"]
    return config


class SiteSettings:
    def __init__(self, option: dict[str, Any] = {}):
        option = self.update_site_settings(option)

        class jobs:
            def __init__(self, option: dict[str, Any] = {}) -> None:
                self.scrape = scrape(option.get("scrape", {}))
                self.metadata = metadata(option.get("metadata", {}))

        class scrape:
            def __init__(self, option: dict[str, bool] = {}) -> None:
                self.subscriptions = option.get("subscriptions", True)
                self.messages = option.get("messages", True)
                self.paid_content = option.get("paid_content", True)

        class browser:
            def __init__(self, option: dict[str, bool] = {}) -> None:
                self.auth = option.get("auth", False)

        class metadata:
            def __init__(self, option: dict[str, bool] = {}) -> None:
                self.posts = option.get("posts", True)
                self.comments = option.get("comments", True)

        self.auto_profile_choice: list[int | str] | int | str | bool = option.get(
            "auto_profile_choice", ["default"]
        )
        self.auto_model_choice: list[int | str] | int | str | bool = option.get(
            "auto_model_choice", False
        )
        self.auto_api_choice: list[int | str] | int | str | bool = option.get(
            "auto_api_choice", True
        )
        self.auto_media_choice: list[int | str] | int | str | bool = option.get(
            "auto_media_choice", "0"
        )
        self.browser = browser(option.get("browser", {}))
        self.jobs = jobs(option.get("jobs", {}))
        self.download_directories = [
            Path(directory)
            for directory in option.get("download_directories", [".sites"])
        ]
        self.file_directory_format = Path(
            option.get(
                "file_directory_format",
                "{site_name}/{model_username}/{api_type}/{value}/{media_type}",
            )
        )
        self.filename_format = Path(option.get("filename_format", "{model_username}-{date}-{media_id}.{ext}"))
        self.metadata_directories = [
            Path(directory)
            for directory in option.get("metadata_directories", [".sites"])
        ]
        self.metadata_directory_format = Path(
            option.get(
                "metadata_directory_format",
                "{site_name}/{model_username}/Metadata",
            )
        )
        self.delete_legacy_metadata = option.get("delete_legacy_metadata", False)
        self.text_length = option.get("text_length", 255)
        self.video_quality = option.get("video_quality", "source")
        self.overwrite_files = option.get("overwrite_files", False)
        self.date_format = option.get("date_format", "%Y-%m-%d")
        self.ignored_keywords = option.get("ignored_keywords", [])
        self.ignore_type = option.get("ignore_type", "")
        self.blacklists = option.get("blacklists", [])
        self.webhook = option.get("webhook", True)
        self.timed_allow = option.get('timed_allow', [])

    def update_site_settings(self, options: dict[str, Any]):
        new_options = copy.copy(options)
        for key, value in options.items():
            match key:
                case "auto_scrape_names":
                    new_options["auto_model_choice"] = value
                case "auto_scrape_apis":
                    new_options["auto_api_choice"] = value
                case "file_directory_format":
                    new_options["file_directory_format"] = value.replace(
                        "{username}", "{model_username}"
                    )
                case "filename_format":
                    new_options["filename_format"] = value.replace(
                        "{username}", "{model_username}"
                    )
                case "metadata_directory_format":
                    new_options["metadata_directory_format"] = value.replace(
                        "{username}", "{model_username}"
                    )
                case "blacklist_name":
                    new_options["blacklists"] = [value]
                case "jobs":
                    if not value.get("scrape"):
                        new_value: dict[str, Any] = {}
                        new_value["scrape"] = {}
                        new_value["scrape"]["subscriptions"] = value.get(
                            "scrape_names", True
                        )
                        new_value["scrape"]["paid_content"] = value.get(
                            "scrape_paid_content", True
                        )
                        new_options["jobs"] = new_value
                case _:
                    pass
        return new_options


class Settings(object):
    def __init__(
        self,
        auto_site_choice: str = "onlyfans",
        profile_directories: list[str] = [".profiles"],
        export_type: str = "json",
        max_threads: int = -1,
        min_drive_space: int = 0,
        helpers: dict[str, bool] = {},
        webhooks: dict[str, Any] = {},
        exit_on_completion: bool = True,
        infinite_loop: bool = True,
        loop_timeout: int = 0,
        dynamic_rules_link: str = "https://raw.githubusercontent.com/DATAHOARDERS/dynamic-rules/main/onlyfans.json",
        proxies: list[str] = [],
        cert: str = "",
        random_string: str = "",
    ):
        class webhooks_settings:
            def __init__(self, option: dict[str, Any] = {}) -> None:
                class webhook_template:
                    def __init__(self, option: dict[str, Any] = {}) -> None:
                        self.webhooks = option.get("webhooks", [])
                        self.status = option.get("status", None)
                        self.hide_sensitive_info = option.get(
                            "hide_sensitive_info", True
                        )
                        print

                class auth_webhook:
                    def __init__(self, option: dict[str, Any] = {}) -> None:
                        self.succeeded = webhook_template(option.get("succeeded", {}))
                        self.failed = webhook_template(option.get("failed", {}))

                    def get_webhook(self, name: Literal["succeeded", "failed"]):
                        if name == "succeeded":
                            return self.succeeded
                        else:
                            return self.failed

                class download_webhook:
                    def __init__(self, option: dict[str, Any] = {}) -> None:
                        self.succeeded = webhook_template(option.get("succeeded", {}))
                        self.failed = webhook_template(option.get("failed", {}))

                    def get_webhook(self, name: Literal["succeeded", "failed"]):
                        if name == "succeeded":
                            return self.succeeded
                        else:
                            return self.failed

                self.global_webhooks = option.get("global_webhooks", [])
                self.global_status = option.get("global_status", True)
                self.auth_webhook = auth_webhook(option.get("auth_webhook", {}))
                self.download_webhook = download_webhook(
                    option.get("download_webhook", {})
                )

        class helpers_settings:
            def __init__(self, option: dict[str, bool] = {}) -> None:
                self.renamer = option.get("renamer", False)
                self.reformat_media = option.get("reformat_media", False)
                self.downloader = option.get("downloader", True)
                self.delete_empty_directories = option.get(
                    "delete_empty_directories", False
                )

        self.auto_site_choice = auto_site_choice
        self.export_type = export_type
        self.profile_directories = [Path(x) for x in profile_directories]
        self.max_threads = max_threads
        self.min_drive_space = min_drive_space
        self.helpers = helpers_settings(helpers)
        self.webhooks = webhooks_settings(webhooks)
        self.exit_on_completion = exit_on_completion
        self.infinite_loop = infinite_loop
        self.loop_timeout = loop_timeout
        dynamic_rules_link_ = URL(dynamic_rules_link)
        self.dynamic_rules_link = str(dynamic_rules_link_)
        self.proxies = proxies
        self.cert = cert
        self.random_string = random_string if random_string else uuid.uuid1().hex


class Config(object):
    def __init__(
        self,
        info: dict[str, Any] = {},
        settings: dict[str, Any] = {},
        supported: dict[str, Any] = {},
    ):
        class Info(object):
            def __init__(self) -> None:
                self.version = 8.0

        class Supported(object):
            def __init__(
                self,
                onlyfans: dict[str, Any] = {},
                fansly: dict[str, Any] = {},
                patreon: dict[str, Any] = {},
                starsavn: dict[str, Any] = {},
            ):
                self.onlyfans = self.OnlyFans(onlyfans)
                self.fansly = self.Fansly(fansly)
                self.starsavn = self.StarsAvn(starsavn)

            class OnlyFans:
                def __init__(self, module: dict[str, Any]):
                    self.settings = SiteSettings(module.get("settings", {}))

            class Fansly:
                def __init__(self, module: dict[str, Any]):
                    self.settings = SiteSettings(module.get("settings", {}))

            class StarsAvn:
                def __init__(self, module: dict[str, Any]):
                    self.settings = SiteSettings(module.get("settings", {}))

            def get_settings(self, site_name: site_name_literals):
                if site_name == "OnlyFans":
                    return self.onlyfans.settings
                elif site_name == "Fansly":
                    return self.fansly.settings
                else:
                    return self.starsavn.settings

        self.info = Info()
        self.settings = Settings(**settings)
        self.supported = Supported(**supported)

    def export(self):
        base = copy.deepcopy(self)
        base.settings.__dict__["profile_directories"] = [
            str(x) for x in base.settings.profile_directories
        ]
        for name in site_names:
            SS = base.supported.get_settings(site_name=name)
            for key, value in SS.__dict__.items():
                match key:
                    case "profile_directories" | "download_directories" | "metadata_directories":
                        items: list[Path] = value
                        new_list = [x.as_posix() for x in items]
                        SS.__dict__[key] = new_list
                    case "file_directory_format" | "filename_format" | "metadata_directory_format":
                        value_: Path = value
                        final_path = value_.as_posix()
                        SS.__dict__[key] = final_path
                    case _:
                        pass
        return base
