# Alias Payments

Plataforma de pagos orientada a agentes: API backend, dashboard de operador, servidor MCP y flujos de solicitud, aprobación y transferencia saliente. Landing page: **[https://vigilant-clarity-production.up.railway.app](https://vigilant-clarity-production.up.railway.app)**

Las transferencias pueden tener cierta demora por los proveedores.

---

## Guía de demostración

Esta sección describe el recorrido completo para probar el proyecto. El flujo es: **Telegram → agente con MCP y skills → solicitud de pago → aprobación en el dashboard → transferencia saliente**.

La demo está montada con **Telegram + OpenClaw** porque es el stack más simple y estándar para mostrar este producto en poco tiempo. Eso no limita el producto: las **tools del MCP** y las **skills** son aplicables a **cualquier agente** que pueda conectarse al servidor MCP de Alias Payments (por ejemplo **Claude**, **GPT**, u otros tantos agentes con soporte MCP).

### 1. Instalar Telegram

Si aún no tenés Telegram, descargalo en tu dispositivo:

| Plataforma | Enlace |
|------------|--------|
| **iOS** | [App Store — Telegram](https://apps.apple.com/app/telegram-messenger/id686449807) |
| **Android** | [Google Play — Telegram](https://play.google.com/store/apps/details?id=org.telegram.messenger) |
| **Escritorio** (Windows, macOS, Linux) | [Telegram Desktop](https://desktop.telegram.org/) |

También podés ver todas las apps oficiales en [telegram.org/apps](https://telegram.org/apps).

### 2. Cuenta y acceso al agente

Para la demo, el equipo crea una **cuenta asociada a un agente** para que puedas probar el flujo de punta a punta sin configurar infraestructura propia.

### 3. Abrir el chat del bot en Telegram

Una vez en Telegram, entrá al chat del agente usando este enlace:

**[https://t.me/hackaton_openclaw_2026_bot](https://t.me/hackaton_openclaw_2026_bot)**

Ese bot está conectado a un **OpenClaw** desplegado en una instancia **EC2**. El agente ya tiene configuradas las **herramientas MCP** de este proyecto y las **skills** necesarias para operar.

La cuenta del bot está **fondeada por el equipo con aproximadamente $50** (sandbox / demo) para que puedas disparar solicitudes de pago reales del flujo.

### 4. Interactuar con el agente

En el chat podés pedirle tareas que impliquen un pago, por ejemplo:

- Pedir una **transferencia** a la cuenta de un amigo (recomendamos fuertemente probar de enviar $5 al alias de tu amigo que tenes cerca).
- Probar el escenario de **compra en la tienda mockeada que creamos para la demo** (El Refugio - Vende Milanesas) para usar el flujo de pago end-to-end. (Este flujo es exacatamente el mismo que se ve en el video de la demo).

El agente usará las tools MCP y las skills de Alias Payments para crear la **solicitud de pago** correspondiente.

### 5. Aprobar o rechazar la solicitud en el dashboard

Cuando el agente haya creado una solicitud de pago, **no se ejecuta la salida de fondos** hasta que vos la gestiones en el dashboard.

Primero en **Transactions** vas a ver la solicitud de pago pendiente, podes ver el estado de la solicitud y el monto. De ahí podes aprobar o rechazar la solicitud. En el caso de que la solicitud sea aceptada, es encolada. Para forzar la ejecución, ir a **Payouts** y ejecutar el payout.

Abrí el dashboard en:

**[https://motivated-laughter-production-edb2.up.railway.app/](https://motivated-laughter-production-edb2.up.railway.app/)**

Iniciá sesión con las **credenciales de sandbox** provistas para la demo:

| Campo | Valor |
|-------|--------|
| **Usuario** | `lucianoneimark@gmail.com` |
| **Contraseña** | `luciano12345` |

En el dashboard vas a encontrar:

| Sección | Qué ver / hacer |
|---------|------------------|
| **Overview** | Resumen general de la cuenta y actividad. |
| **Transactions** | Listado de solicitudes; desde acá **aprobás o rechazás** cada pedido pendiente. |
| **Agents** | Agentes asociados a este usuario. |
| **Payouts** | Historial de transferencias salientes (outbounds). |
| **Fundings** | Historial de ingresos (inbounds). En sandbox al estar fondeada la cuenta, no habrá actividad relevante. |

### 6. Qué pasa después de aprobar

Cuando se ejecuta el **payout**, se activa el flujo que **ejecuta la transferencia saliente** hacia el destino configurado en esa solicitud.

Si **rechazás** la solicitud, ese pago no se completa.
