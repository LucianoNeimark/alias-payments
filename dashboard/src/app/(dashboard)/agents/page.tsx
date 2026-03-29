"use client";

import { StatusBadge } from "@/components/status-badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { useAccessToken } from "@/hooks/use-access-token";
import { ApiError, apiFetch } from "@/lib/api";
import type { Agent, PaymentRequest } from "@/lib/types";
import { Bot } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { toast } from "sonner";
import { Skeleton } from "@/components/ui/skeleton";

export default function AgentsPage() {
  const token = useAccessToken();
  const [agents, setAgents] = useState<Agent[]>([]);
  const [prs, setPrs] = useState<PaymentRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<string | null>(null);
  const [busy, setBusy] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!token) return;
    const [ag, payments] = await Promise.all([
      apiFetch<Agent[]>("/me/agents", token),
      apiFetch<PaymentRequest[]>("/me/payment-requests?limit=100&offset=0", token),
    ]);
    setAgents(ag);
    setPrs(payments);
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
          toast.error(e instanceof ApiError ? e.message : "Failed to load agents");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [token, load]);

  async function toggleActive(agent: Agent) {
    if (!token) return;
    setBusy(agent.id);
    try {
      await apiFetch<Agent>(`/me/agents/${agent.id}`, token, {
        method: "PATCH",
        body: JSON.stringify({ is_active: !agent.is_active }),
      });
      toast.success(agent.is_active ? "Agent deactivated" : "Agent activated");
      await load();
    } catch (e) {
      toast.error(e instanceof ApiError ? e.message : "Update failed");
    } finally {
      setBusy(null);
    }
  }

  if (!token || loading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-10 w-40" />
        <div className="grid gap-4 sm:grid-cols-2">
          <Skeleton className="h-48" />
          <Skeleton className="h-48" />
        </div>
      </div>
    );
  }

  const forAgent = (id: string) => prs.filter((p) => p.agent_id === id);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight">Agents</h1>
        <p className="text-muted-foreground text-sm mt-1">
          Spending identities linked to your account.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {agents.map((agent) => (
          <Card
            key={agent.id}
            className={`border-border/80 cursor-pointer transition-shadow hover:shadow-md ${
              selected === agent.id ? "ring-1 ring-primary" : ""
            }`}
            onClick={() =>
              setSelected(selected === agent.id ? null : agent.id)
            }
          >
            <CardHeader className="pb-2">
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-center gap-2">
                  <Bot className="h-5 w-5 text-muted-foreground shrink-0" />
                  <div>
                    <CardTitle className="text-base">{agent.name}</CardTitle>
                    <CardDescription className="line-clamp-2">
                      {agent.description ?? "No description"}
                    </CardDescription>
                  </div>
                </div>
                <span
                  className={`mt-1 h-2.5 w-2.5 rounded-full shrink-0 ${
                    agent.is_active ? "bg-emerald-500" : "bg-zinc-500"
                  }`}
                  title={agent.is_active ? "Active" : "Inactive"}
                />
              </div>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <div className="flex flex-wrap gap-2 items-center">
                <StatusBadge
                  status={agent.is_active ? "active" : "inactive"}
                />
                {agent.default_spending_limit != null ? (
                  <span className="text-muted-foreground">
                    Limit:{" "}
                    {Number(agent.default_spending_limit).toLocaleString()}
                  </span>
                ) : null}
              </div>
              <Separator />
              <div className="flex justify-between items-center gap-2">
                <span className="text-muted-foreground">
                  {forAgent(agent.id).length} payment request(s)
                </span>
                <Button
                  size="sm"
                  variant="outline"
                  disabled={busy === agent.id}
                  onClick={(e) => {
                    e.stopPropagation();
                    void toggleActive(agent);
                  }}
                >
                  {agent.is_active ? "Deactivate" : "Activate"}
                </Button>
              </div>
              {selected === agent.id ? (
                <div className="pt-2 border-t border-border text-xs space-y-1 max-h-40 overflow-y-auto">
                  {forAgent(agent.id).length === 0 ? (
                    <p className="text-muted-foreground">No requests yet.</p>
                  ) : (
                    forAgent(agent.id).slice(0, 8).map((p) => (
                      <div
                        key={p.id}
                        className="flex justify-between gap-2 py-1"
                      >
                        <span className="text-muted-foreground">
                          {new Date(p.created_at).toLocaleDateString()}
                        </span>
                        <span>
                          {Number(p.amount).toLocaleString()} {p.currency}
                        </span>
                        <StatusBadge status={p.status} />
                      </div>
                    ))
                  )}
                </div>
              ) : null}
            </CardContent>
          </Card>
        ))}
      </div>

      {agents.length === 0 ? (
        <p className="text-muted-foreground">No agents yet.</p>
      ) : null}
    </div>
  );
}
