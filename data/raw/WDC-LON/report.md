# Cross-Datacenter TCP Optimization Benchmark Report

**Campaign Identifier**: `20261012_062207Z_sender_to_10_242_64_4_22_10gib_seed42`  
**Timestamp UTC**: `20261012_062207Z`  
**Payload Size**: `10 GiB` | **Blocks**: `30` | **Seed**: `42`  

## 1. Summary Statistics (Application Goodput Mbps, Conservative 95% CI)

| Variation Code | N | Mean (Mbps) | Std Dev | Median | 95% CI |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `V01_BASELINE_4M` | 30 | 108.50 | 4.65 | 110.05 | [106.75, 110.25] |
| `V02_SACK_OFF_4M` | 30 | 110.34 | 2.47 | 110.52 | [109.41, 111.27] |
| `V03_BUF_16M` | 30 | 110.11 | 1.74 | 109.79 | [109.45, 110.76] |
| `V04_BUF_64M` | 30 | 109.40 | 3.64 | 110.28 | [108.03, 110.77] |
| `V05_CUBIC_FQ_16M` | 30 | 110.78 | 8.17 | 112.78 | [107.71, 113.85] |
| `V06_BBR_FQ_16M` | 30 | 110.33 | 1.36 | 110.44 | [109.81, 110.84] |
| `V08_CIPHER_CHACHA_16M` | 30 | 109.17 | 3.52 | 109.79 | [107.85, 110.50] |
| `V09_COMP_RAW_16M` | 30 | 110.24 | 2.01 | 110.72 | [109.49, 111.00] |
| `V10_COMP_GZIP_16M` | 30 | 392.42 | 0.50 | 392.26 | [392.24, 392.61] |
