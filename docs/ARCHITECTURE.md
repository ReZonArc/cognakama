# Nakama Technical Architecture Documentation

This document provides a comprehensive overview of the Nakama game server architecture, including detailed diagrams and explanations of system components, data flows, and deployment patterns.

## Table of Contents

1. [System Overview](#system-overview)
2. [High-Level Architecture](#high-level-architecture)
3. [Component Architecture](#component-architecture)
4. [Data Flow Diagrams](#data-flow-diagrams)
5. [Runtime and Plugin Architecture](#runtime-and-plugin-architecture)
6. [API Architecture](#api-architecture)
7. [Database Architecture](#database-architecture)
8. [Deployment Architecture](#deployment-architecture)
9. [Configuration Management](#configuration-management)

## Additional Documentation

For more detailed information on specific architectural aspects:

- **[🗃️ Database Architecture](DATABASE_ARCHITECTURE.md)** - Detailed database schema, data models, and performance optimization
- **[⚙️ Runtime Architecture](RUNTIME_ARCHITECTURE.md)** - Plugin system and runtime extensibility
- **[🔌 API Architecture](API_ARCHITECTURE.md)** - HTTP/gRPC/WebSocket API details
- **[🚀 Deployment Architecture](DEPLOYMENT_ARCHITECTURE.md)** - Production deployment patterns

## System Overview

Nakama is a distributed server for social and realtime games and apps. It provides a comprehensive backend infrastructure for modern game development, including user management, social features, real-time communication, and extensible runtime capabilities.

### Key Features
- User authentication and management
- Social features (friends, groups, chat)
- Real-time and turn-based multiplayer
- Leaderboards and tournaments
- In-app purchase validation
- Extensible runtime with Lua, JavaScript, and Go support
- RESTful HTTP and gRPC APIs
- Admin console for management

## High-Level Architecture

```mermaid
graph TB
    subgraph "Client Applications"
        iOS[iOS Apps]
        Android[Android Apps]
        Web[Web Apps]
        Unity[Unity Games]
        Unreal[Unreal Games]
    end

    subgraph "Load Balancer"
        LB[Load Balancer/Proxy]
    end

    subgraph "Nakama Cluster"
        N1[Nakama Node 1]
        N2[Nakama Node 2]
        N3[Nakama Node N]
    end

    subgraph "Database Layer"
        DB[(PostgreSQL/CockroachDB)]
        Cache[(Redis Cache)]
    end

    subgraph "External Services"
        Apple[Apple Store]
        Google[Google Play]
        Steam[Steam]
        Facebook[Facebook]
        Discord[Discord]
    end

    subgraph "Monitoring & Ops"
        Metrics[Prometheus/Grafana]
        Logs[Logging System]
    end

    iOS --> LB
    Android --> LB
    Web --> LB
    Unity --> LB
    Unreal --> LB

    LB --> N1
    LB --> N2
    LB --> N3

    N1 --> DB
    N2 --> DB
    N3 --> DB

    N1 -.-> Cache
    N2 -.-> Cache
    N3 -.-> Cache

    N1 --> Apple
    N1 --> Google
    N1 --> Steam
    N1 --> Facebook
    N1 --> Discord

    N1 --> Metrics
    N2 --> Metrics
    N3 --> Metrics

    N1 --> Logs
    N2 --> Logs
    N3 --> Logs
```

## Component Architecture

```mermaid
graph TB
    subgraph "Nakama Server Core"
        subgraph "API Layer"
            HTTP[HTTP/REST API]
            GRPC[gRPC API]
            WS[WebSocket API]
            Console[Admin Console]
        end

        subgraph "Business Logic Layer"
            Auth[Authentication]
            Social[Social Features]
            Match[Match System]
            MM[Matchmaker]
            Storage[Storage Engine]
            Leaderboard[Leaderboards]
            Tournament[Tournaments]
            Party[Party System]
            IAP[In-App Purchases]
        end

        subgraph "Runtime Layer"
            LuaRT[Lua Runtime]
            JSRT[JavaScript Runtime]
            GoRT[Go Runtime]
            Hooks[Before/After Hooks]
        end

        subgraph "Core Services"
            SessionMgr[Session Manager]
            Tracker[Presence Tracker]
            Router[Message Router]
            Registry[Match Registry]
            Metrics[Metrics Collection]
        end

        subgraph "Data Layer"
            DB[Database Interface]
            Cache[Cache Layer]
            Index[Search Index]
        end
    end

    HTTP --> Auth
    GRPC --> Auth
    WS --> SessionMgr
    Console --> Auth

    Auth --> Social
    Auth --> Match
    Auth --> Storage

    Social --> DB
    Match --> Registry
    Storage --> DB
    Storage --> Index

    MM --> Match
    MM --> Tracker

    LuaRT --> Hooks
    JSRT --> Hooks
    GoRT --> Hooks

    Hooks --> Auth
    Hooks --> Social
    Hooks --> Match

    SessionMgr --> Tracker
    Match --> Router
    Router --> SessionMgr
```

## Data Flow Diagrams

### User Authentication Flow

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Auth
    participant Runtime
    participant DB
    participant External

    Client->>API: Authentication Request
    API->>Runtime: Before Auth Hook
    Runtime-->>API: Hook Response
    API->>Auth: Process Authentication
    Auth->>External: Validate External Token (if applicable)
    External-->>Auth: Validation Response
    Auth->>DB: User Lookup/Creation
    DB-->>Auth: User Data
    Auth->>Auth: Generate Session Token
    Auth-->>API: Session Created
    API->>Runtime: After Auth Hook
    Runtime-->>API: Hook Response
    API-->>Client: Authentication Response
```

### Real-time Match Flow

```mermaid
sequenceDiagram
    participant Client1
    participant Client2
    participant WS
    participant Match
    participant Runtime
    participant Registry

    Client1->>WS: Join Match Request
    WS->>Registry: Find/Create Match
    Registry->>Match: Initialize Match
    Match->>Runtime: Match Init Hook
    Runtime-->>Match: Hook Response
    Match->>Registry: Register Match
    Registry-->>WS: Match Created
    WS-->>Client1: Match Joined

    Client2->>WS: Join Match Request
    WS->>Registry: Find Match
    Registry-->>WS: Match Found
    WS->>Match: Add Player
    Match->>Runtime: Player Join Hook
    Runtime-->>Match: Hook Response
    Match->>WS: Player Added
    WS-->>Client1: Player Joined Event
    WS-->>Client2: Match Joined

    Client1->>WS: Game Action
    WS->>Match: Process Action
    Match->>Runtime: Match Logic Hook
    Runtime-->>Match: Game State Update
    Match->>WS: Broadcast Update
    WS-->>Client1: State Update
    WS-->>Client2: State Update
```

### Storage Operation Flow

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Storage
    participant Runtime
    participant DB
    participant Index

    Client->>API: Storage Write Request
    API->>Runtime: Before Storage Hook
    Runtime-->>API: Validation Response
    API->>Storage: Process Write
    Storage->>DB: Write Data
    DB-->>Storage: Write Confirmation
    Storage->>Index: Update Search Index
    Index-->>Storage: Index Updated
    Storage-->>API: Write Complete
    API->>Runtime: After Storage Hook
    Runtime-->>API: Hook Response
    API-->>Client: Write Response
```

## Runtime and Plugin Architecture

```mermaid
graph TB
    subgraph "Runtime Environment"
        subgraph "Lua Runtime"
            LuaVM[Lua VM]
            LuaModules[Lua Modules]
        end

        subgraph "JavaScript Runtime"
            V8[V8 Engine]
            JSModules[JS Modules]
        end

        subgraph "Go Runtime"
            GoPlugins[Go Plugins (.so)]
            GoModules[Go Modules]
        end
    end

    subgraph "Hook System"
        BeforeHooks[Before Hooks]
        AfterHooks[After Hooks]
        RPCHooks[RPC Functions]
        MatchHooks[Match Handlers]
        EventHooks[Event Handlers]
    end

    subgraph "Core Server"
        API[API Layer]
        Business[Business Logic]
        Database[Database]
    end

    LuaVM --> BeforeHooks
    V8 --> BeforeHooks
    GoPlugins --> BeforeHooks

    LuaVM --> AfterHooks
    V8 --> AfterHooks
    GoPlugins --> AfterHooks

    LuaVM --> RPCHooks
    V8 --> RPCHooks
    GoPlugins --> RPCHooks

    LuaVM --> MatchHooks
    V8 --> MatchHooks
    GoPlugins --> MatchHooks

    BeforeHooks --> API
    AfterHooks --> API
    RPCHooks --> API
    MatchHooks --> Business
    EventHooks --> Business

    API --> Business
    Business --> Database

    LuaModules --> LuaVM
    JSModules --> V8
    GoModules --> GoPlugins
```

## API Architecture

### HTTP/gRPC Request Flow

```mermaid
graph TB
    subgraph "Client Request"
        ClientReq[Client Request]
    end

    subgraph "API Gateway"
        Router[Request Router]
        Auth[Authentication Middleware]
        CORS[CORS Middleware]
        Metrics[Metrics Middleware]
    end

    subgraph "API Handlers"
        HTTPHandlers[HTTP Handlers]
        GRPCHandlers[gRPC Handlers]
    end

    subgraph "Business Logic"
        Core[Core Functions]
        Validation[Request Validation]
        Processing[Business Processing]
    end

    subgraph "Response Generation"
        Serialization[Response Serialization]
        ErrorHandling[Error Handling]
    end

    ClientReq --> Router
    Router --> Auth
    Auth --> CORS
    CORS --> Metrics
    Metrics --> HTTPHandlers
    Metrics --> GRPCHandlers

    HTTPHandlers --> Validation
    GRPCHandlers --> Validation
    Validation --> Core
    Core --> Processing
    Processing --> Serialization
    Processing --> ErrorHandling
    Serialization --> ClientReq
    ErrorHandling --> ClientReq
```

### WebSocket Connection Flow

```mermaid
stateDiagram-v2
    [*] --> Connecting
    Connecting --> Authenticating: WebSocket Connected
    Authenticating --> Connected: Auth Success
    Authenticating --> Disconnected: Auth Failed
    Connected --> Processing: Message Received
    Processing --> Connected: Response Sent
    Connected --> Disconnected: Client Disconnect
    Processing --> Disconnected: Error
    Disconnected --> [*]

    state Processing {
        [*] --> Validate
        Validate --> Route: Valid Message
        Validate --> Error: Invalid Message
        Route --> Execute: Handler Found
        Route --> Error: No Handler
        Execute --> Response: Success
        Execute --> Error: Processing Failed
        Response --> [*]
        Error --> [*]
    }
```

## Database Architecture

```mermaid
erDiagram
    users ||--o{ user_device : has
    users ||--o{ user_edge : from
    users ||--o{ user_edge : to
    users ||--o{ storage : owns
    users ||--o{ leaderboard_record : has
    users ||--o{ tournament_record : has
    users ||--o{ groups : member_of
    users ||--o{ message : sends
    users ||--o{ notification : receives
    users ||--o{ wallet_ledger : has

    groups ||--o{ group_edge : from
    groups ||--o{ group_edge : to

    leaderboard ||--o{ leaderboard_record : contains
    tournament ||--o{ tournament_record : contains

    users {
        uuid id PK
        string username
        string display_name
        string avatar_url
        string lang_tag
        string location
        string timezone
        jsonb metadata
        timestamp create_time
        timestamp update_time
    }

    user_device {
        uuid id PK
        uuid user_id FK
        string platform
        string identifier
        jsonb vars
    }

    storage {
        string collection
        string key
        uuid user_id FK
        string value
        string version
        jsonb read
        jsonb write
        timestamp create_time
        timestamp update_time
    }

    leaderboard {
        string id PK
        jsonb metadata
        timestamp create_time
        string operator
        bool reset_schedule_active
    }

    groups {
        uuid id PK
        uuid creator_id FK
        string name
        string description
        string avatar_url
        string lang_tag
        jsonb metadata
        bool open
        int edge_count
        int max_count
        timestamp create_time
        timestamp update_time
    }
```

## Deployment Architecture

### Docker Deployment

```mermaid
graph TB
    subgraph "Docker Host"
        subgraph "Nakama Stack"
            NakamaContainer[Nakama Container]
            DBContainer[PostgreSQL Container]
            RedisContainer[Redis Container]
        end

        subgraph "Monitoring Stack"
            PrometheusContainer[Prometheus Container]
            GrafanaContainer[Grafana Container]
        end

        subgraph "Networking"
            DockerNetwork[Docker Network]
            Volumes[Docker Volumes]
        end
    end

    subgraph "External"
        Client[Game Clients]
        LoadBalancer[Load Balancer]
    end

    Client --> LoadBalancer
    LoadBalancer --> NakamaContainer
    NakamaContainer --> DBContainer
    NakamaContainer --> RedisContainer
    NakamaContainer --> PrometheusContainer
    PrometheusContainer --> GrafanaContainer

    NakamaContainer -.-> DockerNetwork
    DBContainer -.-> DockerNetwork
    RedisContainer -.-> DockerNetwork
    DBContainer -.-> Volumes
    RedisContainer -.-> Volumes
```

### Kubernetes Deployment

```mermaid
graph TB
    subgraph "Kubernetes Cluster"
        subgraph "Ingress"
            IngressController[Ingress Controller]
        end

        subgraph "Nakama Namespace"
            NakamaPods[Nakama Pods]
            NakamaService[Nakama Service]
            NakamaConfigMap[ConfigMap]
            NakamaSecrets[Secrets]
        end

        subgraph "Database Namespace"
            PostgreSQLPods[PostgreSQL Pods]
            PostgreSQLService[PostgreSQL Service]
            PostgreSQLPVC[Persistent Volume Claims]
        end

        subgraph "Cache Namespace"
            RedisPods[Redis Pods]
            RedisService[Redis Service]
        end

        subgraph "Monitoring Namespace"
            PrometheusPods[Prometheus Pods]
            GrafanaPods[Grafana Pods]
            MonitoringServices[Monitoring Services]
        end
    end

    IngressController --> NakamaService
    NakamaService --> NakamaPods
    NakamaPods --> NakamaConfigMap
    NakamaPods --> NakamaSecrets
    NakamaPods --> PostgreSQLService
    NakamaPods --> RedisService
    PostgreSQLService --> PostgreSQLPods
    PostgreSQLPods --> PostgreSQLPVC
    RedisService --> RedisPods
    PrometheusPods --> NakamaPods
    MonitoringServices --> PrometheusPods
    MonitoringServices --> GrafanaPods
```

## Configuration Management

```mermaid
graph TB
    subgraph "Configuration Sources"
        ConfigFile[nakama.yml]
        EnvVars[Environment Variables]
        CLIFlags[Command Line Flags]
        RuntimeConfig[Runtime Configuration]
    end

    subgraph "Configuration Processing"
        Parser[Config Parser]
        Validator[Config Validator]
        Merger[Config Merger]
    end

    subgraph "Server Components"
        Database[Database Config]
        Runtime[Runtime Config]
        Socket[Socket Config]
        Session[Session Config]
        Social[Social Config]
        Metrics[Metrics Config]
        Logger[Logger Config]
    end

    ConfigFile --> Parser
    EnvVars --> Parser
    CLIFlags --> Parser
    RuntimeConfig --> Parser

    Parser --> Validator
    Validator --> Merger
    Merger --> Database
    Merger --> Runtime
    Merger --> Socket
    Merger --> Session
    Merger --> Social
    Merger --> Metrics
    Merger --> Logger

    note: "Configuration precedence: CLI Flags > Environment Variables > Configuration File > Defaults"
```

### Server Startup Flow

```mermaid
sequenceDiagram
    participant Main
    participant Config
    participant Database
    participant Runtime
    participant Server
    participant Console

    Main->>Config: Load Configuration
    Config-->>Main: Config Loaded
    Main->>Database: Initialize Database
    Database-->>Main: DB Connection Ready
    Main->>Runtime: Initialize Runtime
    Runtime->>Runtime: Load Lua/JS/Go Modules
    Runtime-->>Main: Runtime Ready
    Main->>Server: Start Server
    Server->>Server: Initialize API Handlers
    Server->>Server: Start HTTP/gRPC/WebSocket
    Server-->>Main: Server Started
    Main->>Console: Start Admin Console
    Console-->>Main: Console Started
    Main->>Main: Register Signal Handlers
    Main->>Main: Server Running
```

## Conclusion

This architecture documentation provides a comprehensive overview of the Nakama game server's technical design. The modular architecture allows for:

- **Scalability**: Horizontal scaling through multiple server instances
- **Extensibility**: Plugin system supporting multiple runtime languages
- **Reliability**: Robust error handling and monitoring capabilities
- **Maintainability**: Clear separation of concerns between components
- **Performance**: Efficient data flow and caching strategies

For more detailed information about specific components, refer to the source code and inline documentation in the respective modules.