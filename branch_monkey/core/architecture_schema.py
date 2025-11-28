"""
Architecture Schema - Defines the structured format for architecture documentation.

This schema defines how architecture should be documented and displayed.
The LLM will generate architecture in this JSON format.
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import json


class HttpMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    OPTIONS = "OPTIONS"
    HEAD = "HEAD"


class ColumnType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    JSON = "json"
    TEXT = "text"
    BINARY = "binary"
    UUID = "uuid"
    ARRAY = "array"
    FOREIGN_KEY = "foreign_key"


@dataclass
class FlowPosition:
    """Position for a node in the flow diagram."""
    x: float = 0
    y: float = 0


@dataclass
class EndpointParam:
    """A parameter for an API endpoint."""
    name: str
    type: str
    required: bool = True
    description: str = ""
    location: str = "body"  # body, query, path, header


@dataclass
class Endpoint:
    """An API endpoint definition."""
    id: str = ""  # Unique ID for flow diagram
    method: str = ""  # GET, POST, PUT, DELETE, etc.
    path: str = ""
    description: str = ""
    params: List[EndpointParam] = field(default_factory=list)
    response_type: str = ""
    response_description: str = ""
    auth_required: bool = True
    tags: List[str] = field(default_factory=list)
    connects_to: List[str] = field(default_factory=list)  # IDs of entities this endpoint uses


@dataclass
class EntityField:
    """A field in an entity/model."""
    name: str
    type: str
    description: str = ""
    required: bool = True
    default: Optional[str] = None
    constraints: List[str] = field(default_factory=list)  # e.g., "unique", "min:0", "max:100"


@dataclass
class Entity:
    """A data entity/model definition."""
    id: str = ""  # Unique ID for flow diagram
    name: str = ""
    description: str = ""
    fields: List[EntityField] = field(default_factory=list)
    relationships: List[str] = field(default_factory=list)  # e.g., "has_many: Posts", "belongs_to: User"
    file_path: str = ""
    connects_to: List[str] = field(default_factory=list)  # IDs of tables/entities this connects to


@dataclass
class TableColumn:
    """A database table column."""
    name: str
    type: str
    nullable: bool = False
    primary_key: bool = False
    foreign_key: Optional[str] = None  # e.g., "users.id"
    default: Optional[str] = None
    description: str = ""


@dataclass
class TableIndex:
    """A database index."""
    name: str
    columns: List[str]
    unique: bool = False


@dataclass
class DatabaseTable:
    """A database table definition."""
    id: str = ""  # Unique ID for flow diagram
    name: str = ""
    description: str = ""
    columns: List[TableColumn] = field(default_factory=list)
    indexes: List[TableIndex] = field(default_factory=list)
    relationships: List[str] = field(default_factory=list)  # Descriptions of relationships
    connects_to: List[str] = field(default_factory=list)  # IDs of other tables (foreign keys)


@dataclass
class UIComponent:
    """A UI component definition."""
    id: str = ""  # Unique ID for flow diagram
    name: str = ""
    type: str = ""  # page, component, layout, modal, etc.
    description: str = ""
    file_path: str = ""
    props: List[str] = field(default_factory=list)
    children: List[str] = field(default_factory=list)
    routes: List[str] = field(default_factory=list)  # For pages
    connects_to: List[str] = field(default_factory=list)  # IDs of child components or API endpoints used


@dataclass
class TechStackItem:
    """A technology in the stack."""
    id: str = ""  # Unique ID for flow diagram
    name: str = ""
    category: str = ""  # language, framework, database, tool, service
    version: str = ""
    purpose: str = ""


@dataclass
class Architecture:
    """Complete architecture documentation."""
    # Overview
    project_name: str
    description: str
    version: str = ""

    # Tech Stack
    tech_stack: List[TechStackItem] = field(default_factory=list)

    # API Endpoints
    endpoints: List[Endpoint] = field(default_factory=list)

    # Data Entities
    entities: List[Entity] = field(default_factory=list)

    # Database Tables
    tables: List[DatabaseTable] = field(default_factory=list)

    # UI Components
    ui_components: List[UIComponent] = field(default_factory=list)

    # Additional notes
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Architecture':
        """Create Architecture from dictionary."""
        # Convert nested structures
        tech_stack = [TechStackItem(**item) for item in data.get('tech_stack', [])]

        endpoints = []
        for ep in data.get('endpoints', []):
            params = [EndpointParam(**p) for p in ep.get('params', [])]
            ep_copy = {**ep, 'params': params}
            endpoints.append(Endpoint(**ep_copy))

        entities = []
        for ent in data.get('entities', []):
            fields = [EntityField(**f) for f in ent.get('fields', [])]
            ent_copy = {**ent, 'fields': fields}
            entities.append(Entity(**ent_copy))

        tables = []
        for tbl in data.get('tables', []):
            columns = [TableColumn(**c) for c in tbl.get('columns', [])]
            indexes = [TableIndex(**i) for i in tbl.get('indexes', [])]
            tbl_copy = {**tbl, 'columns': columns, 'indexes': indexes}
            tables.append(DatabaseTable(**tbl_copy))

        ui_components = [UIComponent(**comp) for comp in data.get('ui_components', [])]

        return cls(
            project_name=data.get('project_name', ''),
            description=data.get('description', ''),
            version=data.get('version', ''),
            tech_stack=tech_stack,
            endpoints=endpoints,
            entities=entities,
            tables=tables,
            ui_components=ui_components,
            notes=data.get('notes', [])
        )

    @classmethod
    def from_json(cls, json_str: str) -> 'Architecture':
        """Create Architecture from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)


# JSON Schema for validation (can be used by frontend or for documentation)
ARCHITECTURE_JSON_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["project_name", "description"],
    "properties": {
        "project_name": {"type": "string"},
        "description": {"type": "string"},
        "version": {"type": "string"},
        "tech_stack": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "category"],
                "properties": {
                    "name": {"type": "string"},
                    "category": {"type": "string", "enum": ["language", "framework", "database", "tool", "service"]},
                    "version": {"type": "string"},
                    "purpose": {"type": "string"}
                }
            }
        },
        "endpoints": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["method", "path", "description"],
                "properties": {
                    "method": {"type": "string", "enum": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"]},
                    "path": {"type": "string"},
                    "description": {"type": "string"},
                    "params": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["name", "type"],
                            "properties": {
                                "name": {"type": "string"},
                                "type": {"type": "string"},
                                "required": {"type": "boolean"},
                                "description": {"type": "string"},
                                "location": {"type": "string", "enum": ["body", "query", "path", "header"]}
                            }
                        }
                    },
                    "response_type": {"type": "string"},
                    "response_description": {"type": "string"},
                    "auth_required": {"type": "boolean"},
                    "tags": {"type": "array", "items": {"type": "string"}}
                }
            }
        },
        "entities": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "description"],
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "fields": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["name", "type"],
                            "properties": {
                                "name": {"type": "string"},
                                "type": {"type": "string"},
                                "description": {"type": "string"},
                                "required": {"type": "boolean"},
                                "default": {"type": "string"},
                                "constraints": {"type": "array", "items": {"type": "string"}}
                            }
                        }
                    },
                    "relationships": {"type": "array", "items": {"type": "string"}},
                    "file_path": {"type": "string"}
                }
            }
        },
        "tables": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "description"],
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "columns": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["name", "type"],
                            "properties": {
                                "name": {"type": "string"},
                                "type": {"type": "string"},
                                "nullable": {"type": "boolean"},
                                "primary_key": {"type": "boolean"},
                                "foreign_key": {"type": "string"},
                                "default": {"type": "string"},
                                "description": {"type": "string"}
                            }
                        }
                    },
                    "indexes": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["name", "columns"],
                            "properties": {
                                "name": {"type": "string"},
                                "columns": {"type": "array", "items": {"type": "string"}},
                                "unique": {"type": "boolean"}
                            }
                        }
                    },
                    "relationships": {"type": "array", "items": {"type": "string"}}
                }
            }
        },
        "ui_components": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "type", "description"],
                "properties": {
                    "name": {"type": "string"},
                    "type": {"type": "string", "enum": ["page", "component", "layout", "modal", "form", "widget"]},
                    "description": {"type": "string"},
                    "file_path": {"type": "string"},
                    "props": {"type": "array", "items": {"type": "string"}},
                    "children": {"type": "array", "items": {"type": "string"}},
                    "routes": {"type": "array", "items": {"type": "string"}}
                }
            }
        },
        "notes": {"type": "array", "items": {"type": "string"}}
    }
}


def get_example_architecture() -> Architecture:
    """Get an example architecture document for reference."""
    return Architecture(
        project_name="Example Project",
        description="A sample project to demonstrate architecture documentation",
        version="1.0.0",
        tech_stack=[
            TechStackItem(name="Python", category="language", version="3.12", purpose="Backend API"),
            TechStackItem(name="FastAPI", category="framework", version="0.109", purpose="REST API framework"),
            TechStackItem(name="SQLite", category="database", purpose="Data storage"),
            TechStackItem(name="Svelte", category="framework", version="5.0", purpose="Frontend UI"),
        ],
        endpoints=[
            Endpoint(
                method="GET",
                path="/api/users",
                description="List all users",
                params=[
                    EndpointParam(name="limit", type="integer", required=False, location="query"),
                    EndpointParam(name="offset", type="integer", required=False, location="query"),
                ],
                response_type="User[]",
                tags=["users"]
            ),
            Endpoint(
                method="POST",
                path="/api/users",
                description="Create a new user",
                params=[
                    EndpointParam(name="name", type="string", required=True, location="body"),
                    EndpointParam(name="email", type="string", required=True, location="body"),
                ],
                response_type="User",
                tags=["users"]
            ),
        ],
        entities=[
            Entity(
                name="User",
                description="A user account in the system",
                fields=[
                    EntityField(name="id", type="integer", description="Unique identifier"),
                    EntityField(name="name", type="string", description="User's display name"),
                    EntityField(name="email", type="string", description="User's email address", constraints=["unique"]),
                    EntityField(name="created_at", type="datetime", description="Account creation time"),
                ],
                relationships=["has_many: Posts"],
                file_path="models/user.py"
            ),
        ],
        tables=[
            DatabaseTable(
                name="users",
                description="User accounts table",
                columns=[
                    TableColumn(name="id", type="INTEGER", primary_key=True),
                    TableColumn(name="name", type="TEXT", nullable=False),
                    TableColumn(name="email", type="TEXT", nullable=False),
                    TableColumn(name="created_at", type="DATETIME", default="CURRENT_TIMESTAMP"),
                ],
                indexes=[
                    TableIndex(name="idx_users_email", columns=["email"], unique=True),
                ]
            ),
        ],
        ui_components=[
            UIComponent(
                name="UserList",
                type="page",
                description="Displays a list of all users",
                file_path="src/pages/UserList.svelte",
                routes=["/users"]
            ),
            UIComponent(
                name="UserCard",
                type="component",
                description="Displays a single user's information",
                file_path="src/components/UserCard.svelte",
                props=["user: User"]
            ),
        ],
        notes=[
            "Authentication is handled via JWT tokens",
            "All API endpoints require authentication except /api/auth/*"
        ]
    )
