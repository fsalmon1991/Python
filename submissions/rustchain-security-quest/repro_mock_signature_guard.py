"""Local reproduction for RustChain bounty #398 Step 2.

This isolates the current production runtime guard from
node/rustchain_v2_integrated_v2.2.1_rip200.py so its behavior can be checked
without importing the full Flask node and its optional native dependencies.

Source reviewed at commit:
217ba85ef9cab3daac0da7b822c79437693444df
"""

import os

_MOCK_SIG_ALLOWED_ENVS = {
    "test", "testing", "dev", "development", "local", "testnet"
}


def enforce_mock_signature_runtime_guard(testnet_allow_mock_sig: bool) -> None:
    """Exact control-flow reproduction of the current RustChain runtime guard."""
    runtime_env = (
        os.environ.get("RC_RUNTIME_ENV")
        or os.environ.get("RUSTCHAIN_ENV")
        or "production"
    ).strip().lower()
    if testnet_allow_mock_sig and runtime_env not in _MOCK_SIG_ALLOWED_ENVS:
        raise RuntimeError(
            "TESTNET_ALLOW_MOCK_SIG must not be enabled outside test/dev runtimes"
        )


def run_case(runtime_env: str, mock_enabled: bool) -> str:
    os.environ["RC_RUNTIME_ENV"] = runtime_env
    try:
        enforce_mock_signature_runtime_guard(mock_enabled)
    except RuntimeError as exc:
        return f"{runtime_env=} {mock_enabled=} -> BLOCKED: {exc}"
    return f"{runtime_env=} {mock_enabled=} -> ALLOWED"


if __name__ == "__main__":
    cases = [
        ("production", True),
        ("test", True),
        ("production", False),
    ]
    for env, enabled in cases:
        print(run_case(env, enabled))
