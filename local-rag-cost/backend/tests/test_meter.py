from datetime import datetime, timedelta
from backend.app.observability.meter import Meter, MeterRow


def test_meter_write_and_usage(tmp_path):
    db = tmp_path / "obs.duckdb"
    pricing = tmp_path / "pricing.yaml"
    pricing.write_text("models:\n  test-model:\n    input_per_million: 1\n    output_per_million: 2\n")
    meter = Meter(db_path=db, pricing_path=pricing)
    cost = meter.compute_cost("test-model", 1000, 2000)
    meter.write_row(
        MeterRow(
            timestamp=datetime.utcnow(),
            workspace_id="w1",
            user_id="u1",
            provider="x",
            model="test-model",
            op_type="generate",
            input_tokens=1000,
            output_tokens=2000,
            cost_usd=cost,
            latency_ms=10,
            cache_hit=False,
            query_hash="q",
        )
    )
    out = meter.get_usage("w1", datetime.utcnow() - timedelta(days=1), datetime.utcnow() + timedelta(days=1))
    assert out["calls"] == 1
    assert out["input_tokens"] == 1000
    assert out["output_tokens"] == 2000
    assert out["cost_usd"] is not None
