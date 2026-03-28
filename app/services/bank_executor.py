"""
Bank executor: mock for local dev/tests, or HTTP calls to the MP transfer microservice.
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass
from decimal import Decimal
from uuid import uuid4

import httpx

from app.services.payments_client import (
    PaymentsServiceError,
    get_payments_client,
    transfer_with_retry,
)

logger = logging.getLogger(__name__)

# Single-consumer serialization (one transfer at a time per process)
_executor_lock = asyncio.Lock()


@dataclass
class BankTransferResult:
    success: bool
    executor_run_id: str
    provider_receipt_ref: str | None = None
    failure_reason: str | None = None
    needs_manual_review: bool = False


def _amount_to_pesos_int(amount: Decimal) -> int:
    return int(amount)


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
    Run outbound transfer under a global lock.

    When PAYMENTS_SERVICE_URL + PAYMENTS_SERVICE_API_KEY are set, calls the
    external MP transfer service. Otherwise uses the mock implementation.
    """
    client = get_payments_client()
    if client is None:
        return await _mock_run_transfer(
            amount=amount,
            destination_cvu=destination_cvu,
            destination_alias=destination_alias,
            timeout_seconds=timeout_seconds,
            force_failure=force_failure,
            force_manual_review=force_manual_review,
        )

    # Real client: mock-only flags are ignored
    alias = (destination_alias or "").strip() or destination_cvu.strip()
    if not alias:
        return BankTransferResult(
            success=False,
            executor_run_id=f"run_{uuid4().hex[:12]}",
            failure_reason="No destination alias or CVU",
            needs_manual_review=False,
        )

    pesos = _amount_to_pesos_int(amount)
    if pesos <= 0:
        return BankTransferResult(
            success=False,
            executor_run_id=f"run_{uuid4().hex[:12]}",
            failure_reason="Amount must be positive integer ARS",
            needs_manual_review=False,
        )

    run_id = f"mp_{uuid4().hex[:12]}"
    t0 = time.perf_counter()
    logger.info(
        "bank_executor: MP service transfer start run_id=%s amount=%s alias=%s...",
        run_id,
        pesos,
        alias[:8],
    )

    async with _executor_lock:
        try:
            resp = await transfer_with_retry(client, alias, pesos)
        except PaymentsServiceError as e:
            elapsed = time.perf_counter() - t0
            logger.warning(
                "bank_executor: MP service error status=%s run_id=%s elapsed=%.3fs detail=%s",
                e.status_code,
                run_id,
                elapsed,
                e.detail[:200],
            )
            if e.status_code == 403:
                return BankTransferResult(
                    success=False,
                    executor_run_id=run_id,
                    failure_reason=e.detail,
                    needs_manual_review=False,
                )
            if e.status_code == 422:
                return BankTransferResult(
                    success=False,
                    executor_run_id=run_id,
                    failure_reason=e.detail,
                    needs_manual_review=False,
                )
            # 409 exhausted, 500 after retry, or other — may need human check
            if e.status_code == 409:
                return BankTransferResult(
                    success=False,
                    executor_run_id=run_id,
                    failure_reason=e.detail,
                    needs_manual_review=True,
                )
            if e.status_code >= 500:
                return BankTransferResult(
                    success=False,
                    executor_run_id=run_id,
                    failure_reason=e.detail,
                    needs_manual_review=True,
                )
            return BankTransferResult(
                success=False,
                executor_run_id=run_id,
                failure_reason=e.detail,
                needs_manual_review=False,
            )
        except httpx.TimeoutException:
            elapsed = time.perf_counter() - t0
            logger.error(
                "bank_executor: timeout after retries run_id=%s elapsed=%.3fs",
                run_id,
                elapsed,
            )
            return BankTransferResult(
                success=False,
                executor_run_id=run_id,
                failure_reason="Payments service request timed out",
                needs_manual_review=True,
            )
        except Exception as exc:  # noqa: BLE001 — surface as failed transfer
            elapsed = time.perf_counter() - t0
            logger.exception(
                "bank_executor: unexpected error run_id=%s elapsed=%.3fs",
                run_id,
                elapsed,
            )
            return BankTransferResult(
                success=False,
                executor_run_id=run_id,
                failure_reason=str(exc),
                needs_manual_review=True,
            )

    elapsed = time.perf_counter() - t0
    logger.info(
        "bank_executor: MP service success run_id=%s elapsed=%.3fs detail=%s",
        run_id,
        elapsed,
        resp.detail[:120],
    )
    return BankTransferResult(
        success=True,
        executor_run_id=run_id,
        provider_receipt_ref=resp.detail,
    )


async def _mock_run_transfer(
    *,
    amount: Decimal,
    destination_cvu: str,
    destination_alias: str | None,
    timeout_seconds: float,
    force_failure: bool,
    force_manual_review: bool,
) -> BankTransferResult:
    async def _work() -> BankTransferResult:
        run_id = f"run_{uuid4().hex[:12]}"
        t0 = time.perf_counter()
        logger.info(
            "bank_executor(mock): start run_id=%s amount=%s cvu=%s",
            run_id,
            amount,
            destination_cvu[:8] + "...",
        )
        await asyncio.sleep(0.15)

        if force_manual_review:
            logger.warning(
                "bank_executor(mock): needs_manual_review run_id=%s elapsed=%.3fs",
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
                "bank_executor(mock): failed run_id=%s elapsed=%.3fs",
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
            "bank_executor(mock): success run_id=%s receipt=%s elapsed=%.3fs",
            run_id,
            receipt,
            time.perf_counter() - t0,
        )
        _ = destination_alias
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
                "bank_executor(mock): timeout after %.1fs",
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
