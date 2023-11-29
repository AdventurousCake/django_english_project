from decimal import Decimal

import stripe

# stripe.api_key = '12412515'
stripe.api_key = 'sk_test_51MiibLILrXouSZMzvvUe0GbeId5AIqgdjH9UGneTdmRhZ6D5boizxwtheC28CjjJNMZSZtSFTTftPRpIa6ILuoj700F0aCVPT8'


# stripe.Card
def create_stripe_session(product_name: str,
                          price: int | Decimal,
                          redirect_url: str,
                          cancel_url: str,
                          secret_key: str | None = None,

                          quantity: int = 1,
                          currency: str = "usd",
                          ) -> stripe.checkout.Session:
    """
    Creates and returns stripe session object.
    Supports only ONE line item (No more!)
    """

    # stripe.api_key = secret_key
    return stripe.checkout.Session.create(
        line_items=[
            {
                "price_data": {
                    "currency": currency,
                    "product_data": {
                        "name": product_name,
                    },
                    "unit_amount": price,
                },
                "quantity": quantity,
            }
        ],
        success_url=redirect_url,
        cancel_url=cancel_url,
        mode="payment",

        # client_reference_id=request.user.id if request.user.is_authenticated else None,
    )
