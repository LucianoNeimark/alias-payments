"use client";

import { StatusBadge } from "@/components/status-badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
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
import type { Agent, Approval, PaymentRequest } from "@/lib/types";
import { ChevronDown, ChevronRight } from "lucide-react";
import { Fragment, useCallback, useEffect, useMemo, useState } from "react";
import { toast } from "sonner";
import { Skeleton } from "@/components/ui/skeleton";

const STATUSES = [
  "all",
  "requested",
  "reserved",
  "executing",
  "completed",
  "failed",
  "rejected",
  "insufficient_funds",
  "needs_manual_review",
] as const;

export default function TransactionsPage() {
  const token = useAccessToken();
  const [filter, setFilter] = useState<string>("all");
  const [rows, setRows] = useState<PaymentRequest[]>([]);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState<string | null>(null);
  const [approvalsByPr, setApprovalsByPr] = useState<Record<string, Approval[]>>({});
  const [busyId, setBusyId] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!token) return;
    const q =
      filter === "all"
        ? "/me/payment-requests?limit=100&offset=0"
        : `/me/payment-requests?limit=100&offset=0&status=${encodeURIComponent(filter)}`;
    const [list, ag] = await Promise.all([
      apiFetch<PaymentRequest[]>(q, token),
      apiFetch<Agent[]>("/me/agents", token),
    ]);
    setRows(list);
    setAgents(ag);
  }, [token, filter]);

  useEffect(() => {
    if (!token) return;
    let cancelled = false;
    (async () => {
      setLoading(true);
      try {
        await load();
      } catch (e) {
        if (!cancelled) {
          toast.error(e instanceof ApiError ? e.message : "Failed to load");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [token, load]);

  const agentName = useMemo(() => {
    const m = new Map<string, string>();
    agents.forEach((a) => m.set(a.id, a.name));
    return m;
  }, [agents]);

  async function loadApprovals(prId: string) {
    if (!token) return;
    if (prId in approvalsByPr) {
      setExpanded((e) => (e === prId ? null : prId));
      return;
    }
    try {
      const list = await apiFetch<Approval[]>(
        `/me/payment-requests/${prId}/approvals`,
        token,
      );
      setApprovalsByPr((prev) => ({ ...prev, [prId]: list }));
      setExpanded(prId);
    } catch (e) {
      toast.error(e instanceof ApiError ? e.message : "Failed to load approvals");
    }
  }

  async function approve(pr: PaymentRequest) {
    if (!token) return;
    setBusyId(pr.id);
    try {
      await apiFetch(`/me/payment-requests/${pr.id}/approve`, token, {
        method: "POST",
        body: JSON.stringify({}),
      });
      toast.success("Approved");
      await load();
    } catch (e) {
      toast.error(e instanceof ApiError ? e.message : "Approve failed");
    } finally {
      setBusyId(null);
    }
  }

  async function reject(pr: PaymentRequest) {
    if (!token) return;
    const reason = window.prompt("Rejection reason (optional)") ?? undefined;
    setBusyId(pr.id);
    try {
      await apiFetch(`/me/payment-requests/${pr.id}/reject`, token, {
        method: "POST",
        body: JSON.stringify({ decision_reason: reason || null }),
      });
      toast.success("Rejected");
      await load();
    } catch (e) {
      toast.error(e instanceof ApiError ? e.message : "Reject failed");
    } finally {
      setBusyId(null);
    }
  }

  if (!token || loading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-10 w-48" />
        <Skeleton className="h-96" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight">Transactions</h1>
        <p className="text-muted-foreground text-sm mt-1">
          Payment requests across your agents — approve pending transfers.
        </p>
      </div>

      <Card className="border-border/80">
        <CardHeader className="flex flex-row flex-wrap items-center justify-between gap-4">
          <div>
            <CardTitle className="text-base">Payment requests</CardTitle>
            <CardDescription>Filter by status</CardDescription>
          </div>
          <Select value={filter} onValueChange={setFilter}>
            <SelectTrigger className="w-[200px]">
              <SelectValue placeholder="Status" />
            </SelectTrigger>
            <SelectContent>
              {STATUSES.map((s) => (
                <SelectItem key={s} value={s}>
                  {s === "all" ? "All" : s.replace(/_/g, " ")}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </CardHeader>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-8" />
                <TableHead>Created</TableHead>
                <TableHead>Agent</TableHead>
                <TableHead>Amount</TableHead>
                <TableHead>Destination</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {rows.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} className="text-muted-foreground">
                    No payment requests.
                  </TableCell>
                </TableRow>
              ) : (
                rows.map((pr) => (
                  <Fragment key={pr.id}>
                    <TableRow>
                      <TableCell>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8"
                          onClick={() => void loadApprovals(pr.id)}
                          aria-label="Toggle details"
                        >
                          {expanded === pr.id ? (
                            <ChevronDown className="h-4 w-4" />
                          ) : (
                            <ChevronRight className="h-4 w-4" />
                          )}
                        </Button>
                      </TableCell>
                      <TableCell className="text-xs text-muted-foreground whitespace-nowrap">
                        {new Date(pr.created_at).toLocaleString()}
                      </TableCell>
                      <TableCell className="text-sm">
                        {agentName.get(pr.agent_id) ?? pr.agent_id.slice(0, 8)}
                      </TableCell>
                      <TableCell>
                        {Number(pr.amount).toLocaleString()} {pr.currency}
                      </TableCell>
                      <TableCell className="font-mono text-xs max-w-[140px] truncate">
                        {pr.destination_cvu || pr.destination_alias || "—"}
                      </TableCell>
                      <TableCell>
                        <StatusBadge status={pr.status} />
                      </TableCell>
                      <TableCell className="text-right space-x-2">
                        {pr.status === "requested" ? (
                          <>
                            <Button
                              size="sm"
                              disabled={busyId === pr.id}
                              onClick={() => void approve(pr)}
                            >
                              Approve
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              disabled={busyId === pr.id}
                              onClick={() => void reject(pr)}
                            >
                              Reject
                            </Button>
                          </>
                        ) : (
                          <span className="text-muted-foreground text-xs">—</span>
                        )}
                      </TableCell>
                    </TableRow>
                    {expanded === pr.id ? (
                      <TableRow>
                        <TableCell colSpan={7} className="bg-muted/30">
                          <div className="py-3 px-2 text-sm space-y-2">
                            <div>
                              <span className="font-medium">Purpose:</span> {pr.purpose}
                            </div>
                            <div>
                              <span className="font-medium">Approvals:</span>
                              <ul className="list-disc ml-5 mt-1">
                                {(approvalsByPr[pr.id] ?? []).length === 0 ? (
                                  <li className="text-muted-foreground">None yet</li>
                                ) : (
                                  (approvalsByPr[pr.id] ?? []).map((a) => (
                                    <li key={a.id}>
                                      {a.decision}
                                      {a.decision_reason
                                        ? ` — ${a.decision_reason}`
                                        : ""}{" "}
                                      <span className="text-muted-foreground text-xs">
                                        ({new Date(a.created_at).toLocaleString()})
                                      </span>
                                    </li>
                                  ))
                                )}
                              </ul>
                            </div>
                          </div>
                        </TableCell>
                      </TableRow>
                    ) : null}
                  </Fragment>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
