# Accuracy-Cost-Energy Pareto Benchmark V2 - Measured CPU/GPU Contract

This is not a continuation of the analytic V1 claim. V2 excludes closed-form analytic targets and requires measured CPU/GPU telemetry before any Pareto or crossover claim.

## Required measured run

Run on a node with CPU energy telemetry and NVIDIA GPU telemetry:

```bash
python3 scripts/build_accuracy_cost_energy_pareto_v2_measured.py \
  --output-dir docs/benchmarks/accuracy_cost_energy_pareto_v2_gpu_cpu_measured_YYYYMMDD \
  --mode measured-run
```

The current script emits the governed contract and hardware probe. The measured runner must attach per-method/target/budget rows with CPU RAPL or equivalent energy, GPU NVML power/memory, wall time, cloud SKU cost profile, and independent reference status.

## Target count formula

`4 dimensions x 5 confidence levels x 8 regimes x 2 metrics = 320 target rows`.

## Reference oracle

V2 targets deliberately exclude closed-form analytic answers. A measured row is not enough. Each target needs a reference object with uncertainty, and the acceptance equation is:

`|method_estimate - reference_estimate| <= predeclared_tolerance + reference_ci_half_width`.

If reference engines disagree beyond the declared tolerance, the result is `REFERENCE_DISAGREEMENT_INCONCLUSIVE`, not PASS.

The named per-regime reference plan is in `reference_oracle_contract.json`. A reference implementation and evaluated participant may not share the same production/candidate code path.

## Telemetry protocol

- CPU energy: RAPL or equivalent package-energy counter. Cloud VMs may need bare-metal to expose this.
- GPU energy: NVML power integration over multi-iteration windows; short engines cannot be scored from a single sample.
- Energy accounting: publish both total energy and incremental energy over idle; headline uses total infrastructure energy.
- Latency scope: headline is end-to-end workload including host/device transfer where applicable; engine-only is secondary.
- Repeats: N>=3 fresh-process correctness repeats and >=10 telemetry windows for energy dispersion.
- Cloud dollars: published dated SKU rate x measured device-seconds, not directly measured dollars.

## Pre-registration

The crossover hypothesis is stored in `crossover_preregistration_hypothesis.json` and hash-bound in the status artifact. A post-hoc crossover story does not unlock the public claim.

## Node requirements

The node specification is stored in `node_requirements.json`: bare-metal or telemetry-equivalent CPU energy, NVML-capable NVIDIA GPU, CuPy/CUDA runner, fixed/recorded clock policy, idle baseline, and dated cloud cost profile.

## Public claim gate

No public claim is allowed unless `frontier_acceptance_gate.crossover_claim_allowed=true`. In this contract build it is deliberately false.
