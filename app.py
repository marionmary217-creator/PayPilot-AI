
import os
from decimal import Decimal, InvalidOperation

from flask import Flask, render_template, request, redirect
from dotenv import load_dotenv
from google import genai
from google.genai import types

from paypal_service import create_order, capture_order

load_dotenv()

app = Flask(__name__)

api_key = os.getenv("GEMINI_API_KEY")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():

    customer_request = request.form.get("request", "").strip()

    if not customer_request:
        return "Please enter a customer request."

    if not api_key:
        return "Gemini API key not found."

    try:
        client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(timeout=20000)
        )

        models_to_try = [
            "models/gemini-3.5-flash-lite",
            "models/gemini-3.1-flash-lite"
        ]

        prompt = f"""
You are PayPilot AI, a business payment assistant.

Generate a professional invoice draft based on:

{customer_request}

Include:
1. Service Description
2. Customer Details
3. Invoice Amount and Currency
4. Payment Terms
5. Delivery Details
6. Missing Information

Rules:
- Never invent customer details.
- Never invent prices or taxes.
- Do not assume payment has been made.
- Clearly mention missing information.
- This is a draft requiring owner approval.
"""

        invoice = None

        for model_name in models_to_try:
            try:
                print("Trying model:", model_name)

                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )

                if response.text:
                    invoice = response.text
                    print("Invoice generated successfully!")
                    break

            except Exception as error:
                print("Model failed:", model_name, repr(error))

        if not invoice:
            return "AI is temporarily unavailable. Please try again."

        return render_template(
            "invoice.html",
            invoice=invoice,
            customer_request=customer_request
        )

    except Exception as error:
        print("Gemini error:", repr(error))
        return "Something went wrong while generating the invoice."


# Create a PayPal Sandbox payment
@app.route("/create-payment", methods=["POST"])
def create_payment():

    try:
        amount = Decimal(request.form.get("amount", "0"))
        currency = request.form.get("currency", "USD").upper()

        if not amount.is_finite() or amount <= 0:
            return "Please enter a valid amount."

        if amount > Decimal("10000"):
            return "Amount is too high for this demo."

        if currency not in ["USD", "EUR", "GBP"]:
            return "Unsupported demo currency."

        order = create_order(amount, currency)

        approval_url = next(
            (
                link["href"]
                for link in order.get("links", [])
                if link.get("rel") in ["approve", "payer-action"]
            ),
            None
        )

        if not approval_url:
            return "PayPal did not return an approval link."

        return redirect(approval_url)

    except Exception as error:
        print("PayPal order error:", repr(error))
        return "Could not create PayPal payment. Check the VS Code terminal."


# PayPal returns the customer here after approval
@app.route("/paypal/return")
def paypal_return():

    order_id = request.args.get("token")

    if not order_id:
        return "PayPal order ID is missing."

    try:
        result = capture_order(order_id)

        if result.get("status") == "COMPLETED":
            return """
            <h1>Payment Successful!</h1>
            <p>PayPal confirmed that your Sandbox payment was completed.</p>
            <a href="/">Return to PayPilot AI</a>
            """

        return """
        <h1>Payment Not Completed</h1>
        <p>PayPal has not confirmed a completed payment.</p>
        <a href="/">Return to PayPilot AI</a>
        """

    except Exception as error:
        print("PayPal capture error:", repr(error))
        return "Payment verification failed. Check the VS Code terminal."


@app.route("/paypal/cancel")
def paypal_cancel():
    return """
    <h1>Payment Cancelled</h1>
    <p>You cancelled the PayPal payment.</p>
    <a href="/">Return to PayPilot AI</a>
    """


if __name__ == "__main__":
    app.run(debug=True)
