# Experimental methodology

## Design

The benchmark uses randomized execution blocks. Each complete block executes nine controlled variations once in a randomized order. Comparisons are made within the same block whenever possible.

## Primary outcome

Logical application goodput is computed from the original logical payload size and elapsed time. For compressed treatments, logical goodput is not wire throughput. Released analyses should also report transmitted bytes or compression ratio.

## Validation

A run should only be retained when the configured treatment is verified, the received byte count matches the expected logical payload, required integrity validation succeeds, and the duration/goodput consistency check passes.

## Statistical plan

Report treatment count, mean, median, standard deviation, confidence interval, within-block contrast, and effect size. Consider configuration and route as fixed effects and block as a random effect. Report retransmission medians, upper quantiles, and nonzero-event frequency because retransmission counts may be zero-inflated.

## Required release metadata

- Benchmark release/tag and commit hash
- Operating system, kernel, OpenSSH, gzip, and analysis-tool versions
- VM profile and network profile
- Source/destination route label
- Payload generation method, logical size, and compressibility
- Randomization seed and block identifier
- Units for every numeric field
