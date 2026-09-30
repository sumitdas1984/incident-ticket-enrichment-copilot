# Alarm Management API — Specification

This folder is the authoritative contract for the Alarm Management API used throughout the project. The Postman collections here define every endpoint, request schema, response structure, authentication header, trace header, pagination convention, and multi-step chaining flow that the Alarm API simulator MUST implement.

The simulator shipped with the project is the source of truth for local development and integration tests, and its behaviour is validated against these collections.

---

## Collections

| File | Purpose |
| --- | --- |
| `Alarm-API-Simulator.postman_collection.json` | Full end-to-end baseline of all Alarm Management API endpoints. Use as the implementation reference for the simulator. |
| `scenarios/Alarm-API-Scenarios.postman_collection.json` | Scenario-focused request tests. Use to validate individual endpoint behaviour under realistic payloads. |
| `chaining/Alarm-API-Chaining.postman_collection.json` | Multi-step chaining flows where the output of one request feeds into the next. Use to validate orchestration logic and trace propagation. |

---

## Contract conventions

### Base URL

Provided by the collection variable `{{baseUrl}}`. The simulator is expected to honour this variable. The default in the collection is intended for local development.

### Authentication

Every authenticated request carries:

```
Authorization: Bearer {{token}}
```

The token is supplied via the collection variable `{{token}}`. The simulator validates the token against its configured auth secret and rejects unauthenticated calls.

### Trace metadata

Every request includes a correlation identifier propagated end-to-end:

```
X-Correlation-Id: {{correlation_id}}
```

The simulator is required to echo this header on every response so that an MCP tool invocation can be traced from the user request through the LLM, the MCP client, the MCP server, the Alarm API simulator, and back.

### Pagination

List endpoints accept:

| Parameter | Type | Description |
| --- | --- | --- |
| `page` | integer | 1-indexed page number |
| `page_size` | integer | Items per page (default and max enforced by the simulator) |

List responses follow the shape:

```json
{
  "items": [],
  "page": 1,
  "page_size": 50,
  "total": 0
}
```

### Chaining

Chaining flows use Postman test scripts to capture outputs of one request into environment variables consumed by the next. The simulator is expected to be deterministic enough that chained flows can be replayed reliably.

### Error responses

Errors follow the shape:

```json
{
  "error": {
    "code": "string",
    "message": "string",
    "correlation_id": "string"
  }
}
```

---

## Validating the simulator

The simulator MUST pass the full baseline collection before any release that touches the Alarm API surface. Scenarios and chaining flows add additional confidence but are not blocking unless explicitly listed in the release checklist.

```bash
# Using Newman against a running simulator
newman run specs/alarm-api/Alarm-API-Simulator.postman_collection.json \
  --env-var "baseUrl=http://localhost:8000" \
  --env-var "token=$ALARM_API_TOKEN"

# Scenarios
newman run specs/alarm-api/scenarios/Alarm-API-Scenarios.postman_collection.json \
  --env-var "baseUrl=http://localhost:8000" \
  --env-var "token=$ALARM_API_TOKEN"

# Chaining
newman run specs/alarm-api/chaining/Alarm-API-Chaining.postman_collection.json \
  --env-var "baseUrl=http://localhost:8000" \
  --env-var "token=$ALARM_API_TOKEN"
```

---

## Extending the contract

When adding a new endpoint or changing an existing one:

1. Update the relevant collection(s) here **first** — the spec is the source of truth.
2. Implement the change in the simulator.
3. Add or update a chaining flow if the new endpoint participates in orchestration.
4. Update the MCP tool that wraps the endpoint (the tool catalog mirrors the contract).
5. Re-run the full validation suite.

Contract changes are not merged without simulator and MCP tool coverage.
