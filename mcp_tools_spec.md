# AgentPay MCP Tools -- Especificación

## Contexto

Los **agentes** (AI agents) interactúan con AgentPay exclusivamente a través de estas tools.
Las acciones del **usuario humano** (registrarse, fondear, aprobar/rechazar pagos) se hacen desde la web o clickeando una URL. No se exponen como tools.

```
┌──────────────┐         MCP tools           ┌──────────────┐
│   AI Agent   │ ──────────────────────────── │   AgentPay   │
└──────────────┘                              │   FastAPI    │
                                              └──────┬───────┘
┌──────────────┐      Web / URL clicks               │
│   Usuario    │ ────────────────────────────────────-┘
└──────────────┘
```

## Resumen de tools

| # | Tool | Qué hace | Quién lo usa |
|---|------|----------|--------------|
| 1 | `get_balance` | Consulta saldo disponible y reservado del usuario | Agent |
| 2 | `request_payment` | Crea una solicitud de pago a un CVU destino | Agent |
| 3 | `get_payment_request` | Consulta el estado de una solicitud de pago | Agent |
| 4 | `list_payment_requests` | Lista las solicitudes de pago del usuario | Agent |
| 5 | `get_agent_config` | Obtiene la configuración del agente (límites, estado) | Agent |

---

## 1. `get_balance`

Consultar el saldo de la wallet del usuario para saber si hay fondos disponibles antes de solicitar un pago.

**Cuándo usarla:** Antes de crear un `request_payment`, o cuando el agente necesita informar al usuario cuánto saldo tiene.

### Input

```json
{
  "user_id": "uuid -- ID del usuario dueño del agente"
}
```

### Output

```json
{
  "wallet_id": "uuid",
  "currency": "ARS",
  "available_balance": 8500.00,
  "reserved_balance": 1200.00
}
```

### Mapeo a API

```
GET /wallets/{user_id}
```

---

## 2. `request_payment`

Crear una solicitud de pago. El agente indica destino, monto y motivo. La solicitud queda en estado `requested` hasta que el usuario la apruebe o rechace.

**Cuándo usarla:** Cuando el agente necesita pagar algo en nombre del usuario (paywall, suscripción, compra, etc.).

### Input

```json
{
  "user_id": "uuid -- ID del usuario que financia el pago",
  "agent_id": "uuid -- ID del agente que solicita",
  "amount": 1200.00,
  "currency": "ARS",
  "destination_cvu": "0000000000000000000001",
  "destination_alias": "proveedor.demo",
  "destination_holder_name": "Juan Pérez",
  "purpose": "Pago de paywall para acceder a base de datos de investigación",
  "idempotency_key": "unique-string-para-evitar-duplicados"
}
```

| Campo | Requerido | Descripción |
|-------|-----------|-------------|
| `user_id` | si | Usuario dueño de la wallet |
| `agent_id` | si | Agente que solicita el pago |
| `amount` | si | Monto mayor a 0 |
| `currency` | no | Default `ARS` |
| `destination_cvu` | si | CVU o CBU destino |
| `destination_alias` | no | Alias destino (ej: `proveedor.demo`) |
| `destination_holder_name` | no | Nombre del titular destino |
| `purpose` | si | Motivo legible del pago |
| `idempotency_key` | si | Clave única para evitar duplicados; si se reenvía el mismo key con el mismo payload, retorna la solicitud existente |

### Output

```json
{
  "id": "uuid",
  "status": "requested",
  "amount": 1200.00,
  "currency": "ARS",
  "destination_cvu": "0000000000000000000001",
  "destination_alias": "proveedor.demo",
  "destination_holder_name": "Juan Pérez",
  "purpose": "Pago de paywall para acceder a base de datos de investigación",
  "created_at": "2026-03-28T11:00:00Z"
}
```

### Errores esperados

| Caso | Error |
|------|-------|
| Usuario no existe | `404 User not found` |
| Agente no pertenece al usuario | `403 Agent does not belong to this user` |
| Agente desactivado | `400 Agent is not active` |
| Monto excede `default_spending_limit` del agente | `400 Amount exceeds agent default_spending_limit` |
| `idempotency_key` reusada con payload distinto | `409 Idempotency key reused with different payload` |

### Mapeo a API

```
POST /payment-requests/
```

---

## 3. `get_payment_request`

Consultar el estado actual de una solicitud de pago. Útil para que el agente haga polling después de crear una solicitud y espere a que el usuario la apruebe.

**Cuándo usarla:** Después de un `request_payment`, para verificar si el usuario ya aprobó, rechazó, o si el pago ya se ejecutó.

### Input

```json
{
  "payment_request_id": "uuid"
}
```

### Output

```json
{
  "id": "uuid",
  "status": "completed",
  "amount": 1200.00,
  "currency": "ARS",
  "destination_cvu": "0000000000000000000001",
  "purpose": "Pago de paywall para acceder a base de datos de investigación",
  "created_at": "2026-03-28T11:00:00Z",
  "updated_at": "2026-03-28T11:05:00Z"
}
```

### Estados posibles

| Estado | Significado | Acción del agente |
|--------|-------------|-------------------|
| `requested` | Esperando aprobación del usuario | Esperar / informar al usuario |
| `rejected` | El usuario rechazó | Notificar; no reintentar |
| `insufficient_funds` | Fondos insuficientes al intentar reservar | Sugerir al usuario que fondee |
| `reserved` | Fondos reservados, pago encolado | Esperar ejecución |
| `executing` | Transferencia bancaria en curso | Esperar |
| `completed` | Pago ejecutado exitosamente | Confirmar al usuario |
| `failed` | Falló la ejecución bancaria | Puede reintentarse |
| `needs_manual_review` | Requiere intervención humana | Informar al usuario |

### Mapeo a API

```
GET /payment-requests/{payment_request_id}
```

---

## 4. `list_payment_requests`

Listar las solicitudes de pago del usuario, para que el agente pueda revisar el historial o encontrar pagos pendientes.

**Cuándo usarla:** Para mostrar un resumen de pagos o verificar si ya existe una solicitud antes de crear una nueva.

### Input

```json
{
  "user_id": "uuid",
  "limit": 20,
  "offset": 0
}
```

| Campo | Requerido | Descripción |
|-------|-----------|-------------|
| `user_id` | si | Usuario dueño |
| `limit` | no | Default 50, max 100 |
| `offset` | no | Default 0 |

### Output

```json
[
  {
    "id": "uuid",
    "status": "completed",
    "amount": 1200.00,
    "destination_cvu": "0000000000000000000001",
    "purpose": "Paywall base de datos",
    "created_at": "2026-03-28T11:00:00Z"
  }
]
```

### Mapeo a API

```
GET /payment-requests/?user_id={user_id}&limit={limit}&offset={offset}
```

---

## 5. `get_agent_config`

Obtener la configuración del agente: nombre, límite de gasto, si está activo. Permite al agente saber sus propios límites antes de solicitar un pago.

**Cuándo usarla:** Al inicio de una sesión o antes de un pago que podría exceder el límite.

### Input

```json
{
  "agent_id": "uuid"
}
```

### Output

```json
{
  "id": "uuid",
  "name": "research-agent",
  "description": "Agente que investiga y paga paywalls",
  "default_spending_limit": 5000.00,
  "is_active": true
}
```

### Mapeo a API

```
GET /agents/{agent_id}
```

---

## Flujo típico del agente

```
1. get_agent_config        → Conocer sus límites
2. get_balance             → Verificar fondos disponibles
3. request_payment         → Solicitar el pago
4. get_payment_request     → Polling hasta que el usuario apruebe
   (el usuario aprueba desde la web)
5. get_payment_request     → Confirmar que el pago se completó
```

## Qué NO hace el agente (acciones del usuario)

| Acción | Interfaz | Por qué no es tool |
|--------|----------|--------------------|
| Registrarse | Web | Acción única de onboarding |
| Fondear wallet | Web + transferencia bancaria | Requiere CVU + transferencia desde home banking |
| Aprobar pago | Web / URL click | Decisión humana explícita (seguridad) |
| Rechazar pago | Web / URL click | Decisión humana explícita |
| Ejecutar payout | Sistema automático | Lo dispara el backend, no el agente |
| Ver ledger | Web | Auditoría para el usuario, no para el agente |