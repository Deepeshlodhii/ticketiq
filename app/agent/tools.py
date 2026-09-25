def check_account_status(customer_id: str) -> dict:
    """
    Mock account-status tool.

    In production this would query the customer/account service.
    """

    mock_accounts = {
        "CUST001": {
            "status": "active",
            "verification": "verified",
        },
        "CUST002": {
            "status": "locked",
            "verification": "required",
        },
        "CUST003": {
            "status": "active",
            "verification": "pending",
        },
    }

    account = mock_accounts.get(
        customer_id,
        {
            "status": "unknown",
            "verification": "unknown",
        },
    )

    return {
        "customer_id": customer_id,
        **account,
    }


def check_refund_eligibility(order_id: str) -> dict:
    """
    Mock refund-eligibility tool.

    In production this would query an order/payment service.
    """

    mock_orders = {
        "ORD001": {
            "eligible": True,
            "reason": "Purchase is within the refund window.",
        },
        "ORD002": {
            "eligible": False,
            "reason": "Purchase is outside the refund window.",
        },
        "ORD003": {
            "eligible": True,
            "reason": "Duplicate charge detected.",
        },
    }

    order = mock_orders.get(
        order_id,
        {
            "eligible": False,
            "reason": "Order could not be verified.",
        },
    )

    return {
        "order_id": order_id,
        **order,
    }
