"""Background polling of queued payouts and sequential execution."""

from __future__ import annotations

import asyncio
import logging

from app.config import get_settings
from app.database import get_supabase_client
from app.repositories import payout_repository
from app.services import payout_service

logger = logging.getLogger(__name__)


async def run_payout_poller() -> None:
    """Poll for ``queued`` payouts and execute them one at a time until shutdown.

    First cycle runs immediately; subsequent cycles wait ``payout_poll_interval`` seconds.
    """
    while True:
        settings = get_settings()
        interval = max(int(settings.payout_poll_interval), 1)

        try:
            client = get_supabase_client()
            queued = payout_repository.list_queued_payouts(client, limit=20)
            if queued:
                logger.info(
                    "payout_poller: found %d queued payout(s), executing sequentially",
                    len(queued),
                )
                for row in queued:
                    payout_id = str(row.get("id", ""))
                    if not payout_id:
                        continue
                    try:
                        logger.info("payout_poller: executing payout_id=%s", payout_id)
                        await payout_service.execute_payout(client, payout_id)
                        logger.info("payout_poller: finished payout_id=%s", payout_id)
                    except asyncio.CancelledError:
                        raise
                    except Exception:
                        logger.exception(
                            "payout_poller: execute failed for payout_id=%s",
                            payout_id,
                        )

        except asyncio.CancelledError:
            logger.info("payout_poller: cancelled")
            raise

        try:
            await asyncio.sleep(float(interval))
        except asyncio.CancelledError:
            logger.info("payout_poller: shutdown during sleep")
            raise
