# USER STORIES:

1) As a system backend, I want to periodically poll REST sensors every few seconds, so that I can capture the latest environmental states.
2) As a system backend, I want to subscribe to WebSocket/SSE telemetry topics, so that I can capture real-time power and life support metrics.
3) As a data processing service, I want to normalize all heterogeneous REST and Telemetry payloads into a single standard event schema, so that downstream services can process them uniformly.
4) As an ingestion service, I want to publish normalized events to a central RabbitMQ message broker, so that the architecture remains decoupled and event-driven.
5) As an automation service, I want to consume events from the message broker in real-time, so that I can evaluate them against active rules immediately upon arrival.
6) As a database service, I want to persist automation rules in an SQLite database, so that rules are not lost during a system restart.
7) As an automation service, I want to compare incoming sensor values against rule operators, so that I can determine if an action is required.
8) As an automation service, I want to send a POST request to the actuator API when a rule condition is met, so that the physical habitat environment is adjusted.
9) As a system backend, I want to maintain the latest state of each sensor in an in-memory cache, so that the frontend can load current states instantly without querying the broker.
10) As an operator, I want to view a real-time dashboard, so that I can monitor the overall health of the Mars base at a glance.
11) As an operator, I want to see the latest values of REST sensors, so that I know the status of vital resources.
12) As an operator, I want to see a live updating line chart for telemetry streams, so that I can observe trends while the page is open.
13) As a frontend client, I want to receive real-time sensor updates via WebSocket, so that the dashboard UI reflects changes without manual browser refreshes.
14) As an operator, I want to see the current state (ON/OFF) of all actuators, so that I know which environmental controls are active.
15) As an operator, I want to manually toggle an actuator's state (ON/OFF) from the dashboard, so that I can override the system in an emergency.
16) As an operator, I want to view a list of all active automation rules in the dashboard UI, so that I know what automated actions the system is evaluating.
17) As an operator, I want to create a new IF-THEN rule via the frontend interface, so that I can automate responses to new environmental threats.
18) As an operator, I want to delete or disable an existing automation rule from the dashboard, so that I can stop unwanted actuator triggers.
19) As an operator, I want to edit existing automation rules so that automation behavior can be adjusted when conditions change.
20) As the system, I want to automatically discover available sensors from the simulator API so that new devices can be integrated without manual configuration.