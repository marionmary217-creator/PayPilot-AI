
import os
import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET")
BASE_URL = os.getenv(
    "PAYPAL_BASE_URL",
    "https://api-m.sandbox.paypal.com"
)


def get_access_token():

    response = requests.post(
        f"{BASE_URL}/v1/oauth2/token",
        auth=(CLIENT_ID, CLIENT_SECRET),
        data={"grant_type": "client_credentials"},
        timeout=20
    )

    response.raise_for_status()

    return response.json()["access_token"]


def create_order(amount, currency="USD"):

    token = get_access_token()

    payload = {
        "intent": "CAPTURE",
        "purchase_units": [
            {
                "amount": {
                    "currency_code": currency,
                    "value": f"{amount:.2f}"
                }
            }
        ],
        "payment_source": {
            "paypal": {
                "experience_context": {
                    "return_url": "http://127.0.0.1:5000/paypal/return",
                    "cancel_url": "http://127.0.0.1:5000/paypal/cancel"
                }
            }
        }
    }

    response = requests.post(
        f"{BASE_URL}/v2/checkout/orders",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        },
        json=payload,
        timeout=20
    )

    response.raise_for_status()

    return response.json()


def capture_order(order_id):

    token = get_access_token()

    response = requests.post(
        f"{BASE_URL}/v2/checkout/orders/{order_id}/capture",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        },
        json={},
        timeout=20
    )

    response.raise_for_status()

    return response.json()
