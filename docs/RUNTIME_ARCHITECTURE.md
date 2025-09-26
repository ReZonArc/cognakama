# Nakama Runtime Architecture

This document details the runtime architecture of Nakama, focusing on the plugin system and extensibility features.

## Runtime System Overview

Nakama supports three runtime environments for extending server functionality:

1. **Lua Runtime** - Lightweight scripting with LuaJIT
2. **JavaScript Runtime** - V8-powered JavaScript execution
3. **Go Runtime** - Native Go plugins compiled as shared objects

## Runtime Architecture

```mermaid
graph TB
    subgraph "Runtime Manager"
        Loader[Module Loader]
        Scheduler[Function Scheduler]
        Context[Execution Context]
    end

    subgraph "Lua Runtime"
        LuaVM[LuaJIT VM]
        LuaCtx[Lua Context]
        LuaAPI[Lua Nakama API]
        LuaModules[.lua files]
    end

    subgraph "JavaScript Runtime"
        V8Engine[V8 Engine]
        JSCtx[JS Context]
        JSAPI[JS Nakama API]
        JSModules[.js/.ts files]
    end

    subgraph "Go Runtime"
        GoLoader[Plugin Loader]
        GoCtx[Go Context]
        GoAPI[Go Nakama API]
        GoPlugins[.so files]
    end

    subgraph "Core Server"
        APILayer[API Layer]
        BusinessLogic[Business Logic]
        Database[Database]
        Sessions[Session Manager]
    end

    Loader --> LuaVM
    Loader --> V8Engine
    Loader --> GoLoader

    LuaModules --> LuaVM
    JSModules --> V8Engine
    GoPlugins --> GoLoader

    LuaVM --> LuaCtx
    V8Engine --> JSCtx
    GoLoader --> GoCtx

    LuaCtx --> LuaAPI
    JSCtx --> JSAPI
    GoCtx --> GoAPI

    LuaAPI --> APILayer
    JSAPI --> APILayer
    GoAPI --> APILayer

    APILayer --> BusinessLogic
    BusinessLogic --> Database
    BusinessLogic --> Sessions

    Scheduler --> LuaCtx
    Scheduler --> JSCtx
    Scheduler --> GoCtx

    Context --> LuaCtx
    Context --> JSCtx
    Context --> GoCtx
```

## Hook System

```mermaid
graph TB
    subgraph "Hook Types"
        BeforeHooks[Before Hooks]
        AfterHooks[After Hooks]
        RPCHooks[RPC Functions]
        MatchHooks[Match Handlers]
        EventHooks[Event Handlers]
        StorageHooks[Storage Index Hooks]
    end

    subgraph "API Operations"
        AuthAPI[Authentication]
        SocialAPI[Social Features]
        StorageAPI[Storage Operations]
        MatchAPI[Match Operations]
        LeaderboardAPI[Leaderboard]
        TournamentAPI[Tournament]
        PurchaseAPI[Purchase Validation]
    end

    subgraph "Runtime Execution"
        HookExecutor[Hook Executor]
        ErrorHandler[Error Handler]
        TimeoutHandler[Timeout Handler]
    end

    BeforeHooks --> HookExecutor
    AfterHooks --> HookExecutor
    RPCHooks --> HookExecutor
    MatchHooks --> HookExecutor
    EventHooks --> HookExecutor
    StorageHooks --> HookExecutor

    AuthAPI --> BeforeHooks
    AuthAPI --> AfterHooks
    SocialAPI --> BeforeHooks
    SocialAPI --> AfterHooks
    StorageAPI --> BeforeHooks
    StorageAPI --> AfterHooks
    StorageAPI --> StorageHooks
    MatchAPI --> MatchHooks
    LeaderboardAPI --> BeforeHooks
    LeaderboardAPI --> AfterHooks
    TournamentAPI --> BeforeHooks
    TournamentAPI --> AfterHooks
    PurchaseAPI --> BeforeHooks
    PurchaseAPI --> AfterHooks

    HookExecutor --> ErrorHandler
    HookExecutor --> TimeoutHandler
```

## Module Loading Sequence

```mermaid
sequenceDiagram
    participant Server
    participant Loader
    participant LuaRT
    participant JSRT
    participant GoRT
    participant Hooks

    Server->>Loader: Initialize Runtime
    Loader->>Loader: Scan Runtime Directory
    
    Loader->>LuaRT: Load Lua Modules
    LuaRT->>LuaRT: Compile .lua files
    LuaRT->>Hooks: Register Lua Functions
    LuaRT-->>Loader: Lua Ready
    
    Loader->>JSRT: Load JS/TS Modules
    JSRT->>JSRT: Transpile/Compile
    JSRT->>Hooks: Register JS Functions
    JSRT-->>Loader: JS Ready
    
    Loader->>GoRT: Load Go Plugins
    GoRT->>GoRT: dlopen .so files
    GoRT->>GoRT: Call InitModule
    GoRT->>Hooks: Register Go Functions
    GoRT-->>Loader: Go Ready
    
    Loader-->>Server: Runtime Initialized
    Server->>Hooks: Start Hook Registration
    Hooks-->>Server: Hooks Registered
```

## Function Execution Flow

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant HookMgr
    participant Runtime
    participant Context
    participant Database

    Client->>API: API Request
    API->>HookMgr: Trigger Before Hook
    HookMgr->>Runtime: Execute Hook Function
    Runtime->>Context: Create Execution Context
    Context->>Runtime: Context Ready
    Runtime->>Database: Database Operations (if needed)
    Database-->>Runtime: Response
    Runtime-->>HookMgr: Hook Result
    HookMgr-->>API: Continue/Modify/Reject
    
    alt Hook allows continuation
        API->>API: Process Core Logic
        API->>HookMgr: Trigger After Hook
        HookMgr->>Runtime: Execute After Hook
        Runtime-->>HookMgr: Hook Result
        HookMgr-->>API: Final Result
        API-->>Client: Response
    else Hook rejects
        API-->>Client: Hook Rejection Response
    end
```

## Runtime Context and API

```mermaid
graph TB
    subgraph "Runtime Context"
        UserCtx[User Context]
        Logger[Logger Interface]
        Database[Database Interface]
        HTTPClient[HTTP Client]
        Environment[Environment Variables]
    end

    subgraph "Nakama API"
        AuthAPI[Authentication API]
        StorageAPI[Storage API]
        SocialAPI[Social API]
        MatchAPI[Match API]
        NotificationAPI[Notification API]
        LeaderboardAPI[Leaderboard API]
        WalletAPI[Wallet API]
        StreamAPI[Stream API]
    end

    subgraph "Utility Functions"
        JSONUtils[JSON Utilities]
        CryptoUtils[Crypto Utilities]
        TimeUtils[Time Utilities]
        HTTPUtils[HTTP Utilities]
        ValidationUtils[Validation Utilities]
    end

    UserCtx --> AuthAPI
    Logger --> StorageAPI
    Database --> SocialAPI
    HTTPClient --> MatchAPI
    Environment --> NotificationAPI

    AuthAPI --> JSONUtils
    StorageAPI --> CryptoUtils
    SocialAPI --> TimeUtils
    MatchAPI --> HTTPUtils
    NotificationAPI --> ValidationUtils
```

## Error Handling and Timeouts

```mermaid
stateDiagram-v2
    [*] --> Executing
    Executing --> Success: Function Completes
    Executing --> Timeout: Execution Timeout
    Executing --> Error: Runtime Error
    Executing --> Panic: Panic/Exception
    
    Success --> [*]
    
    Timeout --> LogError: Log Timeout
    Error --> LogError: Log Error
    Panic --> LogError: Log Panic
    
    LogError --> Cleanup: Cleanup Context
    Cleanup --> [*]

    state Executing {
        [*] --> ValidateInput
        ValidateInput --> CallFunction: Valid
        ValidateInput --> InputError: Invalid
        CallFunction --> ProcessResult: Complete
        ProcessResult --> [*]
        InputError --> [*]
    }
```

## Runtime Configuration

```mermaid
graph TB
    subgraph "Runtime Config"
        RuntimePath[Runtime Path]
        HTTPKey[HTTP Key]
        Environment[Environment]
        ReadOnlyGlobals[Read Only Globals]
        CallStackSize[Call Stack Size]
        MinCount[Min Pool Size]
        MaxCount[Max Pool Size]
        JSEntrypoint[JS Entrypoint]
        EventQueue[Event Queue Size]
    end

    subgraph "Runtime Pools"
        LuaPool[Lua VM Pool]
        JSPool[JS Context Pool]
        GoPool[Go Plugin Pool]
    end

    subgraph "Security Settings"
        Sandbox[Sandbox Mode]
        AllowedModules[Allowed Modules]
        TimeoutSettings[Timeout Settings]
        MemoryLimits[Memory Limits]
    end

    RuntimePath --> LuaPool
    RuntimePath --> JSPool
    RuntimePath --> GoPool

    MinCount --> LuaPool
    MaxCount --> LuaPool
    MinCount --> JSPool
    MaxCount --> JSPool

    JSEntrypoint --> JSPool
    EventQueue --> LuaPool
    EventQueue --> JSPool

    Sandbox --> LuaPool
    Sandbox --> JSPool
    AllowedModules --> LuaPool
    AllowedModules --> JSPool
    TimeoutSettings --> LuaPool
    TimeoutSettings --> JSPool
    MemoryLimits --> LuaPool
    MemoryLimits --> JSPool
```

## Module Types and Registration

```mermaid
graph TB
    subgraph "Module Types"
        InitModule[Init Modules]
        RPCModule[RPC Modules]
        HookModule[Hook Modules]
        MatchModule[Match Modules]
        EventModule[Event Modules]
    end

    subgraph "Registration Process"
        ModuleScanner[Module Scanner]
        FunctionRegistry[Function Registry]
        HookRegistry[Hook Registry]
        RPCRegistry[RPC Registry]
        MatchRegistry[Match Registry]
    end

    subgraph "Execution Engine"
        Dispatcher[Function Dispatcher]
        ContextManager[Context Manager]
        ErrorManager[Error Manager]
    end

    InitModule --> ModuleScanner
    RPCModule --> ModuleScanner
    HookModule --> ModuleScanner
    MatchModule --> ModuleScanner
    EventModule --> ModuleScanner

    ModuleScanner --> FunctionRegistry
    FunctionRegistry --> HookRegistry
    FunctionRegistry --> RPCRegistry
    FunctionRegistry --> MatchRegistry

    HookRegistry --> Dispatcher
    RPCRegistry --> Dispatcher
    MatchRegistry --> Dispatcher

    Dispatcher --> ContextManager
    Dispatcher --> ErrorManager
```

## Performance Considerations

### VM Pool Management

```mermaid
sequenceDiagram
    participant Request
    participant Pool
    participant VM
    participant Function
    participant Cleanup

    Request->>Pool: Request VM
    Pool->>Pool: Check Available VMs
    
    alt VM Available
        Pool->>VM: Get VM from Pool
    else No VM Available
        Pool->>VM: Create New VM
    end
    
    Pool-->>Request: VM Instance
    Request->>VM: Setup Context
    VM->>Function: Execute Function
    Function-->>VM: Result
    VM-->>Request: Execution Complete
    Request->>Cleanup: Reset VM State
    Cleanup->>Pool: Return VM to Pool
```

### Memory Management

```mermaid
graph TB
    subgraph "Memory Pools"
        LuaMemory[Lua Memory Pool]
        JSMemory[JS Memory Pool]
        GoMemory[Go Memory Pool]
    end

    subgraph "Garbage Collection"
        LuaGC[Lua GC]
        V8GC[V8 GC]
        GoGC[Go GC]
    end

    subgraph "Memory Monitoring"
        MemoryTracker[Memory Tracker]
        LimitEnforcer[Limit Enforcer]
        AlertSystem[Alert System]
    end

    LuaMemory --> LuaGC
    JSMemory --> V8GC
    GoMemory --> GoGC

    LuaMemory --> MemoryTracker
    JSMemory --> MemoryTracker
    GoMemory --> MemoryTracker

    MemoryTracker --> LimitEnforcer
    LimitEnforcer --> AlertSystem
```

## Debugging and Monitoring

```mermaid
graph TB
    subgraph "Debug Features"
        Logging[Runtime Logging]
        Profiling[Performance Profiling]
        Tracing[Execution Tracing]
        Metrics[Runtime Metrics]
    end

    subgraph "Monitoring Tools"
        Console[Admin Console]
        MetricsExporter[Metrics Exporter]
        LogAggregator[Log Aggregator]
        HealthCheck[Health Checker]
    end

    subgraph "Alerting"
        ErrorAlerts[Error Rate Alerts]
        PerformanceAlerts[Performance Alerts]
        MemoryAlerts[Memory Usage Alerts]
        TimeoutAlerts[Timeout Alerts]
    end

    Logging --> Console
    Profiling --> MetricsExporter
    Tracing --> LogAggregator
    Metrics --> HealthCheck

    Console --> ErrorAlerts
    MetricsExporter --> PerformanceAlerts
    LogAggregator --> MemoryAlerts
    HealthCheck --> TimeoutAlerts
```

This runtime architecture enables powerful extensibility while maintaining performance, security, and reliability. The multi-language support allows developers to choose the best tool for their specific use cases while providing a consistent API across all runtime environments.