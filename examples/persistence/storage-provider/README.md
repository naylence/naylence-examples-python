# Persistence Example — Encrypted Node Storage

This example demonstrates how a Naylence node can be configured with a **storage provider** and how an agent can take advantage of this provider to store its own data for housekeeping and other purposes.

When you run this example, you will see the following directory structure created:

```
% find data
data
data/agent
data/agent/__node_meta_encrypted_value.db
data/agent/storage_agent_namespace_encrypted_value.db
data/agent/__keystore_encrypted_value.db
data/agent/__binding_store_encrypted_value.db
data/sentinel
data/sentinel/__node_meta_encrypted_value.db
data/sentinel/__route_store_encrypted_value.db
data/sentinel/__keystore_encrypted_value.db
data/sentinel/__binding_store_encrypted_value.db
```

All of these files are **encrypted SQLite databases**:

* Files beginning with `__` are used for **internal node purposes**, such as:

  * Metadata (`__node_meta…`)
  * Route storage (`__route_store…`)
  * Keystore (`__keystore…`)
  * Binding store (`__binding_store…`)
  * The file `storage_agent_namespace_encrypted_value.db` contains the **custom agent storage**, where the agent’s key-value data is persisted.

> 💡 Developers can also **create and plug in their own node storage providers** if they need custom persistence logic.

---

## What you’ll learn

* Configuring a **sentinel** and **agent** with encrypted storage backends.
* Using an agent (`StorageAgent`) to persist custom key-value records.
* Observing that stored data survives across agent restarts.
* Understanding how Naylence internally separates node housekeeping from user-defined storage.

---

## Important Environment Variables

This example relies on three key environment variables for storage configuration:

```ini
FAME_STORAGE_PROFILE=encrypted-sqlite
FAME_STORAGE_MASTER_KEY=<your_master_key>
FAME_STORAGE_DB_DIRECTORY=/work/data/agent
```

* **`FAME_STORAGE_PROFILE`** — selects the storage backend. In this example we use `encrypted-sqlite`, which stores all node and agent data in encrypted SQLite databases. Other possible values include: **sqlite** (unencrypted SQLite) and **memory** (the default in-memory storage).
* **`FAME_STORAGE_MASTER_KEY`** — the master encryption key used to protect all stored databases. In this example, it is generated automatically during `make init`.
* **`FAME_STORAGE_DB_DIRECTORY`** — the directory path where the encrypted SQLite files will be created and stored. For the agent, this is `/work/data/agent`; for the sentinel, `/work/data/sentinel`.

---

## Storage API Used by the Agent

The `StorageAgent` demonstrates how an agent can use the storage provider’s **key-value API** to persist custom data models.

```python
class RecordModel(BaseModel):
    value: str
    created: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StorageAgent(BaseAgent):
    async def start(self):
        # Obtain a namespaced key-value store bound to RecordModel
        self._store = await self.storage_provider.get_kv_store(
            RecordModel, namespace="storage_agent_namespace"
        )

    @operation
    async def store_value(self, key: str, value: str) -> RecordModel:
        record = RecordModel(value=value)
        await self._store.set(key, record)
        return record

    @operation
    async def retrieve_value(self, key: str) -> RecordModel | None:
        return await self._store.get(key)

    @operation(streaming=True)
    async def retrieve_all_values(self):
        for k, v in (await self._store.list()).items():
            yield k, v
```

* **`get_kv_store`** — initializes a namespaced key-value store, bound to a Pydantic model (`RecordModel`).
* **`set(key, record)`** — saves a record under the given key.
* **`get(key)`** — retrieves a record by key.
* **`list()`** — lists all stored records in the namespace.

⚠️ **Important:** The `BaseAgent.storage_provider` property is available **only after the agent has started**. Access it inside the `start()` method, not in the constructor. Attempting to use it earlier may result in it being `None`.

This API allows the agent to manage its own persisted state safely, with records validated and serialized automatically.

---

## Quick start

### Using Make

```bash
make start
```

This will bring up the **sentinel** and **storage-agent** services with encrypted SQLite storage.

Run the client:

```bash
make run
```

You will see output like:

```
Stored value: {'value': 'Hello, World!', 'created': '2025-09-08T23:39:36.911906Z'}

Retrieved value: {'value': 'Hello, World!', 'created': '2025-09-08T23:39:36.911906Z'}

All stored key-values:
['key_1757374250509', {'value': 'Hello, World!', 'created': '2025-09-08T23:30:50.512534Z'}]
...

Total stored values: 5
```

Now stop the services:

```bash
make stop
```

Then start them again:

```bash
make start
make run
```

You will notice that the **previously stored values are still available**, even though the agent container was restarted. This proves that the data is being persisted to disk through the configured storage provider.

---

## Things to watch out for

* The **master encryption key** is generated automatically by `make` or `make init`.
* If you re-run `make init`, a different master key will be created, making your existing encrypted databases unreadable and the nodes will fail to start.
* To start over, run:

```bash
make clean
```

This removes all generated data, configs, and secrets.

* You can safely run `make start` and `make stop` repeatedly; the persisted data will survive restarts.

---

## Notes

* All stored data is encrypted at rest with the automatically generated master key.
* The example demonstrates **how agent-defined storage is kept alongside node internal storage**.
* You can plug in your own custom storage provider by implementing the node storage provider interface and configuring the node accordingly.
