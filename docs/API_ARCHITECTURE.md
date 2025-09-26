# Nakama API Architecture

This document details the API architecture of Nakama, covering HTTP/REST, gRPC, and WebSocket APIs.

## API Layer Overview

Nakama exposes three primary API interfaces:

1. **HTTP/REST API** - RESTful endpoints for standard operations
2. **gRPC API** - High-performance binary protocol
3. **WebSocket API** - Real-time bidirectional communication

## API Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        HTTPClients[HTTP/REST Clients]
        GRPCClients[gRPC Clients]
        WSClients[WebSocket Clients]
    end

    subgraph "Network Layer"
        LoadBalancer[Load Balancer]
        TLS[TLS Termination]
        RateLimit[Rate Limiting]
    end

    subgraph "API Gateway"
        Router[Request Router]
        AuthMiddleware[Authentication]
        CORSMiddleware[CORS Handler]
        MetricsMiddleware[Metrics Collection]
        LoggingMiddleware[Request Logging]
    end

    subgraph "Protocol Handlers"
        HTTPHandler[HTTP Handler]
        GRPCHandler[gRPC Handler]
        WSHandler[WebSocket Handler]
    end

    subgraph "API Controllers"
        AuthController[Authentication]
        UserController[User Management]
        SocialController[Social Features]
        StorageController[Storage Operations]
        MatchController[Match System]
        LeaderboardController[Leaderboards]
        NotificationController[Notifications]
    end

    subgraph "Business Logic"
        Core[Core Services]
        Runtime[Runtime Hooks]
        Database[Database Layer]
    end

    HTTPClients --> LoadBalancer
    GRPCClients --> LoadBalancer
    WSClients --> LoadBalancer

    LoadBalancer --> TLS
    TLS --> RateLimit
    RateLimit --> Router

    Router --> AuthMiddleware
    AuthMiddleware --> CORSMiddleware
    CORSMiddleware --> MetricsMiddleware
    MetricsMiddleware --> LoggingMiddleware

    LoggingMiddleware --> HTTPHandler
    LoggingMiddleware --> GRPCHandler
    LoggingMiddleware --> WSHandler

    HTTPHandler --> AuthController
    GRPCHandler --> AuthController
    WSHandler --> AuthController

    HTTPHandler --> UserController
    HTTPHandler --> SocialController
    HTTPHandler --> StorageController
    HTTPHandler --> MatchController
    HTTPHandler --> LeaderboardController
    HTTPHandler --> NotificationController

    GRPCHandler --> UserController
    GRPCHandler --> SocialController
    GRPCHandler --> StorageController
    GRPCHandler --> MatchController
    GRPCHandler --> LeaderboardController
    GRPCHandler --> NotificationController

    WSHandler --> MatchController
    WSHandler --> NotificationController

    AuthController --> Core
    UserController --> Core
    SocialController --> Core
    StorageController --> Core
    MatchController --> Core
    LeaderboardController --> Core
    NotificationController --> Core

    Core --> Runtime
    Core --> Database
```

## HTTP/REST API Flow

```mermaid
sequenceDiagram
    participant Client
    participant Gateway
    participant Auth
    participant Controller
    participant Runtime
    participant Core
    participant DB

    Client->>Gateway: HTTP Request
    Gateway->>Gateway: Route Request
    Gateway->>Auth: Validate Token
    Auth-->>Gateway: Auth Result
    
    alt Authenticated
        Gateway->>Controller: Route to Controller
        Controller->>Runtime: Before Hook (if exists)
        Runtime-->>Controller: Hook Result
        
        alt Hook Allows
            Controller->>Core: Execute Business Logic
            Core->>DB: Database Operations
            DB-->>Core: Data Response
            Core-->>Controller: Logic Result
            Controller->>Runtime: After Hook (if exists)
            Runtime-->>Controller: Hook Result
            Controller-->>Gateway: Success Response
        else Hook Rejects
            Controller-->>Gateway: Hook Rejection
        end
        
        Gateway-->>Client: HTTP Response
    else Unauthenticated
        Gateway-->>Client: 401 Unauthorized
    end
```

## gRPC API Flow

```mermaid
sequenceDiagram
    participant Client
    participant GRPCServer
    participant Interceptor
    participant Service
    participant Core

    Client->>GRPCServer: gRPC Request
    GRPCServer->>Interceptor: Authentication Interceptor
    Interceptor->>Interceptor: Validate Token
    
    alt Valid Token
        Interceptor->>Service: Route to Service Method
        Service->>Core: Business Logic
        Core-->>Service: Result
        Service-->>Interceptor: Response
        Interceptor-->>GRPCServer: Response
        GRPCServer-->>Client: gRPC Response
    else Invalid Token
        Interceptor-->>GRPCServer: Auth Error
        GRPCServer-->>Client: gRPC Error
    end
```

## WebSocket API Flow

```mermaid
stateDiagram-v2
    [*] --> Connecting
    Connecting --> Authenticating: WebSocket Connected
    Authenticating --> Connected: Auth Token Valid
    Authenticating --> Disconnected: Auth Failed
    
    Connected --> Processing: Message Received
    Processing --> Connected: Response Sent
    Processing --> Connected: Broadcast Sent
    
    Connected --> Disconnected: Client Disconnect
    Connected --> Disconnected: Server Shutdown
    Processing --> Disconnected: Fatal Error
    
    Disconnected --> [*]

    state Processing {
        [*] --> Validate
        Validate --> Route: Valid Message
        Validate --> Error: Invalid Message
        Route --> Match: Match Message
        Route --> Status: Status Message
        Route --> Party: Party Message
        Route --> Channel: Channel Message
        Route --> RPC: RPC Message
        Match --> Execute
        Status --> Execute
        Party --> Execute
        Channel --> Execute
        RPC --> Execute
        Execute --> [*]
        Error --> [*]
    }
```

## API Endpoints Structure

### HTTP/REST Endpoints

```mermaid
graph TB
    subgraph "Authentication"
        AuthDevice[POST /v2/account/authenticate/device]
        AuthEmail[POST /v2/account/authenticate/email]
        AuthFacebook[POST /v2/account/authenticate/facebook]
        AuthGoogle[POST /v2/account/authenticate/google]
        AuthSteam[POST /v2/account/authenticate/steam]
        AuthCustom[POST /v2/account/authenticate/custom]
    end

    subgraph "Account Management"
        GetAccount[GET /v2/account]
        UpdateAccount[PUT /v2/account]
        DeleteAccount[DELETE /v2/account]
        LinkDevice[POST /v2/account/link/device]
        UnlinkDevice[POST /v2/account/unlink/device]
    end

    subgraph "Social Features"
        GetFriends[GET /v2/friend]
        AddFriend[POST /v2/friend]
        DeleteFriend[DELETE /v2/friend/{id}]
        BlockFriend[POST /v2/friend/{id}/block]
        GetGroups[GET /v2/group]
        CreateGroup[POST /v2/group]
        JoinGroup[POST /v2/group/{id}/join]
        LeaveGroup[POST /v2/group/{id}/leave]
    end

    subgraph "Storage"
        ReadStorage[POST /v2/storage]
        WriteStorage[PUT /v2/storage]
        DeleteStorage[DELETE /v2/storage]
        ListStorage[GET /v2/storage]
    end

    subgraph "Leaderboards"
        GetLeaderboard[GET /v2/leaderboard/{id}]
        WriteLeaderboard[POST /v2/leaderboard/{id}]
        DeleteLeaderboard[DELETE /v2/leaderboard/{id}]
        ListLeaderboards[GET /v2/leaderboard]
    end

    subgraph "Real-time"
        WSEndpoint[WS /ws]
    end
```

### gRPC Services

```mermaid
graph TB
    subgraph "Nakama Service"
        AuthenticateDevice[AuthenticateDevice]
        AuthenticateEmail[AuthenticateEmail]
        AuthenticateFacebook[AuthenticateFacebook]
        AuthenticateGoogle[AuthenticateGoogle]
        AuthenticateSteam[AuthenticateSteam]
        AuthenticateCustom[AuthenticateCustom]
        GetAccount[GetAccount]
        UpdateAccount[UpdateAccount]
        GetUsers[GetUsers]
        AddFriends[AddFriends]
        DeleteFriends[DeleteFriends]
        BlockFriends[BlockFriends]
        ImportFacebookFriends[ImportFacebookFriends]
        CreateGroup[CreateGroup]
        UpdateGroup[UpdateGroup]
        DeleteGroup[DeleteGroup]
        JoinGroup[JoinGroup]
        LeaveGroup[LeaveGroup]
        AddGroupUsers[AddGroupUsers]
        BanGroupUsers[BanGroupUsers]
        KickGroupUsers[KickGroupUsers]
        PromoteGroupUsers[PromoteGroupUsers]
        DemoteGroupUsers[DemoteGroupUsers]
        ListGroupUsers[ListGroupUsers]
        ReadStorageObjects[ReadStorageObjects]
        WriteStorageObjects[WriteStorageObjects]
        DeleteStorageObjects[DeleteStorageObjects]
        RpcFunc[RpcFunc]
    end
```

### WebSocket Messages

```mermaid
graph TB
    subgraph "Incoming Messages"
        ChannelJoin[Channel Join]
        ChannelLeave[Channel Leave]
        ChannelMessageSend[Channel Message Send]
        MatchCreate[Match Create]
        MatchJoin[Match Join]
        MatchLeave[Match Leave]
        MatchDataSend[Match Data Send]
        MatchmakerAdd[Matchmaker Add]
        MatchmakerRemove[Matchmaker Remove]
        PartyCreate[Party Create]
        PartyJoin[Party Join]
        PartyLeave[Party Leave]
        PartyPromote[Party Promote]
        PartyAccept[Party Accept]
        PartyRemove[Party Remove]
        PartyClose[Party Close]
        PartyJoinRequest[Party Join Request]
        PartyMatchmakerAdd[Party Matchmaker Add]
        PartyMatchmakerRemove[Party Matchmaker Remove]
        PartyDataSend[Party Data Send]
        StatusFollow[Status Follow]
        StatusUnfollow[Status Unfollow]
        StatusUpdate[Status Update]
        Ping[Ping]
        Rpc[RPC]
    end

    subgraph "Outgoing Messages"
        ChannelMessage[Channel Message]
        ChannelPresenceEvent[Channel Presence Event]
        Error[Error]
        MatchData[Match Data]
        MatchPresenceEvent[Match Presence Event]
        MatchmakerMatched[Matchmaker Matched]
        Notifications[Notifications]
        PartyData[Party Data]
        PartyPresenceEvent[Party Presence Event]
        PartyMatchmakerTicket[Party Matchmaker Ticket]
        PartyLeader[Party Leader]
        PartyClose2[Party Close]
        StatusPresenceEvent[Status Presence Event]
        StreamData[Stream Data]
        StreamPresenceEvent[Stream Presence Event]
        Pong[Pong]
    end
```

## Request/Response Patterns

### Authentication Flow

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
    Runtime-->>API: Validation Response
    
    alt External Auth (Facebook, Google, etc.)
        API->>External: Verify Token
        External-->>API: Token Valid/Invalid
    end
    
    API->>Auth: Process Authentication
    Auth->>DB: User Lookup/Create
    DB-->>Auth: User Record
    Auth->>Auth: Generate Session Token
    Auth-->>API: Session Created
    API->>Runtime: After Auth Hook
    Runtime-->>API: Hook Response
    API-->>Client: Auth Response + Session Token
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
    Runtime-->>API: Validation/Modification
    API->>Storage: Process Write
    Storage->>DB: Write to Database
    DB-->>Storage: Write Confirmed
    Storage->>Index: Update Search Index
    Index-->>Storage: Index Updated
    Storage-->>API: Write Complete
    API->>Runtime: After Storage Hook
    Runtime-->>API: Hook Response
    API-->>Client: Success Response
```

## Error Handling

```mermaid
graph TB
    subgraph "Error Types"
        ValidationError[Validation Errors]
        AuthError[Authentication Errors]
        AuthzError[Authorization Errors]
        RuntimeError[Runtime Errors]
        DatabaseError[Database Errors]
        InternalError[Internal Errors]
    end

    subgraph "Error Responses"
        HTTPErrors[HTTP Status Codes]
        GRPCErrors[gRPC Status Codes]
        WSErrors[WebSocket Error Messages]
    end

    subgraph "Error Handling"
        ErrorLogger[Error Logger]
        ErrorMetrics[Error Metrics]
        ErrorAlerts[Error Alerts]
    end

    ValidationError --> HTTPErrors
    AuthError --> HTTPErrors
    AuthzError --> HTTPErrors
    RuntimeError --> HTTPErrors
    DatabaseError --> HTTPErrors
    InternalError --> HTTPErrors

    ValidationError --> GRPCErrors
    AuthError --> GRPCErrors
    AuthzError --> GRPCErrors
    RuntimeError --> GRPCErrors
    DatabaseError --> GRPCErrors
    InternalError --> GRPCErrors

    ValidationError --> WSErrors
    AuthError --> WSErrors
    AuthzError --> WSErrors
    RuntimeError --> WSErrors
    DatabaseError --> WSErrors
    InternalError --> WSErrors

    HTTPErrors --> ErrorLogger
    GRPCErrors --> ErrorLogger
    WSErrors --> ErrorLogger

    ErrorLogger --> ErrorMetrics
    ErrorMetrics --> ErrorAlerts
```

## Rate Limiting

```mermaid
graph TB
    subgraph "Rate Limit Types"
        GlobalLimit[Global Rate Limit]
        UserLimit[Per-User Rate Limit]
        IPLimit[Per-IP Rate Limit]
        EndpointLimit[Per-Endpoint Rate Limit]
    end

    subgraph "Rate Limit Storage"
        Memory[In-Memory Store]
        Redis[Redis Store]
        Database[Database Store]
    end

    subgraph "Rate Limit Algorithms"
        TokenBucket[Token Bucket]
        SlidingWindow[Sliding Window]
        FixedWindow[Fixed Window]
    end

    subgraph "Actions"
        Allow[Allow Request]
        Reject[Reject Request]
        Queue[Queue Request]
    end

    GlobalLimit --> Memory
    UserLimit --> Redis
    IPLimit --> Memory
    EndpointLimit --> Redis

    Memory --> TokenBucket
    Redis --> SlidingWindow
    Database --> FixedWindow

    TokenBucket --> Allow
    TokenBucket --> Reject
    SlidingWindow --> Allow
    SlidingWindow --> Reject
    FixedWindow --> Allow
    FixedWindow --> Queue
```

## API Security

```mermaid
graph TB
    subgraph "Authentication Methods"
        DeviceAuth[Device Authentication]
        EmailAuth[Email Authentication]
        SocialAuth[Social Authentication]
        CustomAuth[Custom Authentication]
    end

    subgraph "Authorization"
        SessionToken[Session Tokens]
        RefreshToken[Refresh Tokens]
        Permissions[Permission System]
        UserRoles[User Roles]
    end

    subgraph "Security Measures"
        TLSEncryption[TLS Encryption]
        InputValidation[Input Validation]
        SQLInjection[SQL Injection Prevention]
        XSSProtection[XSS Protection]
        CSRFProtection[CSRF Protection]
    end

    subgraph "Monitoring"
        AuditLogs[Audit Logs]
        SecurityMetrics[Security Metrics]
        AnomalyDetection[Anomaly Detection]
    end

    DeviceAuth --> SessionToken
    EmailAuth --> SessionToken
    SocialAuth --> SessionToken
    CustomAuth --> SessionToken

    SessionToken --> Permissions
    RefreshToken --> SessionToken
    Permissions --> UserRoles

    TLSEncryption --> InputValidation
    InputValidation --> SQLInjection
    SQLInjection --> XSSProtection
    XSSProtection --> CSRFProtection

    SessionToken --> AuditLogs
    Permissions --> SecurityMetrics
    UserRoles --> AnomalyDetection
```

## Performance Optimization

```mermaid
graph TB
    subgraph "Caching Strategies"
        SessionCache[Session Cache]
        QueryCache[Query Cache]
        ResponseCache[Response Cache]
        CDNCache[CDN Cache]
    end

    subgraph "Connection Pooling"
        HTTPPool[HTTP Connection Pool]
        DBPool[Database Connection Pool]
        RedisPool[Redis Connection Pool]
    end

    subgraph "Optimization Techniques"
        Compression[Response Compression]
        Batching[Request Batching]
        Pagination[Result Pagination]
        Streaming[Data Streaming]
    end

    subgraph "Monitoring"
        ResponseTime[Response Time Metrics]
        Throughput[Throughput Metrics]
        ErrorRates[Error Rate Metrics]
        ResourceUsage[Resource Usage Metrics]
    end

    SessionCache --> HTTPPool
    QueryCache --> DBPool
    ResponseCache --> RedisPool
    CDNCache --> Compression

    HTTPPool --> Batching
    DBPool --> Pagination
    RedisPool --> Streaming

    Compression --> ResponseTime
    Batching --> Throughput
    Pagination --> ErrorRates
    Streaming --> ResourceUsage
```

This API architecture provides a robust, scalable, and secure foundation for game and application backends, supporting multiple protocols and extensive customization through the runtime system.