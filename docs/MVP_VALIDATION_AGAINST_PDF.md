# Validación MVP: backend vs `agentpay_mvp_arquitectura.pdf`

Informe de auditoría (solo diagnóstico). Fecha de referencia del código: repo `alias-payments`.

---

## 1. Requisitos extraídos del PDF (resumen)

### Principios

1. Separar fondeo entrante, ledger interno, aprobación explícita y ejecución bancaria.
2. Ledger explicativo movimiento a movimiento; wallet con `available` / `reserved` materializada.
3. Reservar saldo antes de ejecutar; evitar doble gasto ante concurrencia (idealmente transacción/lock).
4. Idempotencia en webhooks y reintentos.
5. Ejecutor Selenium encapsulado: cola/lock, timeout, logs; punto frágil aislado.

### Modelo de datos (8 entidades)

`users`, `agents`, `wallets`, `funding_orders`, `funding_events`, `payment_requests`, `approvals`, `payouts`, `ledger_entries`.

### Endpoints sugeridos

| Método | Ruta (PDF) | En código (`README` / routers) |
|--------|------------|-----------------------------------|
| POST | `/users/register` | Sí (`/users/register`) |
| POST | `/agents` | Sí (`POST /agents/`) |
| GET | `/wallets/{user_id}` | Sí |
| POST | `/funding-orders` | Sí (`POST /funding-orders/`) |
| POST | `/webhooks/talo` | Sí |
| POST | `/payment-requests` | Sí |
| POST | `/payment-requests/{id}/approve` | Sí |
| POST | `/payment-requests/{id}/reject` | Sí |
| POST | `/payouts/{id}/execute` | Sí |
| GET | `/ledger/{wallet_id}` | Sí |

Endpoints extra en MVP actual (no contradicen el PDF): listados y consultas por id para users, agents, funding orders, payment requests, approvals, payouts.

### Reglas mínimas del PDF

- No acreditar dos veces la misma `funding_order` ni el mismo `provider_event_id`.
- No aprobar un `payment_request` ya rechazado o completado.
- No reservar si `available_balance` &lt; monto.
- No ejecutar payout si el request no está en `reserved`.
- Si un payout falla, liberar reserva antes de reintentos; ejecutor serializado; evidencia mínima de ejecución.

### Estados (PDF)

- `funding_orders`: pending, credited, underpaid, overpaid, expired, failed.
- `payment_requests`: requested, **approved**, rejected, insufficient_funds, reserved, executing, completed, failed (+ impl citada: needs_manual_review).
- `payouts`: queued, executing, completed, failed, needs_manual_review.

---

## 2. Alineado con el documento

| Área | Evidencia |
|------|-----------|
| Capas separadas | Routers → `services` → `repositories` → Supabase; dominios: fondeo, webhook, ledger, payment requests + approvals, payouts. |
| FastAPI como orquestación | `app/main.py` registra todos los routers; reglas en servicios, no solo CRUD. |
| Ledger y tipos de movimiento | `ledger_service.py`: `funding_credit`, `reserve`, `release`, `payout_debit`, `manual_adjustment`; actualiza wallet y `balance_after_*`. |
| Flujo aprobación → reserva → cola payout | `payment_request_service.approve_payment_request`: crea `approval`, `RESERVE`, estado `reserved`, inserta payout `queued`. |
| Flujo payout | `payout_service.execute_payout`: exige payout `queued` y PR `reserved`; pasa a `executing`; éxito → `PAYOUT_DEBIT` + completado; fallo “normal” → `RELEASE` + `failed`. |
| Idempotencia webhook | `webhook_service.process_talo_webhook`: deduplica por `provider_event_id`; orden debe estar `pending` para aplicar. |
| Idempotencia payment request | `idempotency_key` con validación de mismo usuario y mismo payload. |
| Límites de agente | `default_spending_limit` en create PR. |
| Ownership approve/reject | Solo `user_id` dueño del PR. |
| Agente activo y del usuario | `_require_agent_for_user`. |
| Ejecutor serializado + timeout | `bank_executor.py`: `asyncio.Lock` global + `wait_for` timeout; logs básicos. |
| Integración Talo / MP como demo | `talo_client` mock; executor mock con `executor_run_id`, `provider_receipt_ref`, `failure_reason`. |
| Tabla `approvals` separada | Creación en approve/reject; listado por PR. |
| funding_events + raw_payload | Webhook persiste evento con payload para auditoría. |

---

## 3. Desalineado o sólo parcialmente alineado

| Tema | PDF | Implementación actual | Severidad |
|------|-----|------------------------|-----------|
| Estado `approved` en `payment_requests` | Transición explícita requested → **approved** → reserved | Tras aprobar se pasa directo a `reserved` (no existe `approved` en `PaymentRequestStatus`). | Baja (coherente con “recortar” approvals en el request; trazabilidad de “OK humano” sigue en tabla `approvals`). |
| Regla: liberar reserva si payout falla | Incluye escenarios de fallo antes de reintentos | Si el banco devuelve `needs_manual_review=True` (`payout_service`), **no** se hace `RELEASE`: el saldo queda reservado. | **Media-Alta** para reintentos operativos y coherencia con el texto del PDF sobre liberar antes de reintentar. |
| Doble acreditación `funding_order` | No repetir acreditación por misma orden | Además de `provider_event_id`, el estado `pending` bloquea un segundo webhook con otro id. Correcto. Si en el futuro se permitiera re-apertura de órdenes, habría que reforzar con idempotencia por orden. | OK hoy |
| Concurrencia reserva | Reservar sin doble gasto b paralelismo | Lectura/escritura wallet y ledger en pasos separados sin transacción única PostgreSQL desde la app. | **Alta** bajo carga concurrente (riesgo de carreras). |
| Autenticación | Usuario vía Supabase Auth; API no confía ciegamente en `user_id` | `user_id` en body/query; sin JWT/API key en routers. | **Alta** seguridad/demo seria; mitigación típica: RLS + anon key + JWT. |
| Webhook Talo | Idempotente y confiable | Sin verificación de firma/secreto en `webhooks.py`. | **Alta** si el endpoint es público. |
| `users.status` | Usuario lógicamente activo | `suspended` / `banned` no bloquean fondeo, pagos ni agentes. | Media |
| Un payout activo por `payment_request` | Flujo único implícito | `get_latest_for_payment_request` en repositorio no se usa en servicio; duplicados en BD serían posibles. | Media |
| Evidencia Selenium | Screenshots opcionales, errores legibles | Mock con texto de error y receipt; sin almacenamiento de screenshot. | Baja (MVP demo) |
| Tests automatizados | — | No hay suite de tests en el repo. | Media para regresiones |

---

## 4. Riesgos operativos (MVP / demo)

1. **Doble reserva o saldo inconsistente** si dos aprobaciones concurrentes leen el mismo `available_balance` antes de actualizar (mitigación típica: `SELECT ... FOR UPDATE` o RPC atómica en Postgres).
2. **`needs_manual_review`**: fondos pueden quedar congelados en `reserved` sin liberación automática; reintentar otro payout puede exigir intervención manual o un flujo no implementado.
3. **Éxito bancario + fallo de ledger**: ya contemplado como `needs_manual_review` en payout; riesgo de divergencia MP vs libros (correcto marcar revisión manual, pero proceso no automatizado).
4. **Clave Supabase**: si se usa service role desde el cliente server-side está bien; si algún cliente expone la misma clave, el modelo “user_id en body” es peligroso.

---

## 5. TODOs implícitos (no hay `TODO` en `.py`)

Prioridad sugerida:

| Prioridad | Ítem |
|-----------|------|
| Bloqueante para producción | AuthN/AuthZ (JWT / Supabase session), webhook secret/firma, endurecer concurrencia en reserva/acreditación. |
| Importante para alinear PDF al pie de la letra | Política explícita de `RELEASE` cuando payout queda `needs_manual_review` y se va a reintentar; o endpoint/admin para liberar. |
| Importante | Enforcement de `UserStatus` en operaciones sensibles; usar o eliminar `get_latest_for_payment_request` para un solo payout “activo” por PR. |
| Mejora MVP | Estado intermedio `approved` en PR si se quiere máquina de estados idéntica al PDF; tests de idempotencia y de máquina de estados. |

---

## 6. Conclusión

El backend **cumple la intención arquitectónica del PDF** para un MVP: capas separadas, ledger con reserva, idempotencia en webhook y payment requests, payouts encolados con executor serializado mock, y endpoints principales presentes.

Las **mayores brechas respecto al espíritu del documento** son: **falta de autenticación fuerte en la API**, **webhook sin validación de origen**, **concurrencia no transaccional en movimientos de wallet**, y el comportamiento de **`needs_manual_review` sin liberación de reservas** frente a la regla explícita del PDF sobre liberar antes de reintentos.
