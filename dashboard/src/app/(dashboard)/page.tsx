"use client";

import { StatsCard } from "@/components/stats-card";
import { StatusBadge } from "@/components/status-badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
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
import type { MeResponse } from "@/lib/types";
import { Bot, Clock, Wallet } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";
import { toast } from "sonner";
import { Skeleton } from "@/components/ui/skeleton";

export default function OverviewPage() {
  const token = useAccessToken();
  const [me, setMe] = useState<MeResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) return;
    let cancelled = false;
    (async () => {
      try {
        const data = await apiFetch<MeResponse>("/me", token);
        if (!cancelled) setMe(data);
      } catch (e) {
        if (!cancelled) {
          const msg =
            e instanceof ApiError ? e.message : "Could not load dashboard";
          toast.error(msg);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [token]);

  if (!token || loading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-10 w-64" />
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} className="h-28" />
          ))}
        </div>
      </div>
    );
  }

  if (!me) {
    return (
      <p className="text-muted-foreground">
        No data. If you just signed up, complete{" "}
        <code className="text-xs">POST /users/register</code> with your Supabase
        user id.
      </p>
    );
  }

  const w = me.wallet;

  return (
    <div className="space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-semibold tracking-tight">Resumen</h1>
          <p className="text-muted-foreground text-sm mt-1">
            Estado de tu cuenta y actividad reciente
          </p>
        </div>
        <div className="flex gap-2">
          <Button asChild>
            <Link href="/transactions">Review transactions</Link>
          </Button>
          <Button variant="outline" asChild>
            <Link href="/agents">Agents</Link>
          </Button>
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          title="Available"
          value={
            w
              ? `${Number(w.available_balance).toLocaleString()} ${w.currency}`
              : "—"
          }
          subtitle="Wallet balance"
          icon={Wallet}
        />
        <StatsCard
          title="Reserved"
          value={
            w
              ? `${Number(w.reserved_balance).toLocaleString()} ${w.currency}`
              : "—"
          }
          icon={Wallet}
        />
        <StatsCard
          title="Pending approvals"
          value={me.pending_payment_requests_count}
          subtitle="Payment requests"
          icon={Clock}
        />
        <StatsCard
          title="Agents"
          value={me.agents.filter((a) => a.is_active).length}
          subtitle={`${me.agents.length} total`}
          icon={Bot}
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card className="border-border/80">
          <CardHeader>
            <CardTitle className="text-base">Recent payment requests</CardTitle>
            <CardDescription>Latest activity</CardDescription>
          </CardHeader>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Date</TableHead>
                  <TableHead>Amount</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {me.recent_payment_requests.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={3} className="text-muted-foreground">
                      No payment requests yet.
                    </TableCell>
                  </TableRow>
                ) : (
                  me.recent_payment_requests.map((pr) => (
                    <TableRow key={pr.id}>
                      <TableCell className="text-xs text-muted-foreground">
                        {new Date(pr.created_at).toLocaleString()}
                      </TableCell>
                      <TableCell>
                        {Number(pr.amount).toLocaleString()} {pr.currency}
                      </TableCell>
                      <TableCell>
                        <StatusBadge status={pr.status} />
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        <Card className="border-border/80">
          <CardHeader>
            <CardTitle className="text-base">Recent payouts</CardTitle>
            <CardDescription>Execution status</CardDescription>
          </CardHeader>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Date</TableHead>
                  <TableHead>Destination</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {me.recent_payouts.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={3} className="text-muted-foreground">
                      No payouts yet.
                    </TableCell>
                  </TableRow>
                ) : (
                  me.recent_payouts.map((p) => (
                    <TableRow key={p.id}>
                      <TableCell className="text-xs text-muted-foreground">
                        {new Date(p.created_at).toLocaleString()}
                      </TableCell>
                      <TableCell className="font-mono text-xs">
                        {p.destination_cvu}
                      </TableCell>
                      <TableCell>
                        <StatusBadge status={p.status} />
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>

      <Card className="border-border/80">
        <CardHeader>
          <CardTitle className="text-base">Ledger</CardTitle>
          <CardDescription>Recent balance movements</CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Time</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Amount</TableHead>
                <TableHead>Description</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {me.recent_ledger_entries.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={4} className="text-muted-foreground">
                    No ledger entries.
                  </TableCell>
                </TableRow>
              ) : (
                me.recent_ledger_entries.map((e) => (
                  <TableRow key={e.id}>
                    <TableCell className="text-xs text-muted-foreground whitespace-nowrap">
                      {new Date(e.created_at).toLocaleString()}
                    </TableCell>
                    <TableCell className="text-xs">{e.entry_type}</TableCell>
                    <TableCell>
                      {Number(e.amount).toLocaleString()} {e.currency}
                    </TableCell>
                    <TableCell className="text-muted-foreground text-sm max-w-[240px] truncate">
                      {e.description ?? "—"}
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
