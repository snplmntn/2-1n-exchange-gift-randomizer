#!/usr/bin/env python3
"""Randomly assign gift givers to receivers and send email notifications."""

from __future__ import annotations

import argparse
import csv
import os
import random
from pathlib import Path
from dataclasses import dataclass

from dotenv import load_dotenv
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

load_dotenv()


@dataclass
class Participant:
    section: str
    email: str
    name: str
    wish1: str
    wish1_desc: str
    wish2: str
    wish2_desc: str
    wish3: str
    wish3_desc: str


def load_participants(csv_path: Path) -> list[Participant]:
    participants = []
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            def get(col: str) -> str:
                for key in row:
                    if key.strip() == col.strip():
                        return (row[key] or "").strip()
                return ""

            participants.append(Participant(
                section=get("Enter your Section"),
                email=get("Username"),
                name=get("Enter your Name (FN, MI, LN)"),
                wish1=get("What is your wish #1? (Priority Wish)"),
                wish1_desc=get("Describe your wish #1! (Priority Wish)"),
                wish2=get("What is your wish #2?"),
                wish2_desc=get("Describe your wish #2!"),
                wish3=get("What is your wish #3?"),
                wish3_desc=get("Describe your wish #3!"),
            ))
    return participants


def random_derangement(participants: list[Participant]) -> list[tuple[Participant, Participant]]:
    """Generate a random derangement where no one is assigned to themselves."""
    n = len(participants)
    if n < 2:
        raise ValueError("Need at least 2 participants for gift exchange")

    indices = list(range(n))
    for _ in range(1000):
        shuffled = indices[:]
        random.shuffle(shuffled)
        if all(i != shuffled[i] for i in range(n)):
            return [(participants[i], participants[shuffled[i]]) for i in range(n)]

    raise RuntimeError("Failed to generate derangement after 1000 attempts")


def build_email_body(gifter: Participant, receiver: Participant) -> str:
    body = f"""Ho Ho Ho! Christmas came a little early because you're about to give someone a present!

Hello {gifter.name}! You've been tasked to gift {receiver.name}.

The price range is around ₱50, but it's totally up to you if you want to go a bit over.

Here are some things {receiver.name} would love to receive:

{receiver.wish1}
{receiver.wish1_desc}

{receiver.wish2}
{receiver.wish2_desc}

{receiver.wish3}
{receiver.wish3_desc}

Remember to keep your match a secret until the exchange. The wishlist is just a guide - have fun with it!

Happy gifting from your 2-1N family!

With love,
BSCS 2-1N Gift Exchange
"""
    return body


def build_email_html(gifter: Participant, receiver: Participant) -> str:
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <title>Your Secret Santa Match</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #2d3748;
            background-color: #f7fafc;
            -webkit-font-smoothing: antialiased;
        }}
        
        .wrapper {{
            width: 100%;
            background: linear-gradient(135deg, #165B33 0%, #BB2528 50%, #146B3A 100%);
            padding: 40px 20px;
        }}
        
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background: #ffffff;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
        }}
        
        .header {{
            background: linear-gradient(135deg, #146B3A 0%, #165B33 100%);
            padding: 48px 32px;
            text-align: center;
            position: relative;
        }}
        
        .santa-emoji {{
            font-size: 64px;
            line-height: 1;
            margin-bottom: 16px;
        }}
        
        .title {{
            color: #000000;
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 8px;
            text-shadow: 2px 2px 4px rgba(255, 255, 255, 0.3);
        }}
        
        .subtitle {{
            color: #000000;
            font-size: 16px;
            font-weight: 400;
        }}
        
        .content {{
            padding: 40px 32px;
        }}
        
        .greeting {{
            font-size: 18px;
            color: #2d3748;
            margin-bottom: 28px;
            line-height: 1.7;
        }}
        
        .golden-ticket {{
            background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
            border: 3px solid #DAA520;
            border-radius: 12px;
            padding: 24px;
            margin: 24px 0;
            text-align: center;
            box-shadow: 0 8px 16px rgba(255, 215, 0, 0.5);
        }}
        
        .golden-ticket-label {{
            display: inline-block;
            background: #000000;
            color: #FFD700;
            font-size: 11px;
            font-weight: 700;
            padding: 6px 12px;
            border-radius: 6px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 12px;
        }}
        
        .golden-ticket-name {{
            font-size: 19px;
            font-weight: 700;
            color: #000000;
            line-height: 1.3;
        }}
        
        .budget-text {{
            font-size: 16px;
            color: #4a5568;
            margin: 24px 0;
            line-height: 1.7;
        }}
        
        .section-header {{
            font-size: 18px;
            font-weight: 700;
            color: #146B3A;
            margin: 32px 0 20px;
        }}
        
        .wishlist {{
            margin: 24px 0;
        }}
        
        .wish {{
            background: #ffffff;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 16px;
            border: 2px solid #e2e8f0;
        }}
        
        .wish.priority {{
            background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
            border: 3px solid #DAA520;
        }}
        
        .wish-badge {{
            display: inline-block;
            background: #000000;
            color: #FFD700;
            font-size: 11px;
            font-weight: 700;
            padding: 6px 12px;
            border-radius: 6px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 12px;
            border: 2px solid #FFD700;
        }}
        
        .wish-badge.secondary {{
            background: #146B3A;
            color: #ffffff;
            border: none;
        }}
        
        .wish-title {{
            font-size: 19px;
            font-weight: 700;
            color: #000000;
            margin-bottom: 8px;
        }}
        
        .wish-desc {{
            font-size: 15px;
            color: #000000;
            line-height: 1.6;
        }}
        
        .footer {{
            background: linear-gradient(135deg, #146B3A 0%, #0F5132 100%);
            padding: 40px 32px;
            text-align: center;
        }}
        
        .footer-message {{
            font-size: 20px;
            font-weight: 600;
            color: #000000;
            margin-bottom: 8px;
        }}
        
        .footer-family {{
            font-size: 17px;
            font-weight: 600;
            color: #000000;
            margin-top: 8px;
        }}
        
        @media only screen and (max-width: 600px) {{
            .wrapper {{
                padding: 20px 10px;
            }}
            
            .container {{
                border-radius: 12px;
            }}
            
            .header {{
                padding: 32px 20px;
            }}
            
            .santa-emoji {{
                font-size: 48px;
            }}
            
            .title {{
                font-size: 24px;
            }}
            
            .subtitle {{
                font-size: 14px;
            }}
            
            .content {{
                padding: 28px 20px;
            }}
            
            .greeting {{
                font-size: 16px;
            }}
            
            .reveal-box {{
                padding: 24px 16px;
            }}
            
            .reveal-name {{
                font-size: 26px;
            }}
            
            .budget-text {{
                font-size: 15px;
            }}
            
            .wish {{
                padding: 20px;
            }}
            
            .footer {{
                padding: 32px 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="wrapper">
        <div class="container">
            
            <div class="header">
                <div class="santa-emoji">🎁</div>
                <div class="title">Ho Ho Ho!</div>
                <div class="subtitle">Christmas came a little early because you're about to give someone a present!</div>
            </div>
            
            <div class="content">
                
                <p class="greeting">
                    Hello {gifter.name}! You've been tasked to gift:
                </p>
                
                <div class="golden-ticket">
                    <div class="golden-ticket-label">🎟️ YOUR GIFT RECIPIENT</div>
                    <div class="golden-ticket-name">{receiver.name}</div>
                </div>
                
                <p class="budget-text">
                    The price range is around <strong>₱50</strong>, but it's totally up to you if you want to go a bit over.
                </p>
                
                <div class="section-header">Here are some things {receiver.name} would love to receive:</div>
                
                <div class="wishlist">
                    <div class="wish priority">
                        <div class="wish-badge">⭐ PRIORITY WISH</div>
                        <div class="wish-title">{receiver.wish1}</div>
                        <div class="wish-desc">{receiver.wish1_desc}</div>
                    </div>
                    
                    <div class="wish">
                        <div class="wish-badge secondary">WISHLIST #2</div>
                        <div class="wish-title">{receiver.wish2}</div>
                        <div class="wish-desc">{receiver.wish2_desc}</div>
                    </div>
                    
                    <div class="wish">
                        <div class="wish-badge secondary">WISHLIST #3</div>
                        <div class="wish-title">{receiver.wish3}</div>
                        <div class="wish-desc">{receiver.wish3_desc}</div>
                    </div>
                </div>
                
            </div>
            
            <div class="footer">
                <div class="footer-message">Happy Gifting! 🎄</div>
                <div class="footer-family">From your 2-1N Family ❤️</div>
            </div>
            
        </div>
    </div>
</body>
</html>"""
    return html


def send_email_brevo(
    api_key: str,
    sender_email: str,
    sender_name: str,
    recipient_email: str,
    subject: str,
    body_text: str,
    body_html: str,
) -> None:
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key["api-key"] = api_key

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": recipient_email}],
        sender={"email": sender_email, "name": sender_name},
        subject=subject,
        html_content=body_html,
        text_content=body_text,
    )

    try:
        api_instance.send_transac_email(send_smtp_email)
    except ApiException as e:
        raise RuntimeError(f"Failed to send email: {e}") from e


def create_dummy_data() -> list[Participant]:
    """Create dummy test data for 3 participants."""
    return [
        Participant(
            section="BSCS 2-1N",
            email="example1@example.com",
            name="Lorem D. Ipsum  ",
            wish1="Chocolate Box",
            wish1_desc="Any brand of assorted chocolates",
            wish2="Notebook",
            wish2_desc="Preferably A5 size with lined pages",
            wish3="Keychain",
            wish3_desc="Cute animal designs",
        ),
        Participant(
            section="BSCS 2-1N",
            email="example2@example.com",
            name="Ipsum D. Lorem",
            wish1="Pen Set",
            wish1_desc="Gel pens in various colors",
            wish2="Stickers",
            wish2_desc="Aesthetic or anime stickers",
            wish3="Candy",
            wish3_desc="Sour candy preferred",
        ),
        Participant(
            section="BSCS 2-1N",
            email="example3@example.com",
            name="Luffy D. Lorem",
            wish1="Bookmark",
            wish1_desc="Metal or magnetic bookmarks",
            wish2="Snacks",
            wish2_desc="Any chips or crackers",
            wish3="Hair Clips",
            wish3_desc="Simple and minimalist design",
        ),
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Randomly assign gift givers and send emails")
    parser.add_argument("--csv", help="Path to cleaned CSV file")
    parser.add_argument("--dummy", action="store_true", help="Use dummy test data")
    parser.add_argument("--dry-run", action="store_true", help="Print emails instead of sending")
    parser.add_argument("--brevo-api-key", default=os.environ.get("BREVO_API_KEY"), help="Brevo API key (or set BREVO_API_KEY env var)")
    parser.add_argument("--sender-email", default=os.environ.get("SENDER_EMAIL", "noreply@yourdomain.com"), help="Sender email address")
    parser.add_argument("--sender-name", default=os.environ.get("SENDER_NAME", "BSCS 2-1N Gift Exchange"), help="Sender name")
    args = parser.parse_args()

    if args.dummy:
        participants = create_dummy_data()
        print("Using dummy test data with 3 participants")
    elif args.csv:
        participants = load_participants(Path(args.csv))
        print(f"Loaded {len(participants)} participants from {args.csv}")
    else:
        parser.error("Either --csv or --dummy is required")

    assignments = random_derangement(participants)

    print("\nAssignments:")
    for gifter, receiver in assignments:
        print(f"  {gifter.name} -> {receiver.name}")

    print()

    for gifter, receiver in assignments:
        body_text = build_email_body(gifter, receiver)
        body_html = build_email_html(gifter, receiver)
        subject = "Your Secret Santa Assignment!"

        if args.dry_run:
            print(f"=== Email to {gifter.email} ({gifter.name}) ===")
            print(body_text)
            print("=" * 50)
            print()
        else:
            api_key = args.brevo_api_key or os.environ.get("BREVO_API_KEY")
            if not api_key:
                parser.error("--brevo-api-key or BREVO_API_KEY env var required for sending emails")
            send_email_brevo(
                api_key,
                args.sender_email,
                args.sender_name,
                gifter.email,
                subject,
                body_text,
                body_html,
            )
            print(f"Sent email to {gifter.email}")

    print("Done!")


if __name__ == "__main__":
    main()
