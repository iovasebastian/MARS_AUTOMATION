# SYSTEM DESCRIPTION:

The Mars Habitat Automation Platform is a distributed, event-driven system designed to monitor and control a fragile habitat on Mars. The system architecture is divided into decoupled layers: data ingestion, event processing/automation, and a real-time presentation dashboard. 

# USER STORIES:

1. As a system backend, I want to periodically poll REST sensors every few seconds, so that I can capture the latest environmental states.
2. As a system backend, I want to subscribe to WebSocket/SSE telemetry topics, so that I can capture real-time power and life support metrics.
3. As a data processing service, I want to normalize all heterogeneous REST and Telemetry payloads into a single standard event schema, so that downstream services can process them uniformly.
4. As an ingestion service, I want to publish normalized events to a central RabbitMQ message broker, so that the architecture remains decoupled and event-driven.
5. As an automation service, I want to consume events from the message broker in real-time, so that I can evaluate them against active rules immediately upon arrival.
6. As a database service, I want to persist automation rules in an SQLite database, so that rules are not lost during a system restart.
7. As an automation service, I want to compare incoming sensor values against rule operators, so that I can determine if an action is required.
8. As an automation service, I want to send a POST request to the actuator API when a rule condition is met, so that the physical habitat environment is adjusted.
9. As a system backend, I want to maintain the latest state of each sensor in an in-memory cache, so that the frontend can load current states instantly without querying the broker.
10. As an operator, I want to view a real-time dashboard, so that I can monitor the overall health of the Mars base at a glance.
11. As an operator, I want to see the latest values of REST sensors, so that I know the status of vital resources.
12. As an operator, I want to see a live updating line chart for telemetry streams, so that I can observe trends while the page is open.
13. As a frontend client, I want to receive real-time sensor updates via WebSocket, so that the dashboard UI reflects changes without manual browser refreshes.
14. As an operator, I want to see the current state (ON/OFF) of all actuators, so that I know which environmental controls are active.
15. As an operator, I want to manually toggle an actuator's state (ON/OFF) from the dashboard, so that I can override the system in an emergency.
16. As an operator, I want to view a list of all active automation rules in the dashboard UI, so that I know what automated actions the system is evaluating.
17. As an operator, I want to create a new IF-THEN rule via the frontend interface, so that I can automate responses to new environmental threats.
18. As an operator, I want to delete or disable an existing automation rule from the dashboard, so that I can stop unwanted actuator triggers.
19. As an operator, I want to edit existing automation rules so that automation behavior can be adjusted when conditions change.
20. As the system, I want to automatically discover available sensors from the simulator API so that new devices can be integrated without manual configuration.


# CONTAINERS:

## CONTAINER_NAME: ingestion-service

### DESCRIPTION: 
Manages the data retrieval from the Mars IoT Simulator, normalizes heterogenous payloads, and publishes standardized events to the RabbitMQ broker.

### USER STORIES:
1, 2, 3, 4, 20

### PORTS: 
None exposed externally (Internal network communication only).

### PERSISTENCE EVALUATION
The ingestion-service does not require data persistence. It acts purely as a stateless data forwarder.

### EXTERNAL SERVICES CONNECTIONS
Connects to the externally provided `simulator` container on port 8080.

### MICROSERVICES:

#### MICROSERVICE: ingestion-be
- TYPE: backend
- DESCRIPTION: Fetches raw data, formats it into a standard schema, and publishes to RabbitMQ via AMQP.
- PORTS: 8001
- TECHNOLOGICAL SPECIFICATION:
Developed in Python using the FastAPI framework. It utilizes `requests` for REST polling, `websockets` for telemetry streams, and `pika` (or `aio_pika`) to connect to the RabbitMQ broker.
- SERVICE ARCHITECTURE: 
A headless script running asyncio event loops to concurrently manage polling and streaming tasks without blocking.

- ENDPOINTS: 
	| HTTP METHOD | URL  | Description                                                  | User Stories |
	| ----------- | ---- | ------------------------------------------------------------ | ------------ |
	| N/A         | N/A  | This is a background producer service with no exposed HTTP endpoints. | 1, 2, 3, 4   |


## CONTAINER_NAME: broker

### DESCRIPTION: 
Provides asynchronous publish/subscribe communication between the decoupled microservices using AMQP.

### USER STORIES:
4, 5, 13

### PORTS: 
5672:5672 (AMQP)
15672:15672 (Management UI)

### PERSISTENCE EVALUATION
Configured for transient message passing to maximize throughput. 

### EXTERNAL SERVICES CONNECTIONS
No external connections.

### MICROSERVICES:

#### MICROSERVICE: rabbitmq-broker
- TYPE: middleware
- DESCRIPTION: Standard RabbitMQ image acting as the message broker.
- PORTS: 5672, 15672
- TECHNOLOGICAL SPECIFICATION:
Official `rabbitmq:3-management` Docker image.
- SERVICE ARCHITECTURE: 
Topic-based exchange architecture to route sensor data to respective queues.


## CONTAINER_NAME: automation-service

### DESCRIPTION: 
Evaluates incoming events against persisted automation rules and triggers actuators.

### USER STORIES:
5, 6, 7, 8, 9

### PORTS: 
None exposed externally.

### PERSISTENCE EVALUATION
Requires an embedded SQLite database (`rules.db`) mounted via a shared Docker Volume to persist user-defined automation rules, ensuring survival across container restarts.

### EXTERNAL SERVICES CONNECTIONS
Connects to the Mars IoT Simulator actuator endpoints to send POST requests.

### MICROSERVICES:

#### MICROSERVICE: automation-be
- TYPE: backend
- DESCRIPTION: Subscribes to RabbitMQ queues, evaluates rules via SQLite, and commands the simulator.
- PORTS: 8002
- TECHNOLOGICAL SPECIFICATION:
Developed in Python using FastAPI. Uses SQLAlchemy as the ORM to interact with the shared SQLite volume, and `pika` to consume messages from RabbitMQ.
- SERVICE ARCHITECTURE: 
Event-driven worker using an in-memory dictionary for sensor states and querying the SQLite rule table dynamically.

- DB STRUCTURE: 
	**_Rule_** :	| **_id_** | sensor_name | operator | threshold_value | actuator_name | action_state |


## CONTAINER_NAME: api-service

### DESCRIPTION: 
Provides REST API endpoints for rule management and a WebSocket connection for the frontend dashboard.

### USER STORIES:
13, 15, 16, 17, 18, 19

### PORTS: 
8003:8003

### PERSISTENCE EVALUATION
Connects to the same SQLite Docker Volume as the `automation-service` to perform CRUD operations on rules.

### EXTERNAL SERVICES CONNECTIONS
No external connections.

### MICROSERVICES:

#### MICROSERVICE: api-be
- TYPE: backend
- DESCRIPTION: Exposes WebSocket streams and rule CRUD endpoints for the React frontend.
- PORTS: 8003
- TECHNOLOGICAL SPECIFICATION:
Built with Python FastAPI. Uses Pydantic for data validation and SQLAlchemy for database interactions with the shared SQLite `.db` file.
- SERVICE ARCHITECTURE: 
RESTful API for rule management and an active WebSocket route that consumes from RabbitMQ and forwards messages to connected React clients.
- ENDPOINTS: 
	| HTTP METHOD | URL | Description | User Stories |
	| ----------- | --- | ----------- | ------------ |
	| GET | /api/rules | Retrieves all active automation rules | 16 |
	| POST | /api/rules | Creates a new automation rule | 17 |
	| PUT | /api/rules/{id} | Edits an existing automation rule | 19 |
	| DELETE | /api/rules/{id} | Deletes an existing rule | 18 |
	| POST | /api/actuators/{name} | Manually toggles an actuator | 15 |
	| WS | /ws/stream | WebSocket for real-time sensor updates | 13 |
- DB STRUCTURE: 
  **_Rule_** :	| **_id_** | sensor_name | operator | threshold_value | actuator_name | action_state |


## CONTAINER_NAME: frontend

### DESCRIPTION: 
Provides the real-time graphical user interface for habitat operators.

### USER STORIES:
10, 11, 12, 13, 14, 15, 16, 17, 18, 19

### PORTS: 
3000:3000

### PERSISTENCE EVALUATION
No database is included.

### EXTERNAL SERVICES CONNECTIONS
No external connections.

### MICROSERVICES:

#### MICROSERVICE: client-fe
- TYPE: frontend

- DESCRIPTION: Serves the main user interface.

- PORTS: 3000

- TECHNOLOGICAL SPECIFICATION:
  Developed using React.js. Communicates with `api-service` via REST (axios/fetch) for rules and native WebSockets for real-time telemetry.

- PAGES:
	| Name      | Description                                                  | Related Microservice | User Stories                           |
	| --------- | ------------------------------------------------------------ | -------------------- | -------------------------------------- |
	| Dashboard | Main monitoring page with charts, actuator toggles, and rule tables | api-service          | 10, 11, 12, 13, 14, 15, 16, 17, 18, 19 |

	