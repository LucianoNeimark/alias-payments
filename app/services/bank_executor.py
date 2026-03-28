"""
Mock bank executor (Selenium + Mercado Pago) for demo.

Serializes execution with a process-global asyncio lock and supports timeout.
Replace `run_transfer` internals with real Selenium when integrating.
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass
from decimal import Decimal
from uuid import uuid4

logger = logging.getLogger(__name__)

# Single-consumer serialization for demo (one transfer at a time per process)
_executor_lock = asyncio.Lock()


@dataclass
class BankTransferResult:
    success: bool
    executor_run_id: str
    provider_receipt_ref: str | None = None
    failure_reason: str | None = None
    needs_manual_review: bool = False


async def run_transfer(
    *,
    amount: Decimal,
    destination_cvu: str,
    destination_alias: str | None = None,
    timeout_seconds: float = 60.0,
    force_failure: bool = False,
    force_manual_review: bool = False,
) -> BankTransferResult:
    """
    Run a mocked outbound transfer holding the global lock for the whole operation.

    Parameters
    ----------
    force_failure
        If True, simulates Mercado Pago / Selenium failure after a short delay.
    force_manual_review
        If True, returns success=False with needs_manual_review=True (no debit).
    """

    async def _work() -> BankTransferResult:
        run_id = f"run_{uuid4().hex[:12]}"
        t0 = time.perf_counter()
        logger.info(
            "bank_executor: start run_id=%s amount=%s cvu=%s",
            run_id,
            amount,
            destination_cvu[:8] + "...",
        )
        await asyncio.sleep(0.15)  # simulate UI automation latency

        if force_manual_review:
            logger.warning(
                "bank_executor: needs_manual_review run_id=%s elapsed=%.3fs",
                run_id,
                time.perf_counter() - t0,
            )
            return BankTransferResult(
                success=False,
                executor_run_id=run_id,
                failure_reason="Mock: manual review required (captcha / extra step)",
                needs_manual_review=True,
            )

        if force_failure:
            logger.warning(
                "bank_executor: failed run_id=%s elapsed=%.3fs",
                run_id,
                time.perf_counter() - t0,
            )
            return BankTransferResult(
                success=False,
                executor_run_id=run_id,
                failure_reason="Mock: session expired or transfer rejected",
                needs_manual_review=False,
            )

        receipt = f"mp_mock_{uuid4().hex[:16]}"
        logger.info(
            "bank_executor: success run_id=%s receipt=%s elapsed=%.3fs",
            run_id,
            receipt,
            time.perf_counter() - t0,
        )
        _ = destination_alias  # real executor would use alias when present
        return BankTransferResult(
            success=True,
            executor_run_id=run_id,
            provider_receipt_ref=receipt,
        )

    async with _executor_lock:
        try:
            return await asyncio.wait_for(_work(), timeout=timeout_seconds)
        except TimeoutError:
            logger.error(
                "bank_executor: timeout after %.1fs (holding lock released)",
                timeout_seconds,
            )
            return BankTransferResult(
                success=False,
                executor_run_id=f"run_timeout_{uuid4().hex[:8]}",
                failure_reason=f"Executor timeout after {timeout_seconds:.0f}s",
                needs_manual_review=True,
            )


def acquire_lock() -> asyncio.Lock:
    """Expose lock for tests that need to inspect the same singleton."""
    return _executor_lock
