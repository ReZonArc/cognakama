# Nakama Database Architecture and Data Model

This document details the database architecture, schema design, and data relationships in Nakama.

## Database Architecture Overview

Nakama uses PostgreSQL (or PostgreSQL-compatible databases like CockroachDB) as its primary data store, with Redis for caching and session management.

```mermaid
graph TB
    subgraph "Application Layer"
        NakamaServer[Nakama Server]
        AdminConsole[Admin Console]
    end

    subgraph "Database Layer"
        PostgreSQL[(PostgreSQL Primary)]
        ReadReplicas[(Read Replicas)]
        ConnectionPool[Connection Pool]
    end

    subgraph "Cache Layer"
        RedisCache[(Redis Cache)]
        SessionStore[Session Store]
        LeaderboardCache[Leaderboard Cache]
    end

    subgraph "Storage Layer"
        PersistentStorage[Persistent Storage]
        Backups[Database Backups]
        WALArchive[WAL Archive]
    end

    NakamaServer --> ConnectionPool
    AdminConsole --> ConnectionPool
    ConnectionPool --> PostgreSQL
    ConnectionPool --> ReadReplicas

    NakamaServer --> RedisCache
    RedisCache --> SessionStore
    RedisCache --> LeaderboardCache

    PostgreSQL --> PersistentStorage
    PostgreSQL --> Backups
    PostgreSQL --> WALArchive
```

## Core Data Model

```mermaid
erDiagram
    users ||--o{ user_device : has
    users ||--o{ user_edge : from_user
    users ||--o{ user_edge : to_user
    users ||--o{ storage : user_id
    users ||--o{ message : sender_id
    users ||--o{ notification : user_id
    users ||--o{ wallet_ledger : user_id
    users ||--o{ leaderboard_record : owner_id
    users ||--o{ tournament_record : owner_id
    users ||--o{ group_edge : user_id

    groups ||--o{ group_edge : group_id
    groups ||--o{ message : group_id

    leaderboard ||--o{ leaderboard_record : leaderboard_id
    tournament ||--o{ tournament_record : tournament_id

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
        timestamp last_online_at
        boolean online
        boolean edge_count
        boolean disable_time
    }

    user_device {
        string id PK
        uuid user_id FK
        timestamp create_time
        timestamp update_time
        jsonb vars
    }

    user_edge {
        uuid source_id FK
        uuid destination_id FK
        timestamp create_time
        timestamp update_time
        int state
        string label
    }

    storage {
        string collection
        string key
        uuid user_id FK
        string value
        string version
        int permissionRead
        int permissionWrite
        timestamp create_time
        timestamp update_time
    }

    groups {
        uuid id PK
        uuid creator_id FK
        string name
        string description
        string avatar_url
        string lang_tag
        jsonb metadata
        boolean open
        int edge_count
        int max_count
        timestamp create_time
        timestamp update_time
        boolean disable_time
    }

    group_edge {
        uuid source_id FK
        uuid destination_id FK
        int state
        timestamp create_time
        timestamp update_time
    }

    leaderboard {
        string id PK
        boolean authoritative
        string sort_order
        string operator
        boolean reset_schedule_active
        jsonb metadata
        timestamp create_time
        string reset_schedule
        timestamp next_reset
        string title
        string description
        string category
        timestamp start_time
        timestamp end_time
        int duration
        int max_size
        int max_num_score
        boolean join_required
    }

    leaderboard_record {
        string leaderboard_id FK
        uuid owner_id FK
        string username
        int64 score
        int64 subscore
        int num_score
        jsonb metadata
        timestamp create_time
        timestamp update_time
        timestamp expiry_time
        int rank_value
    }

    tournament {
        string id PK
        string sort_order
        string operator
        string duration
        boolean reset_schedule_active
        jsonb metadata
        timestamp create_time
        string reset_schedule
        timestamp next_reset
        string title
        string description
        string category
        timestamp start_time
        timestamp end_time
        int max_size
        int max_num_score
        boolean join_required
    }

    tournament_record {
        string tournament_id FK
        uuid owner_id FK
        string username
        int64 score
        int64 subscore
        int num_score
        jsonb metadata
        timestamp create_time
        timestamp update_time
        timestamp expiry_time
        int rank_value
    }

    message {
        uuid id PK
        string code
        uuid sender_id FK
        string username
        uuid stream_mode
        string stream_subject
        string stream_descriptor
        string stream_label
        timestamp create_time
        timestamp update_time
        boolean persistent
        jsonb content
    }

    notification {
        uuid id PK
        uuid user_id FK
        string subject
        jsonb content
        int code
        uuid sender_id
        timestamp create_time
        boolean persistent
    }

    wallet_ledger {
        uuid id PK
        uuid user_id FK
        int64 changeset
        jsonb metadata
        timestamp create_time
        timestamp update_time
    }
```

## Storage System Architecture

```mermaid
graph TB
    subgraph "Storage API"
        ReadAPI[Read Operations]
        WriteAPI[Write Operations]
        ListAPI[List Operations]
        DeleteAPI[Delete Operations]
    end

    subgraph "Storage Engine"
        PermissionCheck[Permission Validation]
        Hooks[Runtime Hooks]
        StorageCore[Storage Core Logic]
        SearchIndex[Search Indexing]
    end

    subgraph "Data Layer"
        StorageTable[(storage table)]
        BTreeIndexes[B-Tree Indexes]
        FullTextIndex[Full-Text Search]
    end

    subgraph "Caching"
        StorageCache[Storage Cache]
        QueryCache[Query Cache]
    end

    ReadAPI --> PermissionCheck
    WriteAPI --> PermissionCheck
    ListAPI --> PermissionCheck
    DeleteAPI --> PermissionCheck

    PermissionCheck --> Hooks
    Hooks --> StorageCore
    StorageCore --> SearchIndex

    StorageCore --> StorageTable
    StorageCore --> StorageCache
    SearchIndex --> FullTextIndex

    StorageTable --> BTreeIndexes
    StorageCache --> QueryCache
```

## User Management Schema

```mermaid
graph TB
    subgraph "User Core"
        UserTable[(users)]
        UserIndex[User Indexes]
    end

    subgraph "Authentication"
        DeviceTable[(user_device)]
        EmailTable[(user_email)]
        SocialTable[(user_social)]
    end

    subgraph "Social Graph"
        UserEdgeTable[(user_edge)]
        FriendCache[Friend Cache]
    end

    subgraph "User Data"
        WalletTable[(wallet_ledger)]
        NotificationTable[(notification)]
        StorageTable[(storage)]
    end

    UserTable --> UserIndex
    UserTable --> DeviceTable
    UserTable --> EmailTable
    UserTable --> SocialTable
    UserTable --> UserEdgeTable
    UserTable --> WalletTable
    UserTable --> NotificationTable
    UserTable --> StorageTable

    UserEdgeTable --> FriendCache
```

## Social Features Schema

```mermaid
graph TB
    subgraph "Groups"
        GroupTable[(groups)]
        GroupEdgeTable[(group_edge)]
        GroupIndex[Group Indexes]
    end

    subgraph "Chat System"
        MessageTable[(message)]
        ChannelTable[(channel)]
        MessageIndex[Message Indexes]
    end

    subgraph "Social Graph"
        UserEdgeTable[(user_edge)]
        SocialIndex[Social Indexes]
    end

    subgraph "Presence System"
        PresenceCache[Presence Cache]
        StatusCache[Status Cache]
    end

    GroupTable --> GroupEdgeTable
    GroupTable --> GroupIndex
    GroupEdgeTable --> MessageTable

    MessageTable --> ChannelTable
    MessageTable --> MessageIndex

    UserEdgeTable --> SocialIndex
    UserEdgeTable --> PresenceCache

    PresenceCache --> StatusCache
```

## Leaderboard and Tournament Schema

```mermaid
graph TB
    subgraph "Leaderboards"
        LeaderboardTable[(leaderboard)]
        LeaderboardRecordTable[(leaderboard_record)]
        LeaderboardIndex[Leaderboard Indexes]
        LeaderboardCache[Leaderboard Cache]
    end

    subgraph "Tournaments"
        TournamentTable[(tournament)]
        TournamentRecordTable[(tournament_record)]
        TournamentIndex[Tournament Indexes]
        TournamentCache[Tournament Cache]
    end

    subgraph "Ranking System"
        RankCalculator[Rank Calculator]
        RankCache[Rank Cache]
        RankScheduler[Rank Scheduler]
    end

    LeaderboardTable --> LeaderboardRecordTable
    LeaderboardTable --> LeaderboardIndex
    LeaderboardRecordTable --> LeaderboardCache

    TournamentTable --> TournamentRecordTable
    TournamentTable --> TournamentIndex
    TournamentRecordTable --> TournamentCache

    LeaderboardRecordTable --> RankCalculator
    TournamentRecordTable --> RankCalculator
    RankCalculator --> RankCache
    RankCache --> RankScheduler
```

## Data Access Patterns

### Read Patterns

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Cache
    participant DB
    participant Index

    Client->>API: Read Request
    API->>Cache: Check Cache
    
    alt Cache Hit
        Cache-->>API: Cached Data
        API-->>Client: Response
    else Cache Miss
        API->>DB: Query Database
        
        alt Simple Query
            DB-->>API: Result
        else Complex Query
            DB->>Index: Use Index
            Index-->>DB: Indexed Result
            DB-->>API: Result
        end
        
        API->>Cache: Update Cache
        API-->>Client: Response
    end
```

### Write Patterns

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant DB
    participant Cache
    participant Index
    participant Replica

    Client->>API: Write Request
    API->>DB: Write to Primary
    DB-->>API: Write Confirmed
    
    par Update Cache
        API->>Cache: Invalidate/Update Cache
    and Update Index
        API->>Index: Update Search Index
    and Replicate
        DB->>Replica: Async Replication
    end
    
    API-->>Client: Write Response
```

## Database Indexing Strategy

```mermaid
graph TB
    subgraph "Primary Indexes"
        PKIndexes[Primary Key Indexes]
        UKIndexes[Unique Key Indexes]
    end

    subgraph "Query Indexes"
        UserLookup[User Lookup Indexes]
        SocialGraph[Social Graph Indexes]
        StorageQuery[Storage Query Indexes]
        LeaderboardRank[Leaderboard Rank Indexes]
    end

    subgraph "Composite Indexes"
        UserDevice[User-Device Composite]
        StoragePermission[Storage Permission Composite]
        TimeRange[Time Range Composite]
    end

    subgraph "Specialized Indexes"
        FullTextSearch[Full-Text Search]
        GeoSpatial[Geo-Spatial Indexes]
        JSONPath[JSON Path Indexes]
    end

    PKIndexes --> UserLookup
    UKIndexes --> SocialGraph
    UserLookup --> UserDevice
    SocialGraph --> StoragePermission
    StorageQuery --> TimeRange
    LeaderboardRank --> FullTextSearch

    FullTextSearch --> GeoSpatial
    GeoSpatial --> JSONPath
```

## Data Partitioning Strategy

```mermaid
graph TB
    subgraph "Horizontal Partitioning"
        UserPartition[User ID Partitioning]
        TimePartition[Time-based Partitioning]
        HashPartition[Hash Partitioning]
    end

    subgraph "Vertical Partitioning"
        HotData[Hot Data Tables]
        ColdData[Cold Data Tables]
        ArchiveData[Archive Tables]
    end

    subgraph "Functional Partitioning"
        UserData[User Service Data]
        SocialData[Social Service Data]
        GameData[Game Service Data]
        AnalyticsData[Analytics Data]
    end

    UserPartition --> HotData
    TimePartition --> ColdData
    HashPartition --> ArchiveData

    HotData --> UserData
    ColdData --> SocialData
    ArchiveData --> GameData
    ArchiveData --> AnalyticsData
```

## Backup and Recovery

```mermaid
graph TB
    subgraph "Backup Types"
        FullBackup[Full Backup]
        IncrementalBackup[Incremental Backup]
        WALBackup[WAL Backup]
        LogicalBackup[Logical Backup]
    end

    subgraph "Backup Storage"
        LocalStorage[Local Storage]
        CloudStorage[Cloud Storage]
        OffSiteStorage[Off-site Storage]
    end

    subgraph "Recovery Scenarios"
        PointInTime[Point-in-Time Recovery]
        DisasterRecovery[Disaster Recovery]
        DataCorruption[Data Corruption Recovery]
        UserError[User Error Recovery]
    end

    subgraph "Automation"
        BackupScheduler[Backup Scheduler]
        RetentionPolicy[Retention Policy]
        RecoveryTesting[Recovery Testing]
    end

    FullBackup --> LocalStorage
    IncrementalBackup --> CloudStorage
    WALBackup --> OffSiteStorage
    LogicalBackup --> CloudStorage

    LocalStorage --> PointInTime
    CloudStorage --> DisasterRecovery
    OffSiteStorage --> DataCorruption
    CloudStorage --> UserError

    BackupScheduler --> FullBackup
    BackupScheduler --> IncrementalBackup
    RetentionPolicy --> BackupScheduler
    RecoveryTesting --> RetentionPolicy
```

## Performance Optimization

```mermaid
graph TB
    subgraph "Query Optimization"
        QueryPlanning[Query Planning]
        IndexOptimization[Index Optimization]
        StatisticsUpdate[Statistics Update]
        QueryRewriting[Query Rewriting]
    end

    subgraph "Connection Management"
        ConnectionPooling[Connection Pooling]
        ConnectionReuse[Connection Reuse]
        LoadBalancing[Read/Write Load Balancing]
    end

    subgraph "Caching Strategy"
        QueryCache[Query Result Cache]
        ApplicationCache[Application Cache]
        DatabaseCache[Database Buffer Cache]
    end

    subgraph "Monitoring"
        SlowQueryLog[Slow Query Log]
        PerformanceMetrics[Performance Metrics]
        ResourceMonitoring[Resource Monitoring]
    end

    QueryPlanning --> IndexOptimization
    IndexOptimization --> StatisticsUpdate
    StatisticsUpdate --> QueryRewriting

    ConnectionPooling --> ConnectionReuse
    ConnectionReuse --> LoadBalancing

    QueryCache --> ApplicationCache
    ApplicationCache --> DatabaseCache

    SlowQueryLog --> PerformanceMetrics
    PerformanceMetrics --> ResourceMonitoring
```

## Data Migration Patterns

```mermaid
sequenceDiagram
    participant Admin
    participant MigrationTool
    participant DB
    participant Backup
    participant Validation

    Admin->>MigrationTool: Initiate Migration
    MigrationTool->>Backup: Create Backup
    Backup-->>MigrationTool: Backup Complete
    
    MigrationTool->>DB: Begin Transaction
    MigrationTool->>DB: Apply Schema Changes
    MigrationTool->>DB: Migrate Data
    
    alt Migration Successful
        MigrationTool->>Validation: Validate Data
        Validation-->>MigrationTool: Validation Passed
        MigrationTool->>DB: Commit Transaction
        DB-->>MigrationTool: Migration Complete
        MigrationTool-->>Admin: Success
    else Migration Failed
        MigrationTool->>DB: Rollback Transaction
        MigrationTool->>Backup: Restore from Backup
        Backup-->>MigrationTool: Restore Complete
        MigrationTool-->>Admin: Migration Failed
    end
```

This database architecture provides a robust foundation for scalable game and application backends, with careful attention to performance, consistency, and reliability requirements.