# API Reference — Web Playground

Base URL: `https://quanticsai.com/playground/valuations`

## Endpoints

### `POST /api/valuations/calculate`
Run a DCF or 3-statement model.

**Request:**
```json
{
  "model_type": "dcf",
  "assumptions": {
    "fcf_base": 110000000000,
    "fcf_growth_rate": 5.0,
    "wacc": 7.65,
    "terminal_growth": 2.5,
    "net_debt": -50000000000,
    "shares_outstanding": 15500
  }
}
```

**Response:**
```json
{
  "enterprise_value": 2800000000000,
  "equity_value": 2850000000000,
  "price_per_share": 183.87,
  "pv_explicit": 520000000000,
  "pv_terminal": 2280000000000,
  "fcf_projections": [...],
  "sensitivity_wacc_growth": {...}
}
```

### `GET /api/health`
Health check.

**Response:** `{"status": "ok", "version": "0.1.0"}`
