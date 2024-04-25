import json
from pprint import pprint

import stripe
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from typing_extensions import Literal, Mapping

from src.config import config
from src.db.repositories.user import add_tokens

router = APIRouter()

Product = Literal["p1", "p2", "p3"]

product_to_price_id_mapping: Mapping[Product, str] = {
    "p1": "price_1P8V53Ewc70ITpsyugKDMSkP",
    "p2": "price_1P8V60Ewc70ITpsyBAm3uVlT",
    "p3": "price_1P8V6eEwc70ITpsyuzYIEOLM",
}


@router.post("/create_checkout_session")
def create_checkout_session(product: Product, user_email: str, auth0_sub: str):
    print(auth0_sub)
    try:
        checkout_session_creation_args = {
            "line_items": [
                {
                    "price": product_to_price_id_mapping[product],
                    "quantity": 1,
                },
            ],
            "mode": "payment",
            "success_url": f"{config['front_domain']}/app",  # take you to what you paid for or onboarding or congratulations and next steps
            "cancel_url": f"{config['front_domain']}/app",  # back to plans url; payment failed, here are options again
            "automatic_tax": {"enabled": True},
            "metadata": {"auth0_sub": auth0_sub, "test_meta": "test_meta123"},
            "customer_email": user_email,
        }

        if product == "p1":
            checkout_session_creation_args.update(
                {
                    "allow_promotion_codes": True,
                }
            )

        checkout_session = stripe.checkout.Session.create(
            **checkout_session_creation_args
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return RedirectResponse(url=str(checkout_session.url), status_code=303)


@router.post("/stripe_webhooks")
async def my_webhook_view(request: Request):
    payload = await request.body()
    event = None

    try:
        event = stripe.Event.construct_from(
            json.loads(payload.decode("utf-8")), stripe.api_key
        )
    except ValueError as e:
        # Invalid payload
        raise HTTPException(status_code=400, detail="Invalid payload")

    if event["type"] in ["checkout.session.completed"]:
        amount_to_product_mapping: Mapping[int, Product] = {
            900: "p1",
            1900: "p2",
            4900: "p3",
        }
        amount_subtotal = event["data"]["object"]["amount_subtotal"]
        product = amount_to_product_mapping[amount_subtotal]
        handle_checkout_complete(
            product, event["data"]["object"]["metadata"]["auth0_sub"]
        )

    # print(event["type"])

    # # Handle the event
    # if event.type == "payment_intent.succeeded":
    #     payment_intent = event.data.object  # contains a stripe.PaymentIntent
    #     # Then define and call a method to handle the successful payment intent.
    #     # await handle_payment_intent_succeeded(payment_intent)
    # elif event.type == "payment_method.attached":
    #     payment_method = event.data.object  # contains a stripe.PaymentMethod
    #     # Then define and call a method to handle the successful attachment of a PaymentMethod.
    #     # await handle_payment_method_attached(payment_method)
    # # ... handle other event types
    # else:
    #     print("Unhandled event type {}".format(event.type))

    return JSONResponse(content={"message": "Event received"}, status_code=200)


def handle_checkout_complete(product: Product, user_sub: str):
    # update db with proper amount
    # 4 8 16
    product_to_tokens = {"p1": 4 * 3, "p2": 8 * 3, "p3": 16 * 3}
    add_tokens(user_sub, product_to_tokens[product])
