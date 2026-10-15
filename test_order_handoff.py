from order_handoff import OrderHandoff, handoff
from observability_client import Infrai


class FakeClient:
    def __init__(self):
        self.calls = []

    def capture(self, exception, context):
        self.calls.append(("capture", exception, context))

    def report_metric(self, name, value, tags):
        self.calls.append(("metric", name, value, tags))


def test_handoff_records_metric_for_complete_order():
    client = FakeClient()
    result = handoff(OrderHandoff("ord-1", "seller-1", "asset-1", "buyer@example.com"), client)
    assert result == "handed_off"
    assert client.calls == [("metric", "marketplace.order_handoff", 1, {"seller_id": "seller-1"})]


def test_handoff_captures_missing_asset_without_metric():
    client = FakeClient()
    result = handoff(OrderHandoff("ord-1", "seller-1", "", "buyer@example.com"), client)
    assert result == "rejected"
    assert client.calls[0][0] == "capture"


def test_metric_request_includes_required_type(monkeypatch):
    requests_sent = []

    class Response:
        status_code = 200

        def json(self):
            return {"ok": True, "data": {}}

    def request(**kwargs):
        requests_sent.append(kwargs)
        return Response()

    monkeypatch.setattr("observability_client.requests.request", request)
    Infrai("test-key").report_metric("marketplace.order_handoff", 1, {"seller_id": "seller-1"})
    assert requests_sent[0]["json"] == {
        "name": "marketplace.order_handoff",
        "value": 1,
        "type": "counter",
        "tags": {"seller_id": "seller-1"},
    }
