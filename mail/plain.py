from email.mime.text import MIMEText
from smtplib import SMTP_SSL

from prettifier.prettify import make_pretty
from structure.constants import EMAIL_ACCOUNT, EMAIL_SMTP_SERVER


async def send_smtp(email: str, subject: str, body: str):
    msg = MIMEText(body, "html")
    msg["Subject"] = subject
    msg["From"] = EMAIL_ACCOUNT[0]
    msg["To"] = email
    with SMTP_SSL(EMAIL_SMTP_SERVER[0], EMAIL_SMTP_SERVER[1]) as smtp:
        smtp.login(EMAIL_ACCOUNT[0], EMAIL_ACCOUNT[1])
        smtp.sendmail(EMAIL_ACCOUNT[0], [email], msg.as_string())


async def send_signup_code(email: str, signup_code: str):
    body = (
        "<p>Welcome to the Pelipper notification service!</p>"
        f"<p>Your sign-up code is: {signup_code}</p>"
    )
    await send_smtp(email, "Welcome to Pelipper!", body)


async def send_sos(
    rescuer_email: str,
    team: str,
    title: str,
    message: str,
    dungeon_info: str,
    code: str,
    lang: int,
):
    body = f"<p>You've received an SOS Mail from Team {team}!</p>"
    body += f"<p>Team Name: {team}</p>"
    body += f"<p>Dungeon: {dungeon_info}</p>"
    body += f"<p>Rescue Number: {code}</p>"
    if title:
        body += f"<p>Title: {make_pretty(title, lang)}</p>"
    if message:
        body += f"<p>Message: {make_pretty(message, lang)}</p>"
    await send_smtp(rescuer_email, "New SOS Mail", body)


async def send_aok(
    rescued_email: str,
    rescued_team: str,
    rescuer_team: str,
    title: str,
    message: str,
    dungeon_info: str,
    code: str,
    lang: int,
):
    body = f"<p>You've received an A-OK Mail from Team {rescuer_team}!</p>"
    body += f"<p>Rescued Team: {rescued_team}</p>"
    body += f"<p>Rescuer: {rescuer_team}</p>"
    body += f"<p>Dungeon: {dungeon_info}</p>"
    body += f"<p>Rescue Number: {code}</p>"
    if title:
        body += f"<p>Title: {make_pretty(title, lang)}</p>"
    if message:
        body += f"<p>Message: {make_pretty(message, lang)}</p>"
    await send_smtp(rescued_email, "New A-OK Mail", body)


async def send_thank_you(rescuer_email: str, title: str, message: str, lang: int):
    body = f"<p>You've received a Thank-You Mail!</p>"
    if title:
        body += f"<p>Title: {make_pretty(title, lang)}</p>"
    if message:
        body += f"<p>Message: {make_pretty(message, lang)}</p>"
    await send_smtp(rescuer_email, "New Thank-You Mail", body)


enabled = False
if EMAIL_ACCOUNT:
    enabled = True
