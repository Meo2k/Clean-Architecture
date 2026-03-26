## Be

### Overall 
This is the framework for building a FastAPI project with <b>Clean Architecture</b> and <b>DDD (Domain-Driven Design)</b>.

### Architecture


```
src/
├── api/              # API endpoints and routing
├── app/              # Application layer (use cases, services)
├── domain/           # Domain entities and business logic
├── infras/          # Adapters (repositories, external services)
├── lib/              # Shared libraries and utilities
├── main.py           # main application file

```
### Detail Domain-Driven Design
- Entity: mutable and has identity
- Value Object: immutable and self-validate
- Domain Event: uses past tense (e.g., OrderCreated) and is published after the transaction commits, as it is triggered by the use case.
- Domain Service: operate with outside (infras), or shared logic of multi entities
- Repository: interface for database 


### Detail Project 
The project using: 
- Result Pattern
- Unit of Work Pattern
- Domain Event
- Optimistic Locking (version column and using **tenacity lib** to retry)
- Track logs by correlation id (using **asgi-correlation-id**)


Note:
- api layer only handle request and response, not business logic
- app layer handle business logic (not include the components are related to api)
- domain layer handle domain entities and business logic
- infras layer handle adapters (repositories, external services). Is the lowest layer, only operate with database and external services , not include the components are related to api
- In domain layer, we should return exception instead of result pattern. In app layer, we should use result pattern by wrapping the exception in result pattern (try ... except)
- With id of database, we should use UUID v7 (it's time-sortable) instead of integer. But with id of entity, we use string. Adaptering from string to UUID v7 of repository is handled in infras layer.
- Tasks inside BackgroundTasks are queues, and BackgroundTasks bags are hash tables. Addition, BackgroundTasks is not thread-safe, so we should use it in a single thread (ContextVars). Task inside BackgroundTasks only run after request is completed. 
- Event handler is dispatched by event dispatcher which should placed outside of unit of work (uow) to avoid the case that event is triggered when uow is not committed.
- Import according to the flowwing order: 
    1. outside lib (fastapi, sqlalchemy, etc) 
    2. shared code (lib)
    3. Api
    4. Infras
    5. App
    6. Domain

    * <b>Remember to group them together</b>
    * Initialize global variables with one or two blank lines above and below



### Run project

run with localhost
```bash
make run
```

run with public
```bash
make run public=true
```

### With database 
Using: 
* <b>alembic</b> (manager version)
* <b>SQLAlchemy</b> (ORM)

create version
```bash
alembic revision --autogenerate -m "<message>"
```

upgrade
```bash
alembic upgrade head
```

downgrade
```bash
alembic downgrade -1
```