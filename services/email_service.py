import time


def send_order_confirmation_email(
    email: str,
    order_id: int
):
    """
    Simulates sending an email.
    """

    print(
        f"Starting email task for Order #{order_id}"
    )

    # simulate slow email service
    time.sleep(10)

    print(
        f"""
        ==================================
        EMAIL SENT
        ==================================
        To: {email}

        Subject: Order Confirmation

        Your order #{order_id}
        was placed successfully.
        ==================================
        """
    )