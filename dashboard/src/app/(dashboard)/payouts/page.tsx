"use client";

import { StatusBadge } from "@/components/status-badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useAccessToken } from "@/hooks/use-access-token";
import { ApiError, apiFetch } from "@/lib/api";
import type { Payout } from "@/lib/types";
import { useCallback, useEffect, useState } from "react";
import { toast } from "sonner";
import { Skeleton } from "@/components/ui/skeleton";

const EXECUTABLE = new Set(["queued"]);
const RETRYABLE = new Set(["failed", "needs_manual_review"]);

export default function PayoutsPage() {
  const token = useAccessToken();
  const [rows, setRows] = useState<Payout[]>([]);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!token) return;
    const list = await apiFetch<Payout[]>(
      `/me/payouts?limit=100&offset=0`,
      token,
    );
    setRows(list);
  }, [token]);

  useEffect(() => {
    if (!token) return;
    let cancelled = false;
    (async () => {
      setLoading(true);
      try {
        await load();
      } catch (e) {
        if (!cancelled) {
          toast.error(e instanceof ApiError ? e.message : "Failed to load payouts");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [token, load]);

  async function execute(p: Payout) {
    if (!token) return;
    setBusy(p.id);
    try {
      await apiFetch(`/me/payouts/${p.id}/execute`, token, { method: "POST" });
      toast.success("Payout executed");
      await load();
    } catch (e) {
      toast.error(e instanceof ApiError ? e.message : "Execute failed");
    } finally {
      setBusy(null);
    }
  }

  async function retry(p: Payout) {
    if (!token) return;
    setBusy(p.id);
    try {
      await apiFetch(`/me/payouts/${p.id}/retry`, token, { method: "POST" });
      toast.success("Retry started");
      await load();
    } catch (e) {
      toast.error(e instanceof ApiError ? e.message : "Retry failed");
    } finally {
      setBusy(null);
    }
  }

  if (!token || loading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-10 w-40" />
        <Skeleton className="h-96" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight">Payouts</h1>
        <p className="text-muted-foreground text-sm mt-1">
          Bank executions for approved payment requests.
        </p>
      </div>

      <Card className="border-border/80">
        <CardHeader>
          <CardTitle className="text-base">History</CardTitle>
          <CardDescription>Retry failed or manual-review payouts</CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Created</TableHead>
                <TableHead>Amount</TableHead>
                <TableHead>Destination</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Receipt</TableHead>
                <TableHead>Failure</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {rows.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} className="text-muted-foreground">
                    No payouts yet.
                  </TableCell>
                </TableRow>
              ) : (
                rows.map((p) => (
                  <TableRow key={p.id}>
                    <TableCell className="text-xs text-muted-foreground whitespace-nowrap">
                      {new Date(p.created_at).toLocaleString()}
                    </TableCell>
                    <TableCell>
                      {Number(p.amount).toLocaleString()} {p.currency}
                    </TableCell>
                    <TableCell className="font-mono text-xs max-w-[120px] truncate">
                      {p.destination_cvu}
                    </TableCell>
                    <TableCell>
                      <StatusBadge status={p.status} />
                    </TableCell>
                    <TableCell className="text-xs max-w-[100px] truncate">
                      {p.provider_receipt_ref ?? "—"}
                    </TableCell>
                    <TableCell className="text-xs text-destructive max-w-[160px] truncate">
                      {p.failure_reason ?? "—"}
                    </TableCell>
                    <TableCell className="text-right space-x-2">
                      {EXECUTABLE.has(p.status) ? (
                        <Button
                          size="sm"
                          disabled={busy === p.id}
                          onClick={() => void execute(p)}
                        >
                          Execute
                        </Button>
                      ) : null}
                      {RETRYABLE.has(p.status) ? (
                        <Button
                          size="sm"
                          variant="outline"
                          disabled={busy === p.id}
                          onClick={() => void retry(p)}
                        >
                          Retry
                        </Button>
                      ) : null}
                      {!EXECUTABLE.has(p.status) && !RETRYABLE.has(p.status) ? (
                        <span className="text-muted-foreground text-xs">—</span>
                      ) : null}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
