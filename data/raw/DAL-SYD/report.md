# Cross-Datacenter TCP Optimization Benchmark Report

**Campaign Identifier**: `20261012_061830Z_sender_to_10_245_64_4_22_10gib_seed42`  
**Timestamp UTC**: `20261012_061830Z`  
**Payload Size**: `10 GiB` | **Blocks**: `30` | **Seed**: `42`  

## 1. Summary Statistics (Application Goodput Mbps, Conservative 95% CI)

| Variation Code | N | Mean (Mbps) | Std Dev | Median | 95% CI |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `V01_BASELINE_4M` | 30 | 84.53 | 1.53 | 85.01 | [83.96, 85.10] |
| `V02_SACK_OFF_4M` | 30 | 83.34 | 2.21 | 83.51 | [82.52, 84.17] |
| `V03_BUF_16M` | 30 | 84.50 | 1.95 | 84.51 | [83.77, 85.24] |
| `V04_BUF_64M` | 30 | 84.88 | 1.70 | 85.06 | [84.24, 85.52] |
| `V05_CUBIC_FQ_16M` | 30 | 85.36 | 2.52 | 85.28 | [84.41, 86.30] |
| `V06_BBR_FQ_16M` | 30 | 84.27 | 1.69 | 84.12 | [83.63, 84.91] |
| `V08_CIPHER_CHACHA_16M` | 30 | 83.76 | 2.04 | 83.94 | [83.00, 84.53] |
| `V09_COMP_RAW_16M` | 30 | 84.03 | 2.11 | 83.50 | [83.24, 84.83] |
| `V10_COMP_GZIP_16M` | 30 | 405.17 | 17.38 | 393.11 | [398.63, 411.71] |
