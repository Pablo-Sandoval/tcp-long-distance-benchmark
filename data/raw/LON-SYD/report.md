# Cross-Datacenter TCP Optimization Benchmark Report

**Campaign Identifier**: `20261016_153511Z_sender_to_10_245_64_4_22_10gib_seed42`  
**Timestamp UTC**: `20261016_153511Z`  
**Payload Size**: `10 GiB` | **Blocks**: `30` | **Seed**: `42`  

## 1. Summary Statistics (Application Goodput Mbps, Conservative 95% CI)

| Variation Code | N | Mean (Mbps) | Std Dev | Median | 95% CI |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `V01_BASELINE_4M` | 30 | 53.82 | 1.14 | 53.92 | [53.39, 54.25] |
| `V02_SACK_OFF_4M` | 30 | 53.82 | 1.04 | 53.95 | [53.43, 54.21] |
| `V03_BUF_16M` | 30 | 54.12 | 0.61 | 54.16 | [53.89, 54.36] |
| `V04_BUF_64M` | 30 | 53.86 | 0.98 | 53.73 | [53.49, 54.23] |
| `V05_CUBIC_FQ_16M` | 30 | 54.83 | 0.79 | 54.84 | [54.53, 55.13] |
| `V06_BBR_FQ_16M` | 30 | 53.32 | 0.87 | 53.38 | [53.00, 53.65] |
| `V08_CIPHER_CHACHA_16M` | 30 | 53.92 | 0.76 | 54.05 | [53.64, 54.21] |
| `V09_COMP_RAW_16M` | 30 | 54.03 | 1.62 | 54.28 | [53.42, 54.63] |
| `V10_COMP_GZIP_16M` | 30 | 389.41 | 0.72 | 389.84 | [389.14, 389.68] |
