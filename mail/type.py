from enum import Enum


class ProfileType(Enum):
    UNKNOWN = 0
    EMAIL = 1
    DISCORD = 2

    @staticmethod
    def into_parts(combined_name: str):
        if not combined_name:
            return ProfileType.UNKNOWN, combined_name

        if combined_name.startswith("&discord&"):
            return ProfileType.DISCORD, combined_name[9:]
        elif "@" in combined_name:
            return ProfileType.EMAIL, combined_name
        else:
            return ProfileType.UNKNOWN, combined_name
