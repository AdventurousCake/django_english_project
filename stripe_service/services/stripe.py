import stripe
from django.urls import reverse

stripe.api_key = 'sk_test_4eC39HqLyjWDarjtT1zdp7dc'


# stripe.Card
def create_stripe_session(product_name: str,
                          price: int,
                          secret_key: str | None,
                          redirect_url: str = reverse("stripe_service:success"),
                          cancel_url: str = reverse("stripe_service:cancel"),

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
    )
