# CredApp Notification Service

The notification microservice delivers asynchronous notifications for the CredApp platform. It is designed for horizontal scalability and communicates via RabbitMQ to decouple notification delivery from the main workflow.

## Features

- FastAPI-powered HTTP API for enqueuing notification events.
- Asynchronous message publishing and consumption using RabbitMQ (`aio-pika`).
- Pluggable dispatcher that can be extended with e-mail, SMS, push, and in-app channels.
- Configurable via environment variables using `pydantic-settings`.
- Lifespan hooks ensure graceful startup, shutdown, and resource cleanup.
- Built-in rule engine that maps core CredApp events across issuer, learner, and employer roles.

## Getting Started

1. **Install dependencies**

   ```powershell
   cd notification_service
   ..\backend1\venv\Scripts\python -m pip install -r requirements.txt
   ```

2. **Export environment variables (optional)**

   Create an `.env` file in `notification_service` to override defaults.

   ```env
   APP_NAME=CredApp Notification Service
   RABBITMQ_URL=amqp://guest:guest@localhost:5672/
   RABBITMQ_EXCHANGE=notifications.exchange
   RABBITMQ_QUEUE=notifications.queue
   ```

3. **Run RabbitMQ**

   Ensure RabbitMQ is running locally or reachable from the configured URL. Example with Docker:

   ```bash
   docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
   ```

4. **Start the service**

   ```powershell
   ..\backend1\venv\Scripts\uvicorn app.main:app --reload --host 0.0.0.0 --port 8500
   ```

## API

- `POST /api/v1/notifications` – enqueue a notification event.

Example request body:

```json
{
  "event_type": "credential.issued",
  "actor_role": "issuer",
  "recipients": ["learner@example.com"],
  "subject": "Your credential is ready",
  "body": "Congratulations! Your credential has been issued.",
  "metadata": {
    "credential_id": "abc123"
  }
}
```

### Built-in event defaults

The rule engine enriches requests with default channels and audiences when you omit them:

| Event | Actor role | Default recipients | Default channels | Use case |
| ----- | ---------- | ------------------ | ---------------- | -------- |
| `credential.issued` | `issuer` | `learner` | `email`, `in_app` | Notify learner when issuer issues a document |
| `credential.updated` | `issuer` | `learner` | `email`, `in_app` | Credential metadata updated |
| `credential.revoked` | `issuer` | `learner` | `email`, `in_app` | Credential revoked |
| `profile.viewed` | `employer` | `learner` | `in_app` | Employer viewed learner profile |
| `employer.requested_verification` | `employer` | `issuer` | `email`, `in_app` | Employer sought verification from issuer |

Override channels by passing a `channels` array, and override audiences via `recipient_roles`. The service always requires explicit `recipients` (email addresses, phone numbers, or internal IDs) so downstream transports know where to deliver.

## Scaling

- Deploy multiple instances of the service to scale consumers horizontally; RabbitMQ handles load balancing across consumers.
- Adjust `RABBITMQ_PREFETCH_COUNT` and `WORKER_CONCURRENCY` to tune throughput.
- Extend `NotificationDispatcher` to integrate with real delivery providers (e.g. AWS SES, Twilio, Firebase Cloud Messaging).

## Testing

- You can publish messages directly to RabbitMQ using the provided API or management UI to validate end-to-end flows.
- Add unit tests around the dispatcher as new delivery channels are implemented.


