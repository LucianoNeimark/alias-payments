# AgentPay Skill — Pagos en pesos con CVU

AgentPay te permite realizar transferencias bancarias en pesos argentinos de forma autónoma. Usá esta skill cuando necesites pagar a una persona o entidad que tenga un alias o CVU.

---

## Configuración MCP

Para usar esta skill, AgentPay debe estar configurado como servidor MCP en tu agente. Agregá esto a tu configuración de MCP:

```json
{
  "mcpServers": {
    "agentpay": {
      "url": "https://awake-enthusiasm-production-0cee.up.railway.app/mcp"
    }
  }
}
```

Una vez conectado, el agente puede invocar las tools de AgentPay directamente.

---

## Cuándo usar esta skill

Cuando necesitás ejecutar un pago en pesos a un destino que tenga alias o CVU argentino.

---

## Reglas obligatorias

### Antes de solicitar un pago

1. **Si el chat es nuevo**, no uses ningún `agent_id` previo — creá uno nuevo con `generate_agent`.

2. **Obtené la configuración del agente** con `get_agent_config`. Verificá que `is_active` sea `true` y registrá el `default_spending_limit`.

3. **Consultá el balance disponible** con `get_balance`. Si el saldo disponible es menor al monto que querés pagar, **no hagas el payment request** — preguntale al usuario si quiere:
   - Ajustar el monto al saldo disponible, o
   - Fondear más dinero.
   Si decide fondear, generá un nuevo CVU con `generate_cvu` indicando el monto necesario. Aclarále al usuario que **es una cuenta de sandbox** y que no tiene que transferir nada — el sistema simula automáticamente el ingreso del dinero.

4. **Verificá que el monto no supere el `default_spending_limit`**. Si lo supera, no solicites el pago y avisale al usuario.

### Al crear el payment request

El mínimo requerido es:

- `alias` o `cvu` del destinatario
- `amount` — monto en pesos
- `user_id`
- `agent_id`
- `purpose` (muy recomendado) — descripción clara del motivo del pago (ej: "Pago a diseñador freelance por logo"). Es lo que el usuario ve para decidir si aprueba o rechaza.
- `idempotency_key` — generá una clave única por intento. Si reintentás por cualquier motivo, usá la misma clave para evitar pagos duplicados.

### Después de crear el payment request

- El pago **no se ejecuta inmediatamente**. Queda en estado `requested` esperando aprobación humana. No asumas que el pago ya se realizó.
- Consultá el estado con `get_payment_request` para saber si avanzó.

---

## Estados del payment request

| Estado | Significado | Qué hacer |
|---|---|---|
| `requested` | Esperando aprobación del usuario | Esperar |
| `approved` | Aprobado, reservando fondos | Esperar |
| `reserved` | Fondos reservados, ejecutando | Esperar |
| `executing` | Transferencia en curso | Esperar |
| `completed` | Pago exitoso ✅ | Continuar con la tarea |
| `failed` | Falló la ejecución | Avisarle al usuario, no reintentar solo |
| `needs_manual_review` | Requiere revisión humana | Esperar instrucción del usuario, no hacer nada |
| `rejected` | El usuario rechazó el pago | Avisarle al usuario y detener |

---

## Tools disponibles

| Tool | Cuándo usarla |
|---|---|
| `generate_agent` | Al inicio de cada chat nuevo, para crear un agente |
| `get_agent_config` | Para verificar límites y estado del agente |
| `get_balance` | Antes de cada payment request |
| `generate_cvu` | Cuando el usuario necesita fondear — genera un CVU de sandbox |
| `request_payment` | Para crear una solicitud de pago |
| `get_payment_request` | Para consultar el estado de un pago |
| `list_payment_requests` | Para ver el historial de pagos del usuario |

---

## Flujo típico

```
1. generate_agent           → crear agente si el chat es nuevo
2. get_agent_config         → verificar is_active y spending_limit
3. get_balance              → verificar saldo disponible
4. (si falta saldo)         → generate_cvu y simular fondeo en sandbox
5. request_payment          → crear solicitud con todos los campos requeridos
6. [esperar aprobación humana]
7. get_payment_request      → consultar hasta que status = "completed"
```

---

## Importante

- Nunca ejecutes pagos sin verificar el balance primero.
- Nunca asumas que un pago se completó sin confirmar el status `completed`.
- Ante cualquier estado de error, avisá al usuario — no tomes decisiones autónomas.
- En sandbox, el usuario nunca tiene que transferir dinero real — siempre usá `generate_cvu` y el sistema simula el ingreso.
