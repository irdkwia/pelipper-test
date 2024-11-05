from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP_SSL

from prettifier.prettify import make_pretty
from structure.constants import EMAIL_ACCOUNT, EMAIL_SMTP_SERVER


def render_plain(body):
    msg = []
    for c in body:
        title, content = c
        if title == "":
            msg.append(content)
        else:
            msg.append(f"{title}: {content}")
    return "\n".join(msg)


def render_html(body):
    msg = []
    head = True
    for c in body:
        title, content = c
        if title == "":
            if head:
                msg.append(f"<h1>{content}</h1>")
            else:
                msg.append(f"<p>{content}</p>")
            head = False
        else:
            msg.append(
                f'<p><span style="font-weight: bold;">{title}</span>: {content}</p>'
            )
    return "\n".join(msg)


DICT_PARTS = {
    "plain": render_plain,
    "html": render_html,
}


async def send_smtp(email: str, subject: str, body: list):
    msg = MIMEMultipart("alternative")
    for sub, renderer in DICT_PARTS.items():
        x = MIMEText(renderer(body), sub)
        msg.attach(x)
    msg["Subject"] = subject
    msg["From"] = EMAIL_ACCOUNT[0]
    msg["To"] = email
    with SMTP_SSL(EMAIL_SMTP_SERVER[0], EMAIL_SMTP_SERVER[1]) as smtp:
        smtp.login(EMAIL_ACCOUNT[0], EMAIL_ACCOUNT[1])
        smtp.sendmail(EMAIL_ACCOUNT[0], [email], msg.as_string())


async def send_signup_code(email: str, signup_code: str):
    body = [
        ("", "Welcome to the Pelipper notification service!"),
        ("", f"Your sign-up code is: {signup_code}"),
    ]
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
    body = [
        ("", f"You've received an SOS Mail from Team {team}!"),
        ("Team Name", team),
        ("Dungeon", dungeon_info),
        ("Rescue Number", code),
    ]
    if title:
        body.append(("Title", make_pretty(title, lang)))
    if message:
        body.append(("Message", make_pretty(message, lang)))
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
    body = [
        ("", f"You've received an A-OK Mail from Team {rescuer_team}!"),
        ("Rescued Team", rescued_team),
        ("Rescuer", rescuer_team),
        ("Dungeon", dungeon_info),
        ("Rescue Number", code),
    ]
    if title:
        body.append(("Title", make_pretty(title, lang)))
    if message:
        body.append(("Message", make_pretty(message, lang)))
    await send_smtp(rescued_email, "New A-OK Mail", body)


async def send_thank_you(rescuer_email: str, title: str, message: str, lang: int):
    body = [("", "You've received a Thank-You Mail!")]
    if title:
        body.append(("Title", make_pretty(title, lang)))
    if message:
        body.append(("Message", make_pretty(message, lang)))
    await send_smtp(rescuer_email, "New Thank-You Mail", body)


enabled = False
if EMAIL_ACCOUNT:
    enabled = True
