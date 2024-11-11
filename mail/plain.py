from email.mime.text import MIMEText
from smtplib import SMTP, SMTP_SSL

from structure.constants import EMAIL_ACCOUNT, EMAIL_SMTP_SERVER, EMAIL_USE_TLS


async def send_smtp(email: str, subject: str, body: str):
    msg = MIMEText(body, "html")
    msg["Subject"] = subject
    msg["From"] = EMAIL_ACCOUNT[0]
    msg["To"] = email

    SMTPClass = SMTP_SSL if EMAIL_USE_TLS else SMTP
    with SMTPClass(EMAIL_SMTP_SERVER[0], EMAIL_SMTP_SERVER[1]) as smtp:
        if EMAIL_ACCOUNT is not None:
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
):
    body = f"<p>You've received an SOS Mail from Team {team}!</p>"
    body += f"<p>Team Name: {team}</p>"
    body += f"<p>Dungeon: {dungeon_info}</p>"
    body += f"<p>Rescue Number: {code}</p>"
    if title:
        body += f"<p>Title: {title}</p>"
    if message:
        body += f"<p>Message: {message}</p>"
    await send_smtp(rescuer_email, "New SOS Mail", body)


async def send_aok(
    rescued_email: str,
    rescued_team: str,
    rescuer_team: str,
    title: str,
    message: str,
    dungeon_info: str,
    code: str,
):
    body = f"<p>You've received an A-OK Mail from Team {rescuer_team}!</p>"
    body += f"<p>Rescued Team: {rescued_team}</p>"
    body += f"<p>Rescuer: {rescuer_team}</p>"
    body += f"<p>Dungeon: {dungeon_info}</p>"
    body += f"<p>Rescue Number: {code}</p>"
    if title:
        body += f"<p>Title: {title}</p>"
    if message:
        body += f"<p>Message: {message}</p>"
    await send_smtp(rescued_email, "New A-OK Mail", body)


async def send_thank_you(rescuer_email: str, title: str, message: str):
    body = f"<p>You've received a Thank-You Mail!</p>"
    if title:
        body += f"<p>Title: {title}</p>"
    if message:
        body += f"<p>Message: {message}</p>"
    await send_smtp(rescuer_email, "New Thank-You Mail", body)


enabled = False
if EMAIL_ACCOUNT:
    enabled = True
