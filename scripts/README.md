# Scripts

Place the production benchmark runner and supporting modules here. Recommended separation:

- `run_benchmark.py` or `run_benchmark.sh`: orchestration and randomized blocks
- `configure_transport.*`: kernel and queue-discipline configuration
- `collect_telemetry.*`: RTT, retransmission, cwnd, MSS, CPU, and active-CC capture
- `validate_run.*`: bytes, checksum, duration, and treatment validation
- `export_results.*`: stable tabular schema

The production script was not available in this workspace, so this package intentionally contains documentation rather than fabricated executable code.
