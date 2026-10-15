# Long-Distance Cloud Transfer Benchmark

[![DOI](https://zenodo.org/badge/1421186106.svg)](https://doi.org/10.5281/zenodo.23403337)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE-CODE)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](LICENSE-DATA-DOCS)
[![Python: 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-1.0.0-green.svg)](scripts/tcp_phd_benchmark.py)

A reproducible randomized-block framework for comparing reliability, BDP buffer ceilings, congestion control, encrypted-transfer ciphers, and application-level data reduction over long-distance cloud paths.

## Research axes

1. **Reliability / SACK:** `V02_SACK_OFF_4M` vs `V01_BASELINE_4M`
2. **BDP buffers:** `V01_BASELINE_4M` vs `V03_BUF_16M` vs `V04_BUF_64M`
3. **Congestion control:** `V05_CUBIC_FQ_16M` vs `V06_BBR_FQ_16M`
4. **Encryption:** `V03_BUF_16M` vs `V08_CIPHER_CHACHA_16M`
5. **Data reduction:** `V09_COMP_RAW_16M` vs `V10_COMP_GZIP_16M`

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

## Citation

```bibtex
@software{sandoval2026tcp,
  author       = {Pablo Andrés Sandoval Rojas and Rosa Gabriela Camero Berrones},
  title        = {Cross-Datacenter TCP Long-Distance Optimization Benchmark},
  month        = mar,
  year         = 2026,
  publisher    = {Zenodo},
  version      = {v1.0.0},
  doi          = {10.5281/zenodo.23403337},
  url          = {https://doi.org/10.5281/zenodo.23403337}
}
```

Citation metadata is also provided in `CITATION.cff`.

## License

Code is provided under the [MIT License](LICENSE-CODE). Documentation and released datasets are provided under [CC BY 4.0](LICENSE-DATA-DOCS).
