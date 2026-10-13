#!/usr/bin/env python3
"""
TCP PhD Cross-Datacenter Performance Benchmarking Suite
Version: 4.0.0-phd-frozen-definitive
License: Academic Research Use (Sandoval Doctoral Dissertation / ANEXO-4)

Execution Mode: Always Interactive Prompt Wizard
"""

import argparse
import csv
import datetime
import hashlib
import json
import math
import os
import platform
import random
import re
import shlex
import shutil
import signal
import socket
import subprocess
import sys
import time
import traceback
from typing import Any, Dict, List, Optional, Set, Tuple

VERSION = "4.0.0-phd-frozen-definitive"

# ==============================================================================
# DEFINED REFERENCE & EXPERIMENTAL MATRIX (9 ORTHOGONAL VARIATIONS)
# ==============================================================================

DEFINED_REFERENCE_SYSCTLS = {
    "net.ipv4.tcp_sack": "1",
    "net.ipv4.tcp_dsack": "1",
    "net.ipv4.tcp_fack": "0",
    "net.ipv4.tcp_window_scaling": "1",
    "net.ipv4.tcp_timestamps": "1",
    "net.ipv4.tcp_congestion_control": "cubic",
    "net.core.default_qdisc": "fq_codel",
    "net.core.rmem_max": "16777216",
    "net.core.wmem_max": "16777216",
    "net.core.rmem_default": "212992",
    "net.core.wmem_default": "212992",
    "net.ipv4.tcp_rmem": "4096 131072 16777216",
    "net.ipv4.tcp_wmem": "4096 131072 16777216",
}

EXPERIMENTAL_VARIATIONS = [
    {
        "code": "V01_BASELINE_4M",
        "name": "Controlled Baseline (CUBIC + 4MiB BDP Window + fq_codel)",
        "category": "Baseline",
        "sysctls": {
            "net.ipv4.tcp_congestion_control": "cubic",
            "net.core.default_qdisc": "fq_codel",
            "net.ipv4.tcp_sack": "1",
            "net.core.rmem_max": "4194304",
            "net.core.wmem_max": "4194304",
            "net.ipv4.tcp_rmem": "4096 131072 4194304",
            "net.ipv4.tcp_wmem": "4096 131072 4194304",
        },
        "qdisc": "fq_codel",
        "cipher": "aes128-gcm@openssh.com",
        "compression": False,
        "compressible_payload": False,
        "control_code": None,
    },
    {
        "code": "V02_SACK_OFF_4M",
        "name": "Ablation: Selective ACK Disabled (tcp_sack=0 at 4MiB)",
        "category": "Reliability/SACK",
        "sysctls": {
            "net.ipv4.tcp_congestion_control": "cubic",
            "net.core.default_qdisc": "fq_codel",
            "net.ipv4.tcp_sack": "0",
            "net.core.rmem_max": "4194304",
            "net.core.wmem_max": "4194304",
            "net.ipv4.tcp_rmem": "4096 131072 4194304",
            "net.ipv4.tcp_wmem": "4096 131072 4194304",
        },
        "qdisc": "fq_codel",
        "cipher": "aes128-gcm@openssh.com",
        "compression": False,
        "compressible_payload": False,
        "control_code": "V01_BASELINE_4M",
    },
    {
        "code": "V03_BUF_16M",
        "name": "Buffer Scaling: 16 MiB Socket Window Limit (CUBIC + fq_codel + AES-GCM)",
        "category": "BDP Buffers",
        "sysctls": {
            "net.ipv4.tcp_congestion_control": "cubic",
            "net.core.default_qdisc": "fq_codel",
            "net.ipv4.tcp_sack": "1",
            "net.core.rmem_max": "16777216",
            "net.core.wmem_max": "16777216",
            "net.ipv4.tcp_rmem": "4096 131072 16777216",
            "net.ipv4.tcp_wmem": "4096 131072 16777216",
        },
        "qdisc": "fq_codel",
        "cipher": "aes128-gcm@openssh.com",
        "compression": False,
        "compressible_payload": False,
        "control_code": "V01_BASELINE_4M",
    },
    {
        "code": "V04_BUF_64M",
        "name": "Buffer Scaling: 64 MiB Socket Window Limit (CUBIC + fq_codel)",
        "category": "BDP Buffers",
        "sysctls": {
            "net.ipv4.tcp_congestion_control": "cubic",
            "net.core.default_qdisc": "fq_codel",
            "net.ipv4.tcp_sack": "1",
            "net.core.rmem_max": "67108864",
            "net.core.wmem_max": "67108864",
            "net.ipv4.tcp_rmem": "4096 131072 67108864",
            "net.ipv4.tcp_wmem": "4096 131072 67108864",
        },
        "qdisc": "fq_codel",
        "cipher": "aes128-gcm@openssh.com",
        "compression": False,
        "compressible_payload": False,
        "control_code": "V03_BUF_16M",
    },
    {
        "code": "V05_CUBIC_FQ_16M",
        "name": "Congestion Isolation: CUBIC Loss-Based + Fair Queueing (fq)",
        "category": "Congestion Control",
        "sysctls": {
            "net.ipv4.tcp_congestion_control": "cubic",
            "net.core.default_qdisc": "fq",
            "net.ipv4.tcp_sack": "1",
            "net.core.rmem_max": "16777216",
            "net.core.wmem_max": "16777216",
            "net.ipv4.tcp_rmem": "4096 131072 16777216",
            "net.ipv4.tcp_wmem": "4096 131072 16777216",
        },
        "qdisc": "fq",
        "cipher": "aes128-gcm@openssh.com",
        "compression": False,
        "compressible_payload": False,
        "control_code": "V03_BUF_16M",
    },
    {
        "code": "V06_BBR_FQ_16M",
        "name": "Congestion Isolation: BBR Model-Based + Fair Queueing (fq)",
        "category": "Congestion Control",
        "sysctls": {
            "net.ipv4.tcp_congestion_control": "bbr",
            "net.core.default_qdisc": "fq",
            "net.ipv4.tcp_sack": "1",
            "net.core.rmem_max": "16777216",
            "net.core.wmem_max": "16777216",
            "net.ipv4.tcp_rmem": "4096 131072 16777216",
            "net.ipv4.tcp_wmem": "4096 131072 16777216",
        },
        "qdisc": "fq",
        "cipher": "aes128-gcm@openssh.com",
        "compression": False,
        "compressible_payload": False,
        "control_code": "V05_CUBIC_FQ_16M",
    },
    {
        "code": "V08_CIPHER_CHACHA_16M",
        "name": "Cryptography Treatment: ChaCha20-Poly1305 Stream Cipher at 16MiB",
        "category": "Cryptography",
        "sysctls": {
            "net.ipv4.tcp_congestion_control": "cubic",
            "net.core.default_qdisc": "fq_codel",
            "net.ipv4.tcp_sack": "1",
            "net.core.rmem_max": "16777216",
            "net.core.wmem_max": "16777216",
            "net.ipv4.tcp_rmem": "4096 131072 16777216",
            "net.ipv4.tcp_wmem": "4096 131072 16777216",
        },
        "qdisc": "fq_codel",
        "cipher": "chacha20-poly1305@openssh.com",
        "compression": False,
        "compressible_payload": False,
        "control_code": "V03_BUF_16M",
    },
    {
        "code": "V09_COMP_RAW_16M",
        "name": "Compression Control: Raw Structured Log Stream (Uncompressed)",
        "category": "Data Reduction",
        "sysctls": {
            "net.ipv4.tcp_congestion_control": "cubic",
            "net.core.default_qdisc": "fq_codel",
            "net.ipv4.tcp_sack": "1",
            "net.core.rmem_max": "16777216",
            "net.core.wmem_max": "16777216",
            "net.ipv4.tcp_rmem": "4096 131072 16777216",
            "net.ipv4.tcp_wmem": "4096 131072 16777216",
        },
        "qdisc": "fq_codel",
        "cipher": "aes128-gcm@openssh.com",
        "compression": False,
        "compressible_payload": True,
        "control_code": None,
    },
    {
        "code": "V10_COMP_GZIP_16M",
        "name": "Compression Treatment: Stream Gzip Compression (Level 6)",
        "category": "Data Reduction",
        "sysctls": {
            "net.ipv4.tcp_congestion_control": "cubic",
            "net.core.default_qdisc": "fq_codel",
            "net.ipv4.tcp_sack": "1",
            "net.core.rmem_max": "16777216",
            "net.core.wmem_max": "16777216",
            "net.ipv4.tcp_rmem": "4096 131072 16777216",
            "net.ipv4.tcp_wmem": "4096 131072 16777216",
        },
        "qdisc": "fq_codel",
        "cipher": "aes128-gcm@openssh.com",
        "compression": True,
        "compressible_payload": True,
        "control_code": "V09_COMP_RAW_16M",
    },
]

# ==============================================================================
# UTILITIES & SYSTEM INTERACTIONS
# ==============================================================================

def normalize_whitespace(s: str) -> str:
    return " ".join(s.strip().split()) if s else ""


def run_local_cmd(cmd: str, check: bool = True) -> Tuple[int, str, str]:
    proc = subprocess.Popen(
        ["/bin/bash", "-c", cmd],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    stdout, stderr = proc.communicate()
    if check and proc.returncode != 0:
        raise RuntimeError(
            f"Local command failed (rc={proc.returncode}): {cmd}\nStderr: {stderr}"
        )
    return proc.returncode, stdout.strip(), stderr.strip()


def run_ssh_cmd(
    receiver_ip: str,
    receiver_port: int,
    receiver_user: str,
    ssh_key: str,
    known_hosts: str,
    cmd: str,
    check: bool = True,
    timeout: int = 45,
) -> Tuple[int, str, str]:
    ssh_cmd = (
        f"ssh -p {receiver_port} -o StrictHostKeyChecking=yes -o UserKnownHostsFile={shlex.quote(known_hosts)} "
        f"-o ConnectTimeout=10 -i {shlex.quote(ssh_key)} {receiver_user}@{receiver_ip} {shlex.quote(cmd)}"
    )
    proc = subprocess.Popen(
        ["/bin/bash", "-c", ssh_cmd],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        stdout, stderr = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        raise TimeoutError(f"SSH command timed out after {timeout}s: {cmd}")

    if check and proc.returncode != 0:
        raise RuntimeError(
            f"Remote SSH command failed on {receiver_ip}:{receiver_port} (rc={proc.returncode}): {cmd}\nStderr: {stderr}"
        )
    return proc.returncode, stdout.strip(), stderr.strip()


def get_interface_for_destination(destination: str) -> str:
    _, out, _ = run_local_cmd(f"ip route get {shlex.quote(destination)}")
    match = re.search(r"\bdev\s+(\S+)", out)
    if not match:
        raise RuntimeError(f"Could not identify route interface for {destination}: {out}")
    return match.group(1)


def get_local_sysctl(key: str) -> str:
    _, out, _ = run_local_cmd(f"sysctl -n {key}", check=True)
    return normalize_whitespace(out)


def set_local_sysctl(key: str, val: str) -> None:
    run_local_cmd(f"sysctl -w {key}='{val}'", check=True)
    readback = get_local_sysctl(key)
    if readback != normalize_whitespace(val):
        raise RuntimeError(
            f"Local sysctl verification failed for {key}. Expected '{val}', got '{readback}'"
        )


def get_remote_sysctl(
    receiver_ip: str, receiver_port: int, receiver_user: str, ssh_key: str, known_hosts: str, key: str
) -> str:
    _, out, _ = run_ssh_cmd(
        receiver_ip, receiver_port, receiver_user, ssh_key, known_hosts, f"sysctl -n {key}"
    )
    return normalize_whitespace(out)


def set_remote_sysctl(
    receiver_ip: str, receiver_port: int, receiver_user: str, ssh_key: str, known_hosts: str, key: str, val: str
) -> None:
    run_ssh_cmd(
        receiver_ip,
        receiver_port,
        receiver_user,
        ssh_key,
        known_hosts,
        f"sudo sysctl -w {key}='{val}'",
    )
    readback = get_remote_sysctl(receiver_ip, receiver_port, receiver_user, ssh_key, known_hosts, key)
    if readback != normalize_whitespace(val):
        raise RuntimeError(
            f"Remote sysctl verification failed for {key}. Expected '{val}', got '{readback}'"
        )


def get_interface_qdisc(iface: str) -> str:
    rc, out, _ = run_local_cmd(f"tc qdisc show dev {iface} root", check=False)
    if rc == 0 and "qdisc" in out:
        parts = out.split()
        if len(parts) >= 2:
            return parts[1]
    return "unknown"


def validate_qdisc_layout(iface: str) -> None:
    """Verifies a supported simple root qdisc whose type can be restored after the benchmark."""
    _, output, _ = run_local_cmd(f"tc qdisc show dev {shlex.quote(iface)}", check=True)
    root_lines = [line for line in output.splitlines() if re.search(r"\broot\b", line)]
    if len(root_lines) != 1:
        raise RuntimeError(
            f"Benchmark requires exactly one simple root qdisc on {iface}.\nObserved layout:\n{output}"
        )
    root_qdisc = get_interface_qdisc(iface)
    allowed = {"fq", "fq_codel", "pfifo_fast"}
    if root_qdisc not in allowed:
        raise RuntimeError(
            f"Unsupported initial root qdisc: '{root_qdisc}'. Use a clean environment with simple qdisc (fq, fq_codel, pfifo_fast)."
        )


def set_interface_qdisc(iface: str, qdisc: str) -> None:
    run_local_cmd(f"tc qdisc replace dev {iface} root {qdisc}", check=True)
    observed = get_interface_qdisc(iface)
    if observed != qdisc:
        raise RuntimeError(
            f"Qdisc application verification failed on {iface}. Expected '{qdisc}', observed '{observed}'"
        )


def compute_file_sha256(filepath: str, block_size: int = 1048576) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(block_size), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def compute_script_sha256() -> str:
    """Calculates SHA-256 hash of the executing Python script file."""
    return compute_file_sha256(os.path.abspath(__file__))


def pin_and_get_host_fingerprint(receiver_ip: str, receiver_port: int, known_hosts_path: str) -> str:
    run_local_cmd(f"ssh-keyscan -p {receiver_port} {receiver_ip} > {shlex.quote(known_hosts_path)}")
    _, fp_out, _ = run_local_cmd(f"ssh-keygen -lf {shlex.quote(known_hosts_path)} | awk '{{print $2}}'")
    fp = fp_out.strip()
    if not fp:
        raise RuntimeError(f"Failed to generate host key fingerprint from {known_hosts_path}")
    return fp


def read_local_proc_stat_cpu() -> Tuple[int, int]:
    with open("/proc/stat", "r") as f:
        line = f.readline()
    fields = [int(x) for x in line.split()[1:]]
    idle = fields[3] + fields[4]
    total = sum(fields)
    return total, idle


def read_remote_proc_stat_cpu(
    receiver_ip: str, receiver_port: int, receiver_user: str, ssh_key: str, known_hosts: str
) -> Tuple[int, int]:
    _, out, _ = run_ssh_cmd(
        receiver_ip, receiver_port, receiver_user, ssh_key, known_hosts, "head -n 1 /proc/stat"
    )
    fields = [int(x) for x in out.split()[1:]]
    idle = fields[3] + fields[4]
    total = sum(fields)
    return total, idle


# ==============================================================================
# CONSERVATIVE STATISTICAL ENGINE
# ==============================================================================

def compute_conservative_t_critical(df: int) -> float:
    t_table = {
        1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571,
        6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228,
        15: 2.131, 20: 2.086, 25: 2.060, 30: 2.042, 40: 2.021,
        60: 2.000, 120: 1.980,
    }
    eligible = [key for key in t_table if key <= df]
    if eligible:
        return t_table[max(eligible)]
    return t_table[1]


def compute_statistics(values: List[float]) -> Dict[str, float]:
    n = len(values)
    if n == 0:
        return {"n": 0, "mean": 0.0, "std": 0.0, "ci95_low": 0.0, "ci95_high": 0.0, "median": 0.0}

    mean = sum(values) / n
    variance = sum((x - mean) ** 2 for x in values) / (n - 1) if n > 1 else 0.0
    std = math.sqrt(variance)
    sorted_vals = sorted(values)
    median = (
        sorted_vals[n // 2]
        if n % 2 == 1
        else (sorted_vals[n // 2 - 1] + sorted_vals[n // 2]) / 2.0
    )

    if n > 1:
        t_crit = compute_conservative_t_critical(n - 1)
        sem = std / math.sqrt(n)
        ci_half = t_crit * sem
    else:
        ci_half = 0.0

    return {
        "n": n,
        "mean": mean,
        "std": std,
        "median": median,
        "ci95_low": mean - ci_half,
        "ci95_high": mean + ci_half,
    }


# ==============================================================================
# MAIN BENCHMARK ORCHESTRATOR
# ==============================================================================

class TCPPhDOrchestrator:
    def __init__(
        self,
        receiver_ip: str,
        receiver_port: int,
        receiver_user: str,
        ssh_key: str,
        size_gib: int,
        blocks: int,
        output_dir: str,
        seed: int,
        resume_dir: Optional[str] = None,
    ):
        self.receiver_ip = receiver_ip
        self.receiver_port = receiver_port
        self.receiver_user = receiver_user
        self.ssh_key = ssh_key
        self.size_gib = size_gib
        self.blocks = blocks
        self.seed = seed
        self.is_resume = resume_dir is not None

        if self.is_resume:
            self.campaign_dir = os.path.abspath(resume_dir)  # type: ignore
            manifest_file = os.path.join(self.campaign_dir, "experiment_manifest.json")
            if not os.path.exists(manifest_file):
                raise RuntimeError(f"Cannot resume: {manifest_file} missing.")
            with open(manifest_file, "r") as f:
                manifest = json.load(f)
            self.timestamp = manifest["timestamp_utc"]
            self.size_gib = manifest["payload_size_gib"]
            self.blocks = manifest["blocks"]
            self.seed = manifest["seed"]
            self.receiver_ip = manifest["receiver"]["receiver_ip"]
            self.receiver_port = manifest["receiver"]["receiver_port"]
            self.receiver_user = manifest["receiver"]["receiver_user"]
        else:
            self.timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d_%H%M%SZ")
            self.route = f"sender_to_{receiver_ip.replace('.', '_')}_{receiver_port}"
            self.campaign_dir = os.path.join(
                output_dir, f"{self.timestamp}_{self.route}_{size_gib}gib_seed{seed}"
            )

        self.known_hosts_file = os.path.join(self.campaign_dir, "known_hosts")
        self.iface = get_interface_for_destination(self.receiver_ip)
        self.raw_socket_dir = os.path.join(self.campaign_dir, "raw_socket_samples")
        self.remote_dest_dir = "/tmp/tcp_benchmark_dest"

        self.observed_sender_state: Dict[str, str] = {}
        self.observed_receiver_state: Dict[str, str] = {}
        self.initial_qdisc = "unknown"
        self.host_key_fingerprint = ""
        self.execution_plan: List[Dict[str, Any]] = []

    def preflight_validations(self) -> None:
        """Rigorous system, network, and environmental validation."""
        print("[*] Running Preflight System Validations...")

        if os.geteuid() != 0:
            raise PermissionError("Benchmark requires root privileges for sysctl and tc.")

        if not os.path.isfile(self.ssh_key):
            raise FileNotFoundError(f"SSH private key not found at {self.ssh_key}")

        run_local_cmd("modprobe sch_fq sch_fq_codel tcp_bbr", check=False)
        _, avail_cc, _ = run_local_cmd("sysctl -n net.ipv4.tcp_available_congestion_control")
        if "bbr" not in avail_cc or "cubic" not in avail_cc:
            raise RuntimeError(f"Required CC (bbr, cubic) missing from kernel: {avail_cc}")

        validate_qdisc_layout(self.iface)

        _, existing_ssh, _ = run_local_cmd(
            f"ss -Htn dst {shlex.quote(self.receiver_ip)}:{self.receiver_port}", check=False
        )
        if existing_ssh.strip():
            raise RuntimeError(
                f"Active concurrent SSH connection to {self.receiver_ip}:{self.receiver_port} detected. "
                "Abort to prevent telemetry contamination."
            )

        required_space_bytes = (self.size_gib * 1024**3) * 3
        sender_stat = shutil.disk_usage("/tmp")
        if sender_stat.free < required_space_bytes:
            raise RuntimeError(
                f"Insufficient space on /tmp on sender. Need {required_space_bytes/(1024**3):.1f} GiB, free: {sender_stat.free/(1024**3):.1f} GiB"
            )

        os.makedirs(self.campaign_dir, exist_ok=True)
        os.makedirs(self.raw_socket_dir, exist_ok=True)

        if not self.is_resume:
            self.host_key_fingerprint = pin_and_get_host_fingerprint(
                self.receiver_ip, self.receiver_port, self.known_hosts_file
            )
        else:
            manifest_file = os.path.join(self.campaign_dir, "experiment_manifest.json")
            with open(manifest_file, "r") as f:
                manifest = json.load(f)

            current_script_sha = compute_script_sha256()
            expected_script_sha = manifest["script_sha256"]
            if current_script_sha != expected_script_sha:
                raise RuntimeError(
                    f"Benchmark script SHA-256 mismatch! Expected: {expected_script_sha}, Found: {current_script_sha}. "
                    "Resume aborted to preserve provenance."
                )
            print("    [+] Verified benchmark script provenance SHA-256.")

            expected_fp = manifest["receiver"]["receiver_host_key_fingerprint"]
            _, current_fp_out, _ = run_local_cmd(
                f"ssh-keygen -lf {shlex.quote(self.known_hosts_file)} | awk '{{print $2}}'"
            )
            self.host_key_fingerprint = current_fp_out.strip()
            if self.host_key_fingerprint != expected_fp:
                raise RuntimeError(
                    f"Receiver host-key fingerprint mismatch on resume! Expected: {expected_fp}, Found: {self.host_key_fingerprint}"
                )
            print("    [+] Verified pinned host-key fingerprint matches manifest.")

        run_ssh_cmd(
            self.receiver_ip,
            self.receiver_port,
            self.receiver_user,
            self.ssh_key,
            self.known_hosts_file,
            f"mkdir -p {shlex.quote(self.remote_dest_dir)}",
        )

        _, free_output, _ = run_ssh_cmd(
            self.receiver_ip,
            self.receiver_port,
            self.receiver_user,
            self.ssh_key,
            self.known_hosts_file,
            f"df -B1 --output=avail {shlex.quote(self.remote_dest_dir)} | tail -n 1",
        )
        remote_free = int(free_output.strip())
        receiver_required = self.size_gib * 1024**3 + 2 * 1024**3
        if remote_free < receiver_required:
            raise RuntimeError(
                f"Insufficient receiver disk space on {self.remote_dest_dir}. Free: {remote_free/(1024**3):.1f} GiB, Need: {receiver_required/(1024**3):.1f} GiB"
            )

        _, rec_avail_cc, _ = run_ssh_cmd(
            self.receiver_ip,
            self.receiver_port,
            self.receiver_user,
            self.ssh_key,
            self.known_hosts_file,
            "sysctl -n net.ipv4.tcp_available_congestion_control",
        )
        if "bbr" not in rec_avail_cc or "cubic" not in rec_avail_cc:
            raise RuntimeError(f"Receiver missing required CC algorithms (bbr, cubic): {rec_avail_cc}")

    def capture_or_load_observed_state(self) -> None:
        """Safely loads or captures baseline state without overwriting on resume."""
        sender_state_file = os.path.join(self.campaign_dir, "observed_sender_state.json")
        receiver_state_file = os.path.join(self.campaign_dir, "observed_receiver_state.json")

        if self.is_resume:
            print("[*] Loading original baseline states from campaign directory...")
            with open(sender_state_file, "r") as f:
                self.observed_sender_state = json.load(f)
            with open(receiver_state_file, "r") as f:
                self.observed_receiver_state = json.load(f)
            self.initial_qdisc = self.observed_sender_state["root_qdisc"]
        else:
            print("[*] Capturing pre-benchmark observed system baselines...")
            self.initial_qdisc = get_interface_qdisc(self.iface)
            for k in DEFINED_REFERENCE_SYSCTLS.keys():
                self.observed_sender_state[k] = get_local_sysctl(k)
            self.observed_sender_state["root_qdisc"] = self.initial_qdisc

            with open(sender_state_file, "w") as f:
                json.dump(self.observed_sender_state, f, indent=2)

            for k in DEFINED_REFERENCE_SYSCTLS.keys():
                if not k.startswith("net.core.default_qdisc"):
                    self.observed_receiver_state[k] = get_remote_sysctl(
                        self.receiver_ip, self.receiver_port, self.receiver_user, self.ssh_key, self.known_hosts_file, k
                    )

            with open(receiver_state_file, "w") as f:
                json.dump(self.observed_receiver_state, f, indent=2)

    def generate_and_verify_payloads(self) -> Tuple[str, str, str, str]:
        """Generates payloads and computes/validates SHA-256 digests."""
        payload_dir = "/tmp/tcp_benchmark_payloads"
        os.makedirs(payload_dir, exist_ok=True)
        raw_file = os.path.join(payload_dir, f"payload_raw_{self.size_gib}g.dat")
        comp_file = os.path.join(payload_dir, f"payload_comp_{self.size_gib}g.dat")

        expected_bytes = self.size_gib * 1024**3

        if not os.path.exists(raw_file) or os.path.getsize(raw_file) != expected_bytes:
            print(f"[*] Generating {self.size_gib} GiB high-entropy random payload...")
            run_local_cmd(
                f"dd if=/dev/urandom of={raw_file} bs=1G count={self.size_gib} status=none"
            )

        if not os.path.exists(comp_file) or os.path.getsize(comp_file) != expected_bytes:
            print(f"[*] Generating {self.size_gib} GiB structured compressible log payload...")
            pattern = (
                "2026-03-31T12:00:00.000Z INFO [TCPBench] Transaction-ID=0xDEADBEEF "
                "status=SUCCESS payload=structured_log_simulation_padding_for_compression\n"
            )
            pattern_bytes = (pattern * 1000).encode("utf-8")
            written = 0
            with open(comp_file, "wb") as output:
                while written < expected_bytes:
                    chunk = min(len(pattern_bytes), expected_bytes - written)
                    output.write(pattern_bytes[:chunk])
                    written += chunk

        print("[*] Computing cryptographic SHA-256 digests for payloads...")
        sha_rand = compute_file_sha256(raw_file)
        sha_comp = compute_file_sha256(comp_file)

        manifest_file = os.path.join(self.campaign_dir, "experiment_manifest.json")

        if self.is_resume:
            with open(manifest_file, "r") as f:
                manifest = json.load(f)
            expected_rand = manifest["payloads"]["high_entropy"]["sha256"]
            expected_comp = manifest["payloads"]["compressible"]["sha256"]

            if sha_rand != expected_rand:
                raise RuntimeError(
                    f"High-entropy payload SHA-256 mismatch! Expected: {expected_rand}, Found: {sha_rand}. Resume aborted."
                )
            if sha_comp != expected_comp:
                raise RuntimeError(
                    f"Compressible payload SHA-256 mismatch! Expected: {expected_comp}, Found: {sha_comp}. Resume aborted."
                )
            print("    [+] Verified high-entropy and compressible payload hashes match manifest.")

        return raw_file, comp_file, sha_rand, sha_comp

    def build_or_load_execution_plan(self, sha_rand: str, sha_comp: str) -> List[Dict[str, Any]]:
        """Persists and verifies deterministic randomized execution plan against immutable manifest."""
        plan_file = os.path.join(self.campaign_dir, "execution_plan.json")
        sha_file = os.path.join(self.campaign_dir, "execution_plan_sha256.txt")
        manifest_file = os.path.join(self.campaign_dir, "experiment_manifest.json")

        if self.is_resume and os.path.exists(plan_file):
            print("[*] Loading and verifying execution plan against immutable manifest...")
            with open(plan_file, "rb") as f:
                current_plan_sha = hashlib.sha256(f.read()).hexdigest()

            with open(manifest_file, "r") as f:
                manifest = json.load(f)

            expected_manifest_sha = manifest["execution_plan_sha256"]
            if current_plan_sha != expected_manifest_sha:
                raise RuntimeError(
                    "Execution-plan hash differs from the immutable campaign manifest! Resume aborted."
                )

            with open(plan_file, "r") as f:
                plan_data = json.load(f)
            self.execution_plan = plan_data["plan"]
            print("    [+] Verified execution plan cryptographic integrity against manifest.")
        else:
            print("[*] Generating randomized block execution plan...")
            rng = random.Random(self.seed)
            plan = []
            for b in range(1, self.blocks + 1):
                block_vars = [v["code"] for v in EXPERIMENTAL_VARIATIONS]
                rng.shuffle(block_vars)
                for order_idx, code in enumerate(block_vars, 1):
                    plan.append({"block_id": b, "order_in_block": order_idx, "variation_code": code})
            self.execution_plan = plan
            plan_str = json.dumps({"seed": self.seed, "blocks": self.blocks, "plan": plan}, indent=2)
            plan_sha = hashlib.sha256(plan_str.encode("utf-8")).hexdigest()

            with open(plan_file, "w") as f:
                f.write(plan_str)
            with open(sha_file, "w") as f:
                f.write(plan_sha + "\n")

            manifest_data = {
                "version": VERSION,
                "script_sha256": compute_script_sha256(),
                "timestamp_utc": self.timestamp,
                "strategy": "Observed state capture, defined reference specification, and controlled experimental baseline",
                "sender_hostname": socket.gethostname(),
                "sender_kernel": platform.release(),
                "receiver": {
                    "receiver_ip": self.receiver_ip,
                    "receiver_port": self.receiver_port,
                    "receiver_user": self.receiver_user,
                    "receiver_host_key_fingerprint": self.host_key_fingerprint,
                },
                "payload_size_gib": self.size_gib,
                "destination_sha_verification_policy": "Full SHA-256 for size <= 1 GiB; Block 1 SHA-256 for size > 1 GiB; exact size verification on all iterations",
                "payloads": {
                    "high_entropy": {
                        "path": f"/tmp/tcp_benchmark_payloads/payload_raw_{self.size_gib}g.dat",
                        "size_bytes": self.size_gib * 1024**3,
                        "sha256": sha_rand,
                    },
                    "compressible": {
                        "path": f"/tmp/tcp_benchmark_payloads/payload_comp_{self.size_gib}g.dat",
                        "size_bytes": self.size_gib * 1024**3,
                        "sha256": sha_comp,
                    },
                },
                "execution_plan_sha256": plan_sha,
                "blocks": self.blocks,
                "seed": self.seed,
                "interface": self.iface,
                "initial_qdisc": self.initial_qdisc,
            }
            with open(manifest_file, "w") as f:
                json.dump(manifest_data, f, indent=2)

        return self.execution_plan

    def restore_system_state(self) -> Dict[str, Any]:
        """Fault-tolerant two-sided state restoration with guaranteed report generation."""
        print("\n[*] Restoring sender & receiver system configurations...")
        restoration_log: Dict[str, Any] = {
            "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "status": "RESTORE_VERIFIED",
            "qdisc_restoration_policy": "ROOT_QDISC_TYPE_RESTORED",
            "sender_checks": {},
            "receiver_checks": {},
            "errors": [],
        }

        # Sender Qdisc Restoration
        try:
            set_interface_qdisc(self.iface, self.observed_sender_state["root_qdisc"])
            cur_q = get_interface_qdisc(self.iface)
            restoration_log["sender_checks"]["root_qdisc"] = {
                "expected": self.observed_sender_state["root_qdisc"],
                "observed": cur_q,
                "match": cur_q == self.observed_sender_state["root_qdisc"],
            }
            if cur_q != self.observed_sender_state["root_qdisc"]:
                restoration_log["status"] = "RESTORE_FAILED"
        except Exception as exc:
            restoration_log["status"] = "RESTORE_FAILED"
            restoration_log["errors"].append(f"Sender root_qdisc restoration error: {exc}")

        # Sender Sysctls Restoration
        for k, v in self.observed_sender_state.items():
            if k == "root_qdisc":
                continue
            try:
                set_local_sysctl(k, v)
                cur_v = get_local_sysctl(k)
                matched = cur_v == normalize_whitespace(v)
                restoration_log["sender_checks"][k] = {"expected": v, "observed": cur_v, "match": matched}
                if not matched:
                    restoration_log["status"] = "RESTORE_FAILED"
            except Exception as exc:
                restoration_log["status"] = "RESTORE_FAILED"
                restoration_log["errors"].append(f"Sender {k} restoration error: {exc}")

        # Receiver Sysctls Restoration
        for k, v in self.observed_receiver_state.items():
            try:
                set_remote_sysctl(
                    self.receiver_ip, self.receiver_port, self.receiver_user, self.ssh_key, self.known_hosts_file, k, v
                )
                cur_rv = get_remote_sysctl(
                    self.receiver_ip, self.receiver_port, self.receiver_user, self.ssh_key, self.known_hosts_file, k
                )
                matched = cur_rv == normalize_whitespace(v)
                restoration_log["receiver_checks"][k] = {"expected": v, "observed": cur_rv, "match": matched}
                if not matched:
                    restoration_log["status"] = "RESTORE_FAILED"
            except Exception as exc:
                restoration_log["status"] = "RESTORE_FAILED"
                restoration_log["errors"].append(f"Receiver {k} restoration error: {exc}")

        report_path = os.path.join(self.campaign_dir, "restoration_report.json")
        with open(report_path, "w") as f:
            json.dump(restoration_log, f, indent=2)

        print(f"[*] Restoration complete. Final status: {restoration_log['status']}")
        return restoration_log

    def run_campaign(self) -> None:
        """Executes experimental plan with active telemetry and destination verification."""
        raw_payload, comp_payload, sha_rand, sha_comp = self.generate_and_verify_payloads()
        plan = self.build_or_load_execution_plan(sha_rand, sha_comp)

        iterations_csv = os.path.join(self.campaign_dir, "iterations.csv")
        csv_headers = [
            "block_id",
            "order_in_block",
            "variation_code",
            "variation_name",
            "category",
            "validation_status",
            "checksum_status",
            "duration_sec",
            "application_goodput_mbps",
            "expected_bytes",
            "received_bytes",
            "sender_host_cpu_pct",
            "receiver_host_cpu_pct",
            "observed_cc",
            "rtt_avg_ms",
            "rtt_min_ms",
            "rtt_max_ms",
            "retrans_total_observed",
            "retrans_delta",
            "cwnd_final",
            "mss",
        ]

        completed_cells: Set[Tuple[int, str]] = set()
        if self.is_resume and os.path.exists(iterations_csv):
            with open(iterations_csv, "r", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row["validation_status"] in ("VALID_SIZE_VERIFIED", "VALID_CHECKSUM_VERIFIED"):
                        completed_cells.add((int(row["block_id"]), row["variation_code"]))

        file_mode = "a" if self.is_resume and os.path.exists(iterations_csv) else "w"
        var_lookup = {v["code"]: v for v in EXPERIMENTAL_VARIATIONS}

        with open(iterations_csv, file_mode, newline="") as csv_file:
            writer = csv.writer(csv_file)
            if file_mode == "w":
                writer.writerow(csv_headers)

            for step in plan:
                b = step["block_id"]
                order_idx = step["order_in_block"]
                code = step["variation_code"]
                var = var_lookup[code]

                if (b, code) in completed_cells:
                    print(f"[*] Skipping completed verified cell: Block {b} | {code}")
                    continue

                print(f"\n=======================================================")
                print(f" EXECUTION: Block {b}/{self.blocks} | Step {order_idx} | {code}")
                print(f" {var['name']}")
                print(f"=======================================================")

                # Apply Sender State
                for sk, sv in var["sysctls"].items():
                    set_local_sysctl(sk, sv)
                set_interface_qdisc(self.iface, var["qdisc"])

                # Apply Receiver State
                for sk, sv in var["sysctls"].items():
                    if not sk.startswith("net.core.default_qdisc"):
                        set_remote_sysctl(
                            self.receiver_ip, self.receiver_port, self.receiver_user, self.ssh_key, self.known_hosts_file, sk, sv
                        )

                time.sleep(2)

                payload_file = comp_payload if var["compressible_payload"] else raw_payload
                expected_bytes = os.path.getsize(payload_file)
                dest_file = f"{self.remote_dest_dir}/b{b}_{code}.dat"
                quoted_dest = shlex.quote(dest_file)

                # Construct Pipeline
                if var["compression"]:
                    sender_cmd = f"gzip -c {payload_file}"
                    receiver_cmd = (
                        f"ssh -p {self.receiver_port} -o StrictHostKeyChecking=yes -o UserKnownHostsFile={shlex.quote(self.known_hosts_file)} "
                        f"-c {var['cipher']} -i {shlex.quote(self.ssh_key)} {self.receiver_user}@{self.receiver_ip} "
                        f"'gzip -d > {quoted_dest}'"
                    )
                else:
                    sender_cmd = f"cat {payload_file}"
                    receiver_cmd = (
                        f"ssh -p {self.receiver_port} -o StrictHostKeyChecking=yes -o UserKnownHostsFile={shlex.quote(self.known_hosts_file)} "
                        f"-c {var['cipher']} -i {shlex.quote(self.ssh_key)} {self.receiver_user}@{self.receiver_ip} "
                        f"'cat > {quoted_dest}'"
                    )

                pipeline = f"set -o pipefail; {sender_cmd} | {receiver_cmd}"
                sample_file = os.path.join(self.raw_socket_dir, f"b{b}_{code}_ss.txt")

                s_cpu_tot_0, s_cpu_idle_0 = read_local_proc_stat_cpu()
                r_cpu_tot_0, r_cpu_idle_0 = read_remote_proc_stat_cpu(
                    self.receiver_ip, self.receiver_port, self.receiver_user, self.ssh_key, self.known_hosts_file
                )
                start_time = time.perf_counter()

                proc = subprocess.Popen(
                    ["/bin/bash", "-c", pipeline],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )

                rtt_samples: List[float] = []
                retrans_samples: List[int] = []
                cwnd_samples: List[int] = []
                observed_cc_list: List[str] = []
                mss_val = 1448

                with open(sample_file, "w") as sf:
                    while proc.poll() is None:
                        rc, out, _ = run_local_cmd(
                            f"ss -tin dst {self.receiver_ip}:{self.receiver_port}", check=False
                        )
                        if out:
                            sf.write(out + "\n---\n")
                            for line in out.splitlines():
                                m_cc = re.match(r"^\s*(cubic|bbr|reno|dctcp)\b", line)
                                if m_cc:
                                    observed_cc_list.append(m_cc.group(1))

                            m_rtt = re.search(r"rtt:([\d\.]+)/([\d\.]+)", out)
                            if m_rtt:
                                rtt_samples.append(float(m_rtt.group(1)))
                            m_cwnd = re.search(r"cwnd:(\d+)", out)
                            if m_cwnd:
                                cwnd_samples.append(int(m_cwnd.group(1)))
                            m_mss = re.search(r"mss:(\d+)", out)
                            if m_mss:
                                m_mss_v = int(m_mss.group(1))
                                if m_mss_v > 0:
                                    mss_val = m_mss_v
                            m_retrans = re.search(r"retrans:\d+/(\d+)", out)
                            if m_retrans:
                                retrans_samples.append(int(m_retrans.group(1)))
                        time.sleep(0.5)

                _, stderr = proc.communicate()
                end_time = time.perf_counter()

                s_cpu_tot_1, s_cpu_idle_1 = read_local_proc_stat_cpu()
                r_cpu_tot_1, r_cpu_idle_1 = read_remote_proc_stat_cpu(
                    self.receiver_ip, self.receiver_port, self.receiver_user, self.ssh_key, self.known_hosts_file
                )

                duration = max(end_time - start_time, 0.001)

                dest_size = 0
                checksum_status = "UNCHECKED"
                validation_status = "UNKNOWN"

                if proc.returncode != 0:
                    validation_status = "TRANSFER_FAILED"
                else:
                    _, size_out, _ = run_ssh_cmd(
                        self.receiver_ip, self.receiver_port, self.receiver_user, self.ssh_key, self.known_hosts_file,
                        f"stat -c %s {quoted_dest}", check=False
                    )
                    try:
                        dest_size = int(size_out.strip())
                    except ValueError:
                        dest_size = -1

                    if dest_size != expected_bytes:
                        validation_status = "SIZE_MISMATCH"
                    else:
                        validation_status = "VALID_SIZE_VERIFIED"
                        if self.size_gib <= 1 or b == 1:
                            _, remote_sha_out, _ = run_ssh_cmd(
                                self.receiver_ip, self.receiver_port, self.receiver_user, self.ssh_key, self.known_hosts_file,
                                f"sha256sum {quoted_dest} | awk '{{print $1}}'", check=False, timeout=600
                            )
                            expected_sha = compute_file_sha256(payload_file)
                            if remote_sha_out.strip() == expected_sha:
                                checksum_status = "CHECKSUM_MATCH"
                                validation_status = "VALID_CHECKSUM_VERIFIED"
                            else:
                                checksum_status = "CHECKSUM_MISMATCH"
                                validation_status = "CHECKSUM_MISMATCH"

                run_ssh_cmd(
                    self.receiver_ip, self.receiver_port, self.receiver_user, self.ssh_key, self.known_hosts_file,
                    f"rm -f {quoted_dest}", check=False
                )

                content_valid = validation_status in {"VALID_SIZE_VERIFIED", "VALID_CHECKSUM_VERIFIED"}
                observed_cc_set = set(observed_cc_list)

                if not observed_cc_set:
                    observed_cc = "NONE"
                    if content_valid:
                        validation_status = "TELEMETRY_MISSING"
                elif len(observed_cc_set) == 1:
                    observed_cc = next(iter(observed_cc_set))
                    expected_cc = var["sysctls"]["net.ipv4.tcp_congestion_control"]
                    if content_valid and observed_cc != expected_cc:
                        validation_status = "CC_MISMATCH"
                else:
                    observed_cc = "MULTIPLE:" + ",".join(sorted(observed_cc_set))
                    if content_valid:
                        validation_status = "CC_MISMATCH"

                goodput_mbps = (expected_bytes * 8.0) / (duration * 1_000_000.0) if duration > 0 else 0.0

                s_tot = s_cpu_tot_1 - s_cpu_tot_0
                s_idl = s_cpu_idle_1 - s_cpu_idle_0
                sender_cpu_pct = (1.0 - (s_idl / s_tot)) * 100.0 if s_tot > 0 else 0.0

                r_tot = r_cpu_tot_1 - r_cpu_tot_0
                r_idl = r_cpu_idle_1 - r_cpu_idle_0
                receiver_cpu_pct = (1.0 - (r_idl / r_tot)) * 100.0 if r_tot > 0 else 0.0

                rtt_avg = sum(rtt_samples) / len(rtt_samples) if rtt_samples else 0.0
                rtt_min = min(rtt_samples) if rtt_samples else 0.0
                rtt_max = max(rtt_samples) if rtt_samples else 0.0

                retrans_total = max(retrans_samples) if retrans_samples else 0
                retrans_delta = (retrans_samples[-1] - retrans_samples[0]) if len(retrans_samples) >= 2 else 0
                cwnd = cwnd_samples[-1] if cwnd_samples else 0

                row = [
                    b,
                    order_idx,
                    code,
                    var["name"],
                    var["category"],
                    validation_status,
                    checksum_status,
                    round(duration, 3),
                    round(goodput_mbps, 2),
                    expected_bytes,
                    dest_size,
                    round(sender_cpu_pct, 2),
                    round(receiver_cpu_pct, 2),
                    observed_cc,
                    round(rtt_avg, 2),
                    round(rtt_min, 2),
                    round(rtt_max, 2),
                    retrans_total,
                    retrans_delta,
                    cwnd,
                    mss_val,
                ]
                writer.writerow(row)
                csv_file.flush()

                print(
                    f"    [+] Status: {validation_status} | CC: {observed_cc} | Duration: {duration:.2f}s | "
                    f"Goodput: {goodput_mbps:.2f} Mbps | Sender CPU: {sender_cpu_pct:.1f}% | Receiver CPU: {receiver_cpu_pct:.1f}%"
                )

        self.generate_academic_reports()

    def generate_academic_reports(self) -> None:
        """Matched-control paired inferential statistics and academic reporting."""
        print("\n[*] Synthesizing Matched-Control Inferential Statistics...")
        iterations_csv = os.path.join(self.campaign_dir, "iterations.csv")
        summary_file = os.path.join(self.campaign_dir, "summary.csv")
        inference_file = os.path.join(self.campaign_dir, "paired_inference.csv")
        report_file = os.path.join(self.campaign_dir, "report.md")

        records: List[Dict[str, Any]] = []
        if os.path.exists(iterations_csv):
            with open(iterations_csv, "r", newline="") as f:
                for r in csv.DictReader(f):
                    if r["validation_status"] in ("VALID_SIZE_VERIFIED", "VALID_CHECKSUM_VERIFIED"):
                        records.append(r)

        grouped: Dict[str, Dict[int, float]] = {}
        for r in records:
            b = int(r["block_id"])
            c = r["variation_code"]
            grouped.setdefault(c, {})[b] = float(r["application_goodput_mbps"])

        # Write summary.csv
        with open(summary_file, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["variation_code", "n", "mean_goodput_mbps", "std_mbps", "median_goodput_mbps", "ci95_low", "ci95_high"])
            for var in EXPERIMENTAL_VARIATIONS:
                code = var["code"]
                vals = list(grouped.get(code, {}).values())
                st = compute_statistics(vals)
                w.writerow([code, st["n"], round(st["mean"], 2), round(st["std"], 2), round(st["median"], 2), round(st["ci95_low"], 2), round(st["ci95_high"], 2)])

        # Write paired_inference.csv
        with open(inference_file, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow([
                "treatment_code",
                "control_code",
                "hypothesis_test",
                "n_pairs",
                "paired_mean_diff_mbps",
                "ci95_low",
                "ci95_high",
                "pct_gain",
            ])

            for var in EXPERIMENTAL_VARIATIONS:
                ctrl_code = var["control_code"]
                if not ctrl_code or ctrl_code not in grouped or var["code"] not in grouped:
                    continue

                t_dict = grouped[var["code"]]
                c_dict = grouped[ctrl_code]
                common_blocks = sorted(set(t_dict.keys()) & set(c_dict.keys()))

                diffs = [t_dict[b] - c_dict[b] for b in common_blocks]
                st = compute_statistics(diffs)
                c_vals = [c_dict[b] for b in common_blocks]
                c_mean = sum(c_vals) / len(c_vals) if c_vals else 1.0
                pct_gain = (st["mean"] / c_mean) * 100.0

                w.writerow([
                    var["code"],
                    ctrl_code,
                    f"{var['code']} vs {ctrl_code}",
                    st["n"],
                    round(st["mean"], 2),
                    round(st["ci95_low"], 2),
                    round(st["ci95_high"], 2),
                    round(pct_gain, 2),
                ])

        # Write Academic Markdown Report
        with open(report_file, "w") as f:
            f.write("# Cross-Datacenter TCP Optimization Benchmark Report\n\n")
            f.write(f"**Campaign Identifier**: `{os.path.basename(self.campaign_dir)}`  \n")
            f.write(f"**Timestamp UTC**: `{self.timestamp}`  \n")
            f.write(f"**Payload Size**: `{self.size_gib} GiB` | **Blocks**: `{self.blocks}` | **Seed**: `{self.seed}`  \n\n")
            f.write("## 1. Summary Statistics (Application Goodput Mbps, Conservative 95% CI)\n\n")
            f.write("| Variation Code | N | Mean (Mbps) | Std Dev | Median | 95% CI |\n")
            f.write("| :--- | :--- | :--- | :--- | :--- | :--- |\n")
            for var in EXPERIMENTAL_VARIATIONS:
                code = var["code"]
                vals = list(grouped.get(code, {}).values())
                st = compute_statistics(vals)
                f.write(f"| `{code}` | {st['n']} | {st['mean']:.2f} | {st['std']:.2f} | {st['median']:.2f} | [{st['ci95_low']:.2f}, {st['ci95_high']:.2f}] |\n")

    def generate_campaign_audit(self, restoration_status: str) -> None:
        """Campaign completeness and exact expected-cell verification audit."""
        iterations_csv = os.path.join(self.campaign_dir, "iterations.csv")
        verified_cells: Set[Tuple[int, str]] = set()
        failed_cells: List[Dict[str, Any]] = []

        if os.path.exists(iterations_csv):
            with open(iterations_csv, "r") as f:
                for r in csv.DictReader(f):
                    cell = (int(r["block_id"]), r["variation_code"])
                    if r["validation_status"] in ("VALID_SIZE_VERIFIED", "VALID_CHECKSUM_VERIFIED"):
                        verified_cells.add(cell)
                    else:
                        failed_cells.append({"cell": cell, "status": r["validation_status"]})

        expected_cells = {
            (int(step["block_id"]), step["variation_code"])
            for step in self.execution_plan
        }

        missing_cells = sorted(expected_cells - verified_cells)
        unexpected_cells = sorted(verified_cells - expected_cells)

        is_complete = (
            not missing_cells
            and not unexpected_cells
            and restoration_status == "RESTORE_VERIFIED"
        )

        audit_data = {
            "version": VERSION,
            "campaign_id": os.path.basename(self.campaign_dir),
            "total_expected_cells": len(expected_cells),
            "unique_verified_cells": len(verified_cells),
            "restoration_status": restoration_status,
            "is_complete": is_complete,
            "missing_experimental_cells": [f"Block {b}: {c}" for b, c in missing_cells],
            "unexpected_experimental_cells": [f"Block {b}: {c}" for b, c in unexpected_cells],
            "failed_attempts_count": len(failed_cells),
            "failed_attempts": failed_cells,
        }

        with open(os.path.join(self.campaign_dir, "campaign_audit.json"), "w") as f:
            json.dump(audit_data, f, indent=2)
        print(f"[*] Campaign Audit written: {len(verified_cells)}/{len(expected_cells)} verified | Complete: {is_complete} | Restoration: {restoration_status}")


# ==============================================================================
# ALWAYS-INTERACTIVE CONFIGURATION PROMPTS
# ==============================================================================

def prompt_user_parameters() -> Dict[str, Any]:
    """Always prompts the user for all campaign parameters."""
    print("\n" + "=" * 68)
    print("  TCP PhD Cross-Datacenter Benchmark Suite Configuration Wizard")
    print(f"  Version: {VERSION}")
    print("=" * 68)
    print("Press [Enter] on any prompt to accept the default value shown in brackets.\n")

    default_ip = "10.241.64.4"
    ip = input(f"Destination Receiver IP [{default_ip}]: ").strip()
    receiver_ip = ip if ip else default_ip

    default_port = 22
    port_str = input(f"Destination SSH Port [{default_port}]: ").strip()
    receiver_port = int(port_str) if port_str.isdigit() else default_port

    default_user = "root"
    user = input(f"Destination SSH Username [{default_user}]: ").strip()
    receiver_user = user if user else default_user

    default_key = "/root/test-psr-wdc-ssh_rsa.prv"
    while True:
        key = input(f"Path to SSH Private Key [{default_key}]: ").strip()
        ssh_key = key if key else default_key
        ssh_key = os.path.expanduser(ssh_key)
        if os.path.isfile(ssh_key):
            break
        print(f"[!] File not found at '{ssh_key}'. Please enter a valid path.")

    default_size = 1
    while True:
        size_str = input(f"Payload Size in GiB (e.g. 1, 10, 100) [{default_size}]: ").strip()
        if not size_str:
            size_gib = default_size
            break
        if size_str.isdigit() and int(size_str) > 0:
            size_gib = int(size_str)
            break
        print("[!] Payload size must be a positive integer.")

    default_blocks = 3
    while True:
        blocks_str = input(f"Number of Randomized Blocks / Iterations [{default_blocks}]: ").strip()
        if not blocks_str:
            blocks = default_blocks
            break
        if blocks_str.isdigit() and int(blocks_str) > 0:
            blocks = int(blocks_str)
            break
        print("[!] Number of blocks must be a positive integer.")

    default_seed = 42
    seed_str = input(f"Randomization Seed [{default_seed}]: ").strip()
    seed = int(seed_str) if seed_str.isdigit() else default_seed

    default_out = "./results"
    out = input(f"Output Directory [{default_out}]: ").strip()
    output_dir = out if out else default_out

    print("\n" + "=" * 68)
    print("  CAMPAIGN CONFIGURATION SUMMARY")
    print("=" * 68)
    print(f"  Target Destination : {receiver_user}@{receiver_ip}:{receiver_port}")
    print(f"  SSH Private Key    : {ssh_key}")
    print(f"  Payload Size       : {size_gib} GiB ({size_gib * 1024**3:,} bytes)")
    print(f"  Randomized Blocks  : {blocks} (Total Experimental Cells: {blocks * len(EXPERIMENTAL_VARIATIONS)})")
    print(f"  Random Seed        : {seed}")
    print(f"  Output Directory   : {output_dir}")
    print("=" * 68)

    confirm = input("\nProceed with this configuration? [Y/n]: ").strip().lower()
    if confirm in ("n", "no"):
        print("[!] Campaign aborted by user.")
        sys.exit(0)

    print("\n[*] Initializing benchmark campaign...\n")
    return {
        "receiver_ip": receiver_ip,
        "receiver_port": receiver_port,
        "receiver_user": receiver_user,
        "ssh_key": ssh_key,
        "size_gib": size_gib,
        "blocks": blocks,
        "seed": seed,
        "output_dir": output_dir,
    }


def main():
    parser = argparse.ArgumentParser(description="TCP PhD Cross-Datacenter Benchmarking Suite")
    parser.add_argument("--resume", default=None, help="Campaign directory to resume")
    cli_args = parser.parse_args()

    if cli_args.resume:
        orchestrator = TCPPhDOrchestrator(
            receiver_ip="",
            receiver_port=22,
            receiver_user="",
            ssh_key="",
            size_gib=1,
            blocks=1,
            output_dir="",
            seed=42,
            resume_dir=cli_args.resume,
        )
    else:
        cfg = prompt_user_parameters()
        orchestrator = TCPPhDOrchestrator(
            receiver_ip=cfg["receiver_ip"],
            receiver_port=cfg["receiver_port"],
            receiver_user=cfg["receiver_user"],
            ssh_key=cfg["ssh_key"],
            size_gib=cfg["size_gib"],
            blocks=cfg["blocks"],
            output_dir=cfg["output_dir"],
            seed=cfg["seed"],
        )

    state_captured = False
    restoration_status = "NOT_ATTEMPTED"

    try:
        orchestrator.preflight_validations()
        orchestrator.capture_or_load_observed_state()
        state_captured = True
        orchestrator.run_campaign()
    except KeyboardInterrupt:
        print("\n[!] Campaign interrupted by user (SIGINT). Initiating verified restoration...")
    except Exception as exc:
        error_path = os.path.join(orchestrator.campaign_dir, "campaign_error.log")
        with open(error_path, "a") as f:
            f.write(
                f"{datetime.datetime.now(datetime.timezone.utc).isoformat()} "
                f"{type(exc).__name__}: {exc}\n"
                f"{traceback.format_exc()}\n"
            )
        print(f"\n[!] Campaign failed with exception: {type(exc).__name__}: {exc}")
        print(f"[!] Stack trace captured in: {error_path}")
        raise
    finally:
        if state_captured:
            res_log = orchestrator.restore_system_state()
            restoration_status = res_log.get("status", "RESTORE_FAILED")
            orchestrator.generate_campaign_audit(restoration_status=restoration_status)


if __name__ == "__main__":
    main()
