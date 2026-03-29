"use client";

import { StatusBadge } from "@/components/status-badge";
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
import type { FundingOrder } from "@/lib/types";
import { useCallback, useEffect, useState } from "react";
import { toast } from "sonner";
import { Skeleton } from "@/components/ui/skeleton";

export default function FundingPage() {
  const token = useAccessToken();
  const [rows, setRows] = useState<FundingOrder[]>([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    if (!token) return;
    const list = await apiFetch<FundingOrder[]>(
      `/me/funding-orders?limit=100&offset=0`,
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
          toast.error(
            e instanceof ApiError ? e.message : "Failed to load funding orders",
          );
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [token, load]);

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
        <h1 className="text-3xl font-semibold tracking-tight">Funding</h1>
        <p className="text-muted-foreground text-sm mt-1">
          CVU / alias deposits and order status.
        </p>
      </div>

      <Card className="border-border/80">
        <CardHeader>
          <CardTitle className="text-base">Funding orders</CardTitle>
          <CardDescription>Incoming top-ups to your wallet</CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Created</TableHead>
                <TableHead>Amount</TableHead>
                <TableHead>CVU</TableHead>
                <TableHead>Alias</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Expires</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {rows.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-muted-foreground">
                    No funding orders yet.
                  </TableCell>
                </TableRow>
              ) : (
                rows.map((o) => (
                  <TableRow key={o.id}>
                    <TableCell className="text-xs text-muted-foreground whitespace-nowrap">
                      {new Date(o.created_at).toLocaleString()}
                    </TableCell>
                    <TableCell>
                      {Number(o.requested_amount).toLocaleString()} {o.currency}
                    </TableCell>
                    <TableCell className="font-mono text-xs max-w-[140px] truncate">
                      {o.cvu ?? "—"}
                    </TableCell>
                    <TableCell className="text-sm">{o.alias ?? "—"}</TableCell>
                    <TableCell>
                      <StatusBadge status={o.status} />
                    </TableCell>
                    <TableCell className="text-xs text-muted-foreground whitespace-nowrap">
                      {o.expires_at
                        ? new Date(o.expires_at).toLocaleString()
                        : "—"}
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
