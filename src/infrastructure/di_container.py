from typing import Dict, Any, Type, TypeVar
import tempfile

from src.domain.services.interfaces import DocumentRepository, FontService, ConversionService
from src.infrastructure.services import (
    InMemoryDocumentRepository,
    FontServiceImpl,
    ConversionServiceImpl
)
from src.application.services import DocumentApplicationService
from src.application.use_cases import (
    ConvertDocumentUseCaseImpl
)
from src.presentation.controllers import DocumentController

T = TypeVar('T')

class Container:
    """Simple dependency injection container"""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._singletons: Dict[str, Any] = {}
    
    def register_singleton(self, interface: Type[T], implementation: Type[T]) -> None:
        """Register a singleton service"""
        self._services[interface.__name__] = implementation
    
    def register_instance(self, interface: Type[T], instance: T) -> None:
        """Register a service instance"""
        self._singletons[interface.__name__] = instance
    
    def get(self, interface: Type[T]) -> T:
        """Get service instance"""
        interface_name = interface.__name__
        
        # Return singleton if exists
        if interface_name in self._singletons:
            return self._singletons[interface_name]
        
        # Create and cache singleton
        if interface_name in self._services:
            implementation = self._services[interface_name]
            instance = self._create_instance(implementation)
            self._singletons[interface_name] = instance
            return instance
        
        raise ValueError(f"Service {interface_name} not registered")
    
    def _create_instance(self, implementation: Type[T]) -> T:
        """Create instance with dependency injection for the container"""
        # DI In memory document repository
        if implementation == InMemoryDocumentRepository:
            return InMemoryDocumentRepository()
        
        # DI Font service
        elif implementation == FontServiceImpl:
            return FontServiceImpl(temp_dir=tempfile.gettempdir())
        
        # DI Conversion service
        elif implementation == ConversionServiceImpl:
            font_service = self.get(FontService)
            return ConversionServiceImpl(font_service, temp_dir=tempfile.gettempdir())
        
        # DI Convert document use case
        elif implementation == ConvertDocumentUseCaseImpl:
            document_repo = self.get(DocumentRepository)
            font_service = self.get(FontService)
            conversion_service = self.get(ConversionService)
            return ConvertDocumentUseCaseImpl(document_repo, font_service, conversion_service)
        
        # DI Document application service
        elif implementation == DocumentApplicationService:
            convert_use_case = self.get(ConvertDocumentUseCaseImpl)
            return DocumentApplicationService(convert_use_case)
        
        # DI Document controller
        elif implementation == DocumentController:
            app_service = self.get(DocumentApplicationService)
            return DocumentController(app_service)
        
        # Default case
        else:
            return implementation()


def di_container() -> Container:
    """Configure the dependency injection container"""
    new_container = Container()
    
    # Register services
    new_container.register_singleton(DocumentRepository, InMemoryDocumentRepository)
    new_container.register_singleton(FontService, FontServiceImpl)
    new_container.register_singleton(ConversionService, ConversionServiceImpl)
    new_container.register_singleton(ConvertDocumentUseCaseImpl, ConvertDocumentUseCaseImpl)
    new_container.register_singleton(DocumentApplicationService, DocumentApplicationService)
    new_container.register_singleton(DocumentController, DocumentController)
    
    return new_container