
# PayPilot AI

### Your Smart Business Payment Assistant

PayPilot AI helps freelancers and small businesses turn customer requests into professional invoice drafts using AI and collect payments through PayPal.

## Features

- AI-powered invoice draft generation using Google Gemini.
- Extracts service descriptions, customer details, payment terms and missing information.
- PayPal Sandbox payment integration.
- Secure payment capture and verification through PayPal.
- Simple web interface built with Flask.

## Technologies Used

- Python
- Flask
- Google Gemini API
- PayPal Checkout API
- HTML and CSS

## Setup

1. Clone this repository.
2. Install dependencies:

   `pip install -r requirements.txt`

3. Create a `.env` file with:

   `GEMINI_API_KEY=your_key`

   `PAYPAL_CLIENT_ID=your_client_id`

   `PAYPAL_CLIENT_SECRET=your_secret`

   `PAYPAL_BASE_URL=https://api-m.sandbox.paypal.com`

4. Run the application:

   `python app.py`

5. Open `http://127.0.0.1:5000`.

## Payment Testing

This project uses PayPal Sandbox. No real money is involved.

## License

MIT License.
