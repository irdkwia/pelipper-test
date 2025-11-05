import asyncio

from mail import discord_bot, plain
from mail.type import ProfileType
from structure.formatter import format_floor, format_rescue_code
from structure.models import BuddyList, Profile


class NotifHandler:
    @staticmethod
    def send_thankyou_notifications(db, prf, aok, thk):
        # Sending Thank-You
        rescuer_prf = db.get_elements(Profile, {"pid": aok.rescuerpid}, limit=1)
        if len(rescuer_prf) > 0:
            rescuer_prf = rescuer_prf[0]
            if rescuer_prf.flags & 0x80000:
                (ty, rescuer_identifier) = ProfileType.into_parts(rescuer_prf.email)
                if ty == ProfileType.DISCORD:  # Discord user name/ID
                    if discord_bot.enabled:
                        asyncio.run_coroutine_threadsafe(
                            discord_bot.send_thank_you(
                                rescuer_identifier,
                                thk.title,
                                thk.message,
                                prf.lang,
                            ),
                            discord_bot.bot.loop,
                        )
                elif ty == ProfileType.EMAIL:
                    if plain.enabled:
                        asyncio.run(
                            plain.send_thank_you(
                                rescuer_identifier,
                                thk.title,
                                thk.message,
                                prf.lang,
                            )
                        )

    @staticmethod
    def send_aok_notifications(db, prf, rq, aok):
        # Sending A-OK
        rescued_prf = db.get_elements(Profile, {"pid": rq.pid}, limit=1)
        if len(rescued_prf) > 0:
            rescuer_user_name = None
            (rescuer_ty, rescuer_identifier) = ProfileType.into_parts(prf.email)
            if rescuer_ty == ProfileType.DISCORD:
                rescuer_user_name = rescuer_identifier

            # Sending A-OK to user
            rescued_prf = rescued_prf[0]
            rescued_user_name = None
            (rescued_ty, rescued_identifier) = ProfileType.into_parts(rescued_prf.email)
            if rescued_ty == ProfileType.DISCORD:
                rescued_user_name = rescued_identifier

            # Sending A-OK to everyone
            if discord_bot.enabled and not rq.private:
                asyncio.run_coroutine_threadsafe(
                    discord_bot.send_aok_global(
                        rescued_user_name,
                        rescuer_user_name,
                        rq.team,
                        aok.team,
                        aok.title,
                        aok.message,
                        format_floor(db, rq.dungeon, rq.floor),
                        format_rescue_code(rq.rid),
                        prf.lang,
                    ),
                    discord_bot.bot.loop,
                )

            if rescued_prf.flags & 0x40000:
                if rescued_ty == ProfileType.DISCORD:
                    if discord_bot.enabled:
                        asyncio.run_coroutine_threadsafe(
                            discord_bot.send_aok(
                                rescued_identifier,
                                rescuer_user_name,
                                rq.team,
                                aok.team,
                                aok.title,
                                aok.message,
                                format_floor(db, rq.dungeon, rq.floor),
                                format_rescue_code(rq.rid),
                                prf.lang,
                            ),
                            discord_bot.bot.loop,
                        )
                elif rescued_ty == ProfileType.EMAIL:
                    if plain.enabled:
                        asyncio.run(
                            plain.send_aok(
                                rescued_identifier,
                                rq.team,
                                aok.team,
                                aok.title,
                                aok.message,
                                format_floor(db, rq.dungeon, rq.floor),
                                format_rescue_code(rq.rid),
                                prf.lang,
                            )
                        )

    @staticmethod
    def send_rescue_notifications(db, prf, rq):
        rescued_user_name = None
        (ty, rescued_identifier) = ProfileType.into_parts(prf.email)
        if ty == ProfileType.DISCORD:
            rescued_user_name = rescued_identifier
        if discord_bot.enabled and not rq.private:
            asyncio.run_coroutine_threadsafe(
                discord_bot.send_sos_global(
                    rescued_user_name,
                    rq.team,
                    rq.title,
                    rq.message,
                    format_floor(db, rq.dungeon, rq.floor),
                    format_rescue_code(rq.rid),
                    prf.lang,
                ),
                discord_bot.bot.loop,
            )
        ptr_include = {
            "flags": [
                0x20000,
                0x20000 | 0x40000,
                0x20000 | 0x80000,
                0x20000 | 0x40000 | 0x80000,
            ]
        }
        if rq.private:
            friends = db.get_elements(
                BuddyList,
                {"pid": prf.pid},
                None,
                None,
                None,
                [("pid", "buddy")],
            )
            ptr_include.update({"pid": [prf.pid] + [b.buddy for b in friends]})
        potential_rescuers = db.get_elements(Profile, include=ptr_include)
        for rescuer_prf in potential_rescuers:
            if rescuer_prf.pid == prf.pid:  # Skip yourself
                continue
            try:
                (ty, rescuer_identifier) = ProfileType.into_parts(rescuer_prf.email)
                if ty == ProfileType.DISCORD:  # Discord user name/ID
                    if discord_bot.enabled:
                        asyncio.run_coroutine_threadsafe(
                            discord_bot.send_sos(
                                rescued_user_name,
                                rescuer_identifier,
                                rq.team,
                                rq.title,
                                rq.message,
                                format_floor(db, rq.dungeon, rq.floor),
                                format_rescue_code(rq.rid),
                                prf.lang,
                            ),
                            discord_bot.bot.loop,
                        )
                elif ty == ProfileType.EMAIL:
                    if plain.enabled:
                        asyncio.run(
                            plain.send_sos(
                                rescuer_identifier,
                                rq.team,
                                rq.title,
                                rq.message,
                                format_floor(db, rq.dungeon, rq.floor),
                                format_rescue_code(rq.rid),
                                prf.lang,
                            )
                        )
            except Exception as e:
                print(f"Failed delivering SOS notification.\n{e}")
