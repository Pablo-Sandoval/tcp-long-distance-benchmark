# Long-Distance Cloud Transfer Benchmark

A reproducible randomized-block framework for comparing reliability, BDP buffer ceilings, congestion control, encrypted-transfer ciphers, and application-level data reduction over long-distance cloud paths.

## Research axes

1. **Reliability / SACK:** `V02_SACK_OFF_4M` vs `V01_BASELINE_4M`
2. **BDP buffers:** `V01_BASELINE_4M` vs `V03_BUF_16M` vs `V04_BUF_64M`
3. **Congestion control:** `V05_CUBIC_FQ_16M` vs `V06_BBR_FQ_16M`
4. **Encryption:** `V03_BUF_16M` vs `V08_CIPHER_CHACHA_16M`
5. **Data reduction:** `V09_COMP_RAW_16M` vs `V10_COMP_GZIP_16M`

## Repository status

This is a research-artifact scaffold. Add the production automation script under `scripts/` and replace placeholders before the first public release. Preliminary spreadsheets are included under `data/raw/` and must be reviewed for sensitive metadata before publication.

## Repository layout

```text
scripts/             Execution and telemetry collection
configs/variations/  Machine-readable treatment profiles
data/raw/            Immutable original measurements
data/processed/      Normalized, analysis-ready datasets
notebooks/           Statistical analysis and figures
docs/                Methodology, data dictionary, and protocols
figures/             Generated publication figures
tests/               Validation and consistency tests
```

## Reproducibility requirements

Each run should preserve the configuration, randomization seed, source and destination environment, kernel and OpenSSH versions, route label, payload characteristics, elapsed-time unit, integrity status, and telemetry fields defined in `docs/data-dictionary.md`. Raw data should never be manually edited; corrections should be implemented as a documented processing step.

## Security and publication review

Do not publish passwords, API keys, SSH private keys, host keys, private IP addresses, customer identifiers, cloud account identifiers, or internal-only infrastructure details. Confirm employer, cloud-provider, and university publication requirements before making the repository public.

## Citation

Citation metadata is provided in `CITATION.cff`. Replace the placeholder repository URL and add the release DOI after archiving the first stable release.

## License

Code is provided under the MIT License. Documentation and released datasets are provided under CC BY 4.0, subject to the publication review above.
