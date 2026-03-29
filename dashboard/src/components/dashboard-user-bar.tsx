"use client";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { useAccessToken } from "@/hooks/use-access-token";
import { ApiError, apiFetch } from "@/lib/api";
import type { MeResponse } from "@/lib/types";
import { cn } from "@/lib/utils";
import { Check, Copy, Eye, EyeOff, HelpCircle } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { toast } from "sonner";

const COPY_FEEDBACK_MS = 2500;
/** Ancho fijo: "Copiado" + ícono; evita que la barra salte al cambiar el texto */
const COPY_USER_ID_BTN_CLASS = "w-[7.5rem] shrink-0 gap-1.5";

export function DashboardUserBar() {
  const token = useAccessToken();
  const [me, setMe] = useState<MeResponse | null>(null);
  const [userIdVisible, setUserIdVisible] = useState(false);
  const [copyFeedback, setCopyFeedback] = useState<"idle" | "success" | "error">(
    "idle",
  );
  const copyResetRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (!token) return;
    let cancelled = false;
    (async () => {
      try {
        const data = await apiFetch<MeResponse>("/me", token);
        if (!cancelled) setMe(data);
      } catch (e) {
        if (!cancelled && e instanceof ApiError) {
          toast.error(e.message);
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [token]);

  useEffect(() => {
    return () => {
      if (copyResetRef.current) clearTimeout(copyResetRef.current);
    };
  }, []);

  if (!me) return null;

  function scheduleCopyFeedback(next: "success" | "error") {
    if (copyResetRef.current) clearTimeout(copyResetRef.current);
    setCopyFeedback(next);
    copyResetRef.current = setTimeout(() => {
      setCopyFeedback("idle");
      copyResetRef.current = null;
    }, COPY_FEEDBACK_MS);
  }

  async function copyUserId() {
    if (!me) return;
    try {
      await navigator.clipboard.writeText(me.user.id);
      scheduleCopyFeedback("success");
    } catch {
      scheduleCopyFeedback("error");
      toast.error("No se pudo copiar");
    }
  }

  const copyFeedbackVisual =
    copyFeedback === "success"
      ? "border-emerald-500/70 bg-emerald-500/15 text-emerald-700 hover:bg-emerald-500/20 hover:text-emerald-800 dark:border-emerald-500/50 dark:bg-emerald-500/10 dark:text-emerald-400 dark:hover:bg-emerald-500/15 dark:hover:text-emerald-300"
      : copyFeedback === "error"
        ? "border-destructive/60 bg-destructive/10 text-destructive hover:bg-destructive/15 hover:text-destructive"
        : "";

  const copyLabel =
    copyFeedback === "success"
      ? "Copiado"
      : copyFeedback === "error"
        ? "Error"
        : "Copiar";

  const copyIcon =
    copyFeedback === "success" ? (
      <Check className="h-3.5 w-3.5 shrink-0" aria-hidden />
    ) : (
      <Copy className="h-3.5 w-3.5 shrink-0" aria-hidden />
    );

  return (
    <div className="border-b border-border bg-muted/30">
      <div className="max-w-6xl mx-auto px-6 lg:px-8 py-3 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between sm:gap-4">
        <div className="flex flex-wrap items-center gap-x-3 gap-y-2">
          <span className="font-semibold text-sm">{me.user.username}</span>
          <span className="text-muted-foreground hidden sm:inline">·</span>
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xs text-muted-foreground uppercase tracking-wide">
              user_id
            </span>
            <div className="flex items-center gap-1 rounded-md border border-border bg-background pr-1">
              <code
                className={cn(
                  "text-xs font-mono px-2 py-1.5 min-w-0 max-w-[min(100%,18rem)] block transition-[filter]",
                  userIdVisible
                    ? "truncate select-text"
                    : "blur-[7px] select-none text-foreground/80",
                )}
                title={userIdVisible ? undefined : "Oculto — pulsa el ojo para ver"}
              >
                {me.user.id}
              </code>
              <Button
                type="button"
                variant="ghost"
                size="icon"
                className="h-8 w-8 shrink-0 text-muted-foreground hover:text-foreground"
                aria-label={userIdVisible ? "Ocultar user ID" : "Mostrar user ID"}
                onClick={() => setUserIdVisible((v) => !v)}
              >
                {userIdVisible ? (
                  <EyeOff className="h-4 w-4" />
                ) : (
                  <Eye className="h-4 w-4" />
                )}
              </Button>
            </div>
            <Button
              type="button"
              variant="outline"
              size="sm"
              className={cn(
                "h-8 transition-colors duration-200",
                COPY_USER_ID_BTN_CLASS,
                copyFeedbackVisual,
              )}
              onClick={() => void copyUserId()}
            >
              {copyIcon}
              {copyLabel}
            </Button>
            <Dialog>
              <DialogTrigger asChild>
                <Button
                  type="button"
                  variant="secondary"
                  size="sm"
                  className="h-8 gap-1"
                >
                  <HelpCircle className="h-3.5 w-3.5" />
                  ¿Para agentes?
                </Button>
              </DialogTrigger>
              <DialogContent className="sm:max-w-md gap-0 p-0 overflow-hidden sm:rounded-xl border-2 bg-white dark:bg-zinc-950">
                <div className="border-b border-zinc-200 bg-zinc-100 px-6 py-4 dark:border-zinc-700 dark:bg-zinc-900">
                  <DialogHeader className="space-y-2 text-left">
                    <DialogTitle className="text-xl pr-8 text-zinc-900 dark:text-zinc-50">
                      Tu user ID
                    </DialogTitle>
                    <DialogDescription className="text-base text-zinc-600 dark:text-zinc-400">
                      Identificador que usa la API y tus agentes para tu cuenta.
                    </DialogDescription>
                  </DialogHeader>
                </div>
                <div className="space-y-4 px-6 py-5 text-sm bg-white dark:bg-zinc-950">
                  <p className="text-zinc-600 dark:text-zinc-400 leading-relaxed">
                    Este valor es tu{" "}
                    <strong className="text-zinc-900 dark:text-zinc-50">user_id</strong>{" "}
                    en Alias Payments. Sirve para crear solicitudes de pago y operar
                    sobre tu cuenta desde integraciones.
                  </p>
                  <div className="rounded-lg border border-amber-600 bg-amber-100 px-4 py-3 space-y-2 dark:border-amber-700 dark:bg-amber-950">
                    <p className="font-medium text-amber-950 text-sm leading-snug dark:text-amber-100">
                      Si tu agente te pide el identificador, comparte este{" "}
                      <span className="font-mono text-xs">user_id</span> para que
                      pueda usar tu cuenta.
                    </p>
                    <p className="text-xs text-amber-900/90 dark:text-amber-200/90">
                      Solo compártelo con agentes o servicios en los que confíes.
                    </p>
                  </div>
                  <div className="rounded-md border border-zinc-200 bg-zinc-100 p-3 dark:border-zinc-700 dark:bg-zinc-900">
                    <div className="flex items-center justify-between gap-3 border-b border-zinc-200/90 pb-2.5 dark:border-zinc-600/80">
                      <p className="text-[10px] uppercase tracking-wider text-zinc-500 dark:text-zinc-400">
                        Tu identificador
                      </p>
                      <Button
                        type="button"
                        size="sm"
                        variant="secondary"
                        className={cn(
                          "h-8 transition-colors duration-200",
                          COPY_USER_ID_BTN_CLASS,
                          copyFeedback !== "idle" && "border",
                          copyFeedbackVisual,
                        )}
                        onClick={() => void copyUserId()}
                      >
                        {copyIcon}
                        {copyLabel}
                      </Button>
                    </div>
                    <div className="pt-2.5 [scrollbar-width:thin]">
                      <div className="overflow-x-auto overscroll-x-contain -mx-0.5 px-0.5">
                        <code className="block w-max max-w-none text-xs font-mono leading-relaxed tracking-normal text-zinc-900 dark:text-zinc-100 whitespace-nowrap">
                          {me.user.id}
                        </code>
                      </div>
                    </div>
                  </div>
                </div>
              </DialogContent>
            </Dialog>
          </div>
        </div>
        <p className="text-xs text-muted-foreground sm:text-right truncate max-w-full">
          {me.user.email}
        </p>
      </div>
    </div>
  );
}
