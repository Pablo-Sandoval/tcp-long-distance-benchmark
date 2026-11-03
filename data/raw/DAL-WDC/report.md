# Cross-Datacenter TCP Optimization Benchmark Report

**Campaign Identifier**: `20261016_151806Z_sender_to_10_241_64_4_22_10gib_seed42`  
**Timestamp UTC**: `20261016_151806Z`  
**Payload Size**: `10 GiB` | **Blocks**: `30` | **Seed**: `42`  

## 1. Summary Statistics (Application Goodput Mbps, Conservative 95% CI)

| Variation Code | N | Mean (Mbps) | Std Dev | Median | 95% CI |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `V01_BASELINE_4M` | 30 | 406.97 | 10.47 | 408.72 | [403.03, 410.91] |
| `V02_SACK_OFF_4M` | 30 | 405.12 | 11.85 | 405.37 | [400.67, 409.58] |
| `V03_BUF_16M` | 30 | 401.18 | 35.89 | 408.27 | [387.69, 414.68] |
| `V04_BUF_64M` | 30 | 407.04 | 8.70 | 408.29 | [403.77, 410.31] |
| `V05_CUBIC_FQ_16M` | 30 | 407.64 | 10.25 | 410.19 | [403.78, 411.49] |
| `V06_BBR_FQ_16M` | 30 | 408.80 | 9.55 | 410.13 | [405.21, 412.39] |
| `V08_CIPHER_CHACHA_16M` | 30 | 405.19 | 12.59 | 407.12 | [400.46, 409.92] |
| `V09_COMP_RAW_16M` | 30 | 389.78 | 12.27 | 391.82 | [385.16, 394.39] |
| `V10_COMP_GZIP_16M` | 30 | 433.65 | 1.52 | 434.23 | [433.08, 434.22] |
