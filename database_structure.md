# Modelo de datos recomendado

Para un MVP sólido se recomiendan **ocho tablas**. Si el tiempo aprieta, pueden implementarse primero seis y dejar auditoría fina y configuraciones para una segunda iteración.

---

## 3.1 `users`

| Campo | Tipo sugerido | Por qué existe | Ejemplo |
| --- | --- | --- | --- |
| `id` | uuid / bigint | Identificador interno del usuario. | `usr_123` |
| `auth_provider_user_id` | text | Referencia al usuario en Supabase Auth u otro sistema externo. | `7e3a...` |
| `email` | text | Contacto principal y login visible. | `luciano@example.com` |
| `username` | text | Nombre corto para CLI o UI. | `luciano` |
| `status` | text enum | Estado lógico del usuario. | `active` |
| `created_at` | timestamp | Auditoría temporal. | `2026-03-28 10:15` |
| `updated_at` | timestamp | Última modificación. | `2026-03-28 11:00` |

> **Nota de diseño.** Aunque sea una hackatón, conviene no guardar contraseñas propias. Lo más simple es delegar autenticación a Supabase Auth y almacenar solo el identificador externo.

---

## 3.2 `agents`

| Campo | Tipo sugerido | Por qué existe | Ejemplo |
| --- | --- | --- | --- |
| `id` | uuid / bigint | Identificador del agente. | `agt_001` |
| `user_id` | fk → `users.id` | Dueño del agente. | `usr_123` |
| `name` | text | Nombre visible del agente. | `research-agent` |
| `description` | text | Opcional. Explica qué hace. | Agente que investiga y paga paywalls. |
| `default_spending_limit` | numeric | Límite opcional por transacción o período. | `5000.00` |
| `is_active` | boolean | Permite desactivar el agente sin borrarlo. | `true` |
| `created_at` | timestamp | Auditoría temporal. | `2026-03-28 10:20` |
| `updated_at` | timestamp | Última modificación. | `2026-03-28 10:20` |

> **Nota de diseño.** Un usuario puede tener varios agentes. Por ejemplo, uno para investigación y otro para tareas operativas. Eso justifica separar `agents` de `users`.

---

## 3.3 `wallets`

| Campo | Tipo sugerido | Por qué existe | Ejemplo |
| --- | --- | --- | --- |
| `id` | uuid / bigint | Identificador de la wallet lógica. | `wal_001` |
| `user_id` | fk → `users.id` | Una wallet por usuario en el MVP. | `usr_123` |
| `currency` | text | Moneda del saldo. | `ARS` |
| `available_balance` | numeric | Saldo disponible para nuevas reservas. | `8500.00` |
| `reserved_balance` | numeric | Saldo ya comprometido en pagos aprobados. | `1200.00` |
| `created_at` | timestamp | Auditoría temporal. | `2026-03-28 10:15` |
| `updated_at` | timestamp | Última modificación. | `2026-03-28 11:30` |

> **Nota de diseño.** Se puede calcular el saldo exclusivamente desde `ledger_entries`, pero para el MVP es práctico materializar `available_balance` y `reserved_balance` en `wallets`. La fuente de verdad sigue siendo el ledger.

---

## 3.4 `funding_orders`

| Campo | Tipo sugerido | Por qué existe | Ejemplo |
| --- | --- | --- | --- |
| `id` | uuid / bigint | Identificador de la orden. | `fnd_001` |
| `user_id` | fk → `users.id` | Dueño de la orden. | `usr_123` |
| `wallet_id` | fk → `wallets.id` | Wallet que recibirá la acreditación. | `wal_001` |
| `requested_amount` | numeric | Monto esperado. | `10000.00` |
| `currency` | text | Moneda del fondeo. | `ARS` |
| `provider` | text | Proveedor del CVU. | `talo` |
| `provider_payment_id` | text | Identificador externo de Talo. | `pay_789` |
| `cvu` | text | CVU asignado a esa orden. | `0000003100...` |
| `alias` | text | Alias legible si existe. | `agentpay.demo.fondeo` |
| `status` | text enum | Estado de la orden. | `pending` / `credited` / `underpaid` / `overpaid` / `expired` / `failed` |
| `expires_at` | timestamp | Vencimiento del CVU u orden. | `2026-03-28 14:00` |
| `created_at` | timestamp | Auditoría temporal. | `2026-03-28 10:30` |
| `updated_at` | timestamp | Última modificación. | `2026-03-28 10:35` |

> **Nota de diseño.** `requested_amount` representa la intención original. Si luego el usuario paga de menos o de más, permite comparar el monto esperado con el recibido.

---

## 3.5 `funding_events`

| Campo | Tipo sugerido | Por qué existe | Ejemplo |
| --- | --- | --- | --- |
| `id` | uuid / bigint | Identificador interno del evento. | `fev_001` |
| `funding_order_id` | fk → `funding_orders.id` | Orden relacionada. | `fnd_001` |
| `provider_event_id` | text | Id externo o combinación única del provider. | `evt_123` |
| `provider_status` | text | Estado devuelto por el provider. | `SUCCESS` |
| `received_amount` | numeric | Monto efectivamente detectado. | `10000.00` |
| `raw_payload` | jsonb | Payload completo para auditoría. | `{...}` |
| `processed_at` | timestamp | Momento en que el backend procesó el evento. | `2026-03-28 10:42` |
| `created_at` | timestamp | Momento en que se recibió. | `2026-03-28 10:41` |

> **Nota de diseño.** Guarda el detalle de eventos de conciliación relacionados con una `funding_order`. Es importante para idempotencia y debugging de webhooks.

---

## 3.6 `payment_requests`

| Campo | Tipo sugerido | Por qué existe | Ejemplo |
| --- | --- | --- | --- |
| `id` | uuid / bigint | Identificador del request. | `prq_001` |
| `user_id` | fk → `users.id` | Usuario que financia el pago. | `usr_123` |
| `agent_id` | fk → `agents.id` | Agente que solicita el pago. | `agt_001` |
| `wallet_id` | fk → `wallets.id` | Wallet desde la que saldrá el saldo. | `wal_001` |
| `amount` | numeric | Monto pedido. | `1200.00` |
| `currency` | text | Moneda del pago. | `ARS` |
| `destination_cvu` | text | CVU/CBU destino informado por el agente. | `000000...` |
| `destination_alias` | text | Alias destino si existe. | `proveedor.demo` |
| `destination_holder_name` | text | Nombre visible del titular destino. | Juan Pérez |
| `purpose` | text | Motivo del pago. | Paywall de base de datos |
| `status` | text enum | Estado del request. | `requested` / `approved` / `rejected` / `insufficient_funds` / `reserved` / `executing` / `completed` / `failed` |
| `idempotency_key` | text | Evita duplicados del lado CLI o backend. | `sha256(...)` |
| `created_at` | timestamp | Auditoría temporal. | `2026-03-28 11:00` |
| `updated_at` | timestamp | Última modificación. | `2026-03-28 11:02` |

> **Nota de diseño.** Guardar `destination_holder_name` ayuda a mostrar al usuario no solo el CVU o alias sino también el titular esperado. Eso reduce errores y da más confianza en la demo.

---

## 3.7 `approvals`

| Campo | Tipo sugerido | Por qué existe | Ejemplo |
| --- | --- | --- | --- |
| `id` | uuid / bigint | Identificador de la aprobación. | `apr_001` |
| `payment_request_id` | fk → `payment_requests.id` | Request asociado. | `prq_001` |
| `user_id` | fk → `users.id` | Quién aprueba o rechaza. | `usr_123` |
| `decision` | text enum | `approved` / `rejected` | `approved` |
| `decision_reason` | text | Comentario opcional del usuario. | Pago legítimo |
| `approved_amount` | numeric | Monto finalmente autorizado. | `1200.00` |
| `created_at` | timestamp | Momento de la decisión. | `2026-03-28 11:03` |

> **Nota de diseño.** Separar `approvals` permite dejar trazabilidad clara de la decisión humana, incluso si después el request cambia de estado por falta de saldo, error del executor o reintentos.

---

## 3.8 `payouts`

| Campo | Tipo sugerido | Por qué existe | Ejemplo |
| --- | --- | --- | --- |
| `id` | uuid / bigint | Identificador del payout. | `pyo_001` |
| `payment_request_id` | fk → `payment_requests.id` | Request origen. | `prq_001` |
| `execution_provider` | text | Cómo se ejecutó. | `selenium_mercadopago` |
| `source_account_label` | text | Etiqueta de la cuenta pool usada. | `mp_pool_demo` |
| `destination_cvu` | text | CVU/CBU efectivamente usado. | `000000...` |
| `destination_alias` | text | Alias destino si se usó. | `proveedor.demo` |
| `amount` | numeric | Monto a transferir. | `1200.00` |
| `currency` | text | Moneda. | `ARS` |
| `status` | text enum | Estados del payout. | `queued` / `executing` / `completed` / `failed` / `needs_manual_review` |
| `executor_run_id` | text | Id del intento en el módulo Selenium. | `run_9081` |
| `provider_receipt_ref` | text | Comprobante o referencia externa si existe. | `op_123456` |
| `failure_reason` | text | Error legible si falla. | Sesión expirada en Mercado Pago |
| `created_at` | timestamp | Auditoría temporal. | `2026-03-28 11:04` |
| `updated_at` | timestamp | Última modificación. | `2026-03-28 11:05` |

> **Nota de diseño.** Representa la ejecución real de una transferencia saliente.

---

## 3.9 `ledger_entries`

| Campo | Tipo sugerido | Por qué existe | Ejemplo | Notas |
| --- | --- | --- | --- | --- |
| `id` | uuid / bigint | Identificador del movimiento. | `led_001` | |
| `wallet_id` | fk → `wallets.id` | Wallet impactada. | `wal_001` | |
| `entry_type` | text enum | Tipo de movimiento. | `funding_credit` | Otros: `reserve`, `release`, `payout_debit`, `manual_adjustment` |
| `direction` | text enum | `credit` / `debit` | `credit` | Hace más clara la lectura |
| `amount` | numeric | Monto del movimiento. | `10000.00` | |
| `currency` | text | Moneda. | `ARS` | |
| `reference_type` | text | Tipo del objeto relacionado. | `funding_order` | o `payment_request` / `payout` |
| `reference_id` | text | Id del objeto relacionado. | `fnd_001` | |
| `balance_after_available` | numeric | Saldo disponible luego del movimiento. | `10000.00` | Materializado para debugging |
| `balance_after_reserved` | numeric | Saldo reservado luego del movimiento. | `0.00` | Materializado para debugging |
| `description` | text | Texto humano explicativo. | Acreditación de fondeo Talo | |
| `created_at` | timestamp | Auditoría temporal. | `2026-03-28 10:42` | |

### Ejemplos de movimientos de ledger

| Momento | `entry_type` | Impacto en `available` | Impacto en `reserved` |
| --- | --- | --- | --- |
| Llega el fondeo | `funding_credit` | +10.000 | 0 |
| Se aprueba el pago y se reserva | `reserve` | −1.200 | +1.200 |
| La ejecución falla y se libera | `release` | +1.200 | −1.200 |
| La ejecución completa y se debita | `payout_debit` | 0 | −1.200 |

---

# Estados y máquinas de estado

Modelar estados explícitos evita `if`s difusos y hace que la demo sea entendible.

## 4.1 `funding_orders`

| Estado | Significado | Transiciones típicas |
| --- | --- | --- |
| `pending` | La orden fue creada y espera pago. | `credited` / `underpaid` / `overpaid` / `expired` / `failed` |
| `credited` | El monto esperado o aceptable ya fue acreditado. | final |
| `underpaid` | El usuario mandó menos de lo esperado. | `credited` o final según regla |
| `overpaid` | El usuario mandó más de lo esperado. | `credited` o revisión |
| `expired` | El plazo venció sin pago válido. | final |
| `failed` | Hubo un error operativo o de conciliación. | revisión manual |

## 4.2 `payment_requests`

| Estado | Significado | Transiciones típicas |
| --- | --- | --- |
| `requested` | El agente pidió un pago. | `approved` / `rejected` / `insufficient_funds` |
| `approved` | El usuario dio ok. | `reserved` / `insufficient_funds` |
| `rejected` | El usuario lo rechazó. | final |
| `insufficient_funds` | No hay saldo suficiente. | `requested` luego de refondear |
| `reserved` | El saldo quedó comprometido. | `executing` / `failed` |
| `executing` | Existe un payout en curso. | `completed` / `failed` / `needs_manual_review` |
| `completed` | Pago ejecutado y saldo consumido. | final |
| `failed` | No se pudo completar. | `requested` o revisión manual |
