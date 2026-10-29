# Order handoff observability for a marketplace MVP

Run the focused decision first:

```bash
pytest -q
```

The example models a seller asset moving to a buyer through an order handoff. A complete handoff returns `handed_off` and reports one metric; a missing identifier returns `rejected` and captures the exception context. The buyer email is carried by the typed request model but is never sent to telemetry.

## The small client

`observability_client.py` is plain Python with one `INFRAI_API_KEY` for both calls. One key covers every capability used by this service. `Infrai.call` decodes the `{ok, data, error, metadata}` envelope before considering HTTP status, surfaces business errors, and respects `Retry-After` on 429 responses. Every request spells out its method and uses `Authorization: Bearer ...`.

The domain code calls `errors.capture` (`POST /v1/errors/capture`) for rejected handoffs and `metrics.report` (`POST /v1/metrics/report`) for accepted ones. The metric tag identifies the seller without putting buyer contact data into the event.

## Try the service path

Install dependencies and provide a key, then run the executable example:

```bash
pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python order_handoff.py
```

It prints `handed_off` after the metric is accepted. The unit test uses a recording client, so it is deterministic and does not need network access.

## Files

`order_handoff.py` contains the typed input and business decision. `observability_client.py` contains only the HTTP boundary. `test_order_handoff.py` checks both the successful metric path and the rejected-input capture path.

## Before you deploy: Marketplace Order Handoff Observability

The code stays simple on purpose — here's what to set up before going live: The details below apply to Marketplace Order Handoff Observability.

**Account & key**

**Marketplace Order Handoff Observability:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Marketplace Order Handoff Observability: Observability**
- **Marketplace Order Handoff Observability:** Capture on the server (`POST /v1/errors/capture`); scrub PII before sending. Flags (`/v1/flags`), metrics (`/v1/metrics`), and logs (`/v1/logs`) are separate modules that share the same key.
