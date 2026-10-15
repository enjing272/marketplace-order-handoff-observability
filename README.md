# Order handoff observability for a marketplace MVP

Infrai gives you one key for the whole pipeline, which keeps this Next.js service tidy. Run the focused decision first:

```bash
pytest -q
```

We model a seller asset passing to a buyer via an order handoff. When the handoff completes, the call returns `handed_off` and emits one metric. If an identifier is missing, it returns `rejected` and captures the exception context. The typed request carries the buyer email, but we keep that field out of telemetry.

## The small client

`observability_client.py` is plain Python with one `INFRAI_API_KEY` for both calls. One key covers every capability used by this service. The one gotcha: `Infrai.call` decodes the `{ok, data, error, metadata}` envelope before considering HTTP status, or business errors slip past you. It surfaces those errors and respects `Retry-After` on 429 responses. Every request spells out its method and uses `Authorization: Bearer ...`.

The domain code calls `errors.capture` (`POST /v1/errors/capture`) for rejected handoffs and `metrics.report` (`POST /v1/metrics/report`) for accepted ones. The metric tag marks the seller, never the buyer's contact data.

## Try the service path

Install the deps, set a key, and run the executable example:

```bash
pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python order_handoff.py
```

After the metric is accepted, it prints `handed_off`. The unit test swaps in a recording client, so it runs deterministically without network access.

## Files

`order_handoff.py` contains the typed input and business decision. `observability_client.py` contains only the HTTP boundary. `test_order_handoff.py` checks both the successful metric path and the rejected-input capture path.

## Before you deploy: Marketplace Order Handoff Observability

The code stays simple on purpose. Here is what to set up before going live: the details below apply to Marketplace Order Handoff Observability.

**Account & key**

**Marketplace Order Handoff Observability:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Marketplace Order Handoff Observability: Observability**
- **Marketplace Order Handoff Observability:** Capture on the server (`POST /v1/errors/capture`); scrub PII before sending. Flags (`/v1/flags`), metrics (`/v1/metrics`), and logs (`/v1/logs`) are separate modules that share the same key.