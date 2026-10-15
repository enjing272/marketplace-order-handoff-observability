from dataclasses import dataclass

from observability_client import Infrai


@dataclass(frozen=True)
class OrderHandoff:
    order_id: str
    seller_id: str
    asset_id: str
    buyer_email: str


def handoff(order: OrderHandoff, client: Infrai) -> str:
    """Return the next state after validating a privacy-safe handoff."""
    if not order.order_id or not order.seller_id or not order.asset_id:
        client.capture("missing order handoff identifier", {"order_id": order.order_id})
        return "rejected"
    client.report_metric("marketplace.order_handoff", 1, {"seller_id": order.seller_id})
    return "handed_off"


if __name__ == "__main__":
    import os

    result = handoff(OrderHandoff("ord-42", "seller-7", "asset-9", "buyer@example.com"), Infrai(os.environ["INFRAI_API_KEY"]))
    print(result)
