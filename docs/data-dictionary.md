# Data dictionary

| Field | Definition | Unit / values |
|---|---|---|
| block_id | Randomized execution block | integer |
| order_in_block | Execution position within block | integer |
| variation_code | Controlled treatment identifier | V01-V10 defined in methodology |
| validation_status | Treatment and transfer validation outcome | categorical |
| checksum_status | Integrity verification outcome | categorical |
| duration_sec | Monotonic elapsed time | seconds; decimal |
| application_goodput_mbps | Original logical payload bits divided by elapsed time | Mbps |
| expected_bytes | Original logical payload size | bytes |
| received_bytes | Reconstructed logical payload at receiver | bytes |
| transmitted_bytes | Bytes placed on the network for the payload, when measurable | bytes |
| compression_ratio | Original logical bytes divided by transmitted compressed bytes | ratio |
| sender_host_cpu_pct | Sender host CPU utilization over transfer window | percent |
| receiver_host_cpu_pct | Receiver host CPU utilization over transfer window | percent |
| observed_cc | Active congestion-control algorithm | cubic, bbr, etc. |
| rtt_min_ms / rtt_avg_ms / rtt_max_ms | Socket RTT observations | milliseconds |
| retrans_total_observed | Observed retransmission counter | count |
| retrans_delta | Counter change over transfer window | count |
| cwnd_final | Final sampled congestion window | segments |
| mss | Maximum segment size | bytes |
| route_id | Anonymized source-destination route label | text |
| random_seed | Seed used to randomize the block | integer/text |
| benchmark_version | Tagged framework version | semantic version |
| commit_hash | Source revision used for the run | Git commit |
