# Cross-Datacenter TCP Optimization Benchmark Report

**Campaign Identifier**: `20261021_173144Z_sender_to_10_245_64_4_22_10gib_seed42`  
**Timestamp UTC**: `20261021_173144Z`  
**Payload Size**: `10 GiB` | **Blocks**: `30` | **Seed**: `42`  

## 1. Summary Statistics (Application Goodput Mbps, Conservative 95% CI)

| Variation Code | N | Mean (Mbps) | Std Dev | Median | 95% CI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `V01_BASELINE_4M` | 30 | 73.38 | 1.51 | 73.02 | [72.81, 73.94] |
| `V02_SACK_OFF` | 0 | 0.00 | 0.00 | 0.00 | [0.00, 0.00] |
| `V03_BUFFER_16M` | 0 | 0.00 | 0.00 | 0.00 | [0.00, 0.00] |
| `V04_BUFFER_64M` | 0 | 0.00 | 0.00 | 0.00 | [0.00, 0.00] |
| `V05_CC_BBR` | 0 | 0.00 | 0.00 | 0.00 | [0.00, 0.00] |
| `V06_BBR_16M` | 0 | 0.00 | 0.00 | 0.00 | [0.00, 0.00] |
| `V07_BBR_64M` | 0 | 0.00 | 0.00 | 0.00 | [0.00, 0.00] |
| `V08_CIPHER_CHACHA_16M` | 30 | 73.73 | 1.47 | 73.65 | [73.18, 74.28] |
| `V09_COMP_STRUCTURED_16M` | 0 | 0.00 | 0.00 | 0.00 | [0.00, 0.00] |
| `V10_COMP_GZIP_16M` | 30 | 419.98 | 0.75 | 420.22 | [419.70, 420.26] |
