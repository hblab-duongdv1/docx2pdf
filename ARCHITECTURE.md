# DOCX to PDF Converter - Clean Architecture

This project has been refactored to follow Clean Architecture (also known as Hexagonal Architecture) principles, implementing Domain-Driven Design (DDD) patterns.

## Architecture Overview

The application follows Clean Architecture principles with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                       │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              HTTP Controllers                          │ │
│  │  • DocumentController                                  │ │
│  │  • Request/Response handling                           │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                   APPLICATION LAYER                        │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              Use Cases & Services                      │ │
│  │  • ConvertDocumentUseCase                              │ │
│  │  • PreviewFontsUseCase                                 │ │
│  │  • DocumentApplicationService                           │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                      DOMAIN LAYER                           │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              Entities & Business Logic                 │ │
│  │  • Document Entity                                     │ │
│  │  • FontInfo Value Object                               │ │
│  │  • Domain Service Interfaces                           │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                  INFRASTRUCTURE LAYER                      │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              External Services                         │ │
│  │  • FontServiceImpl                                     │ │
│  │  • ConversionServiceImpl                               │ │
│  │  • InMemoryDocumentRepository                          │ │
│  │  • Dependency Injection Container                      │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Directory Structure

```
src/
├── domain/                 # Domain Layer (Business Logic)
│   ├── entities/           # Domain Entities
│   └── services/           # Domain Service Interfaces
├── application/            # Application Layer (Use Cases)
│   ├── dtos/              # Data Transfer Objects
│   ├── services/           # Application Services & Use Case Interfaces
│   └── use_cases/         # Use Case Implementations
├── infrastructure/         # Infrastructure Layer (External Concerns)
│   ├── services/          # Infrastructure Service Implementations
│   └── container.py       # Dependency Injection Container
└── presentation/          # Presentation Layer (Controllers)
    └── controllers/       # HTTP Controllers
```

## Layer Responsibilities

### 1. Domain Layer (`src/domain/`)
Contains the core business logic and domain entities.

- **Entities**: `Document`, `FontInfo` - Core business objects
- **Value Objects**: `DocumentStatus`, `DocumentFormat` - Immutable objects
- **Domain Services**: Abstract interfaces for business operations

### 2. Application Layer (`src/application/`)
Contains use cases and application services that orchestrate domain operations.

- **DTOs**: Data Transfer Objects for request/response
- **Use Cases**: Business workflows (ConvertDocument, PreviewFonts)
- **Application Services**: Orchestrate use cases

### 3. Infrastructure Layer (`src/infrastructure/`)
Implements external concerns and infrastructure services.

- **Services**: Concrete implementations of domain interfaces
- **Container**: Dependency injection configuration

### 4. Presentation Layer (`src/presentation/`)
Handles HTTP requests and responses.

- **Controllers**: Handle HTTP endpoints and delegate to application services

## Key Benefits

### 1. **Separation of Concerns**
Each layer has a single responsibility:
- Domain: Business rules
- Application: Use cases
- Infrastructure: External services
- Presentation: HTTP handling

### 2. **Dependency Inversion**
High-level modules don't depend on low-level modules. Both depend on abstractions.

### 3. **Testability**
Each layer can be tested independently with mocked dependencies.

### 4. **Maintainability**
Changes in one layer don't affect others, making the codebase easier to maintain.

### 5. **Flexibility**
Easy to swap implementations (e.g., different databases, external services).

## Usage

The application maintains the same API endpoints as before:

- `GET /health` - Health check
- `POST /convert` - Convert DOCX from URL to PDF
- `POST /convert-file` - Convert uploaded DOCX file to PDF
- `POST /fonts/preview` - Preview font availability

## Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

## Architecture Patterns Used

### 1. **Repository Pattern**
Abstracts data access logic:
```python
class DocumentRepository(ABC):
    @abstractmethod
    def save(self, document: Document) -> Document:
        pass
```

### 2. **Use Case Pattern**
Encapsulates business workflows:
```python
class ConvertDocumentUseCase(ABC):
    @abstractmethod
    def execute(self, request: ConvertDocumentRequest) -> ConvertDocumentResponse:
        pass
```

### 3. **Dependency Injection**
Manages object creation and dependencies:
```python
container = configure_container()
document_controller = container.get(DocumentController)
```

### 4. **DTO Pattern**
Transfers data between layers:
```python
@dataclass
class ConvertDocumentRequest:
    docx_url: Optional[str] = None
    font_urls: List[dict] = None
```

## Extending the Architecture

### Adding New Features

1. **Domain**: Add new entities/value objects
2. **Application**: Create new use cases and DTOs
3. **Infrastructure**: Implement new services
4. **Presentation**: Add new controllers/endpoints

### Example: Adding Database Support

1. Create a new repository implementation:
```python
class DatabaseDocumentRepository(DocumentRepository):
    def save(self, document: Document) -> Document:
        # Database implementation
        pass
```

2. Update the container configuration:
```python
container.register_singleton(DocumentRepository, DatabaseDocumentRepository)
```

## Testing Strategy

Each layer can be tested independently:

- **Unit Tests**: Test individual classes with mocked dependencies
- **Integration Tests**: Test layer interactions
- **End-to-End Tests**: Test complete workflows

## Benefits Over Previous Architecture

1. **Better Organization**: Clear separation of concerns
2. **Easier Testing**: Each component can be tested in isolation
3. **Flexibility**: Easy to change implementations
4. **Maintainability**: Changes are localized to specific layers
5. **Scalability**: Easy to add new features without affecting existing code

This architecture makes the codebase more professional, maintainable, and follows industry best practices for enterprise applications.
