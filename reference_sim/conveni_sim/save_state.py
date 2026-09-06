from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


JsonScalar = str | int | float | bool | None
JsonValue = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]


def _validate_json_value(value: Any, *, path: str) -> JsonValue:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, list):
        return [
            _validate_json_value(item, path=f"{path}[{index}]")
            for index, item in enumerate(value)
        ]
    if isinstance(value, dict):
        validated: dict[str, JsonValue] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError(f"save-state key at {path} must be str, got {type(key).__name__}")
            validated[key] = _validate_json_value(item, path=f"{path}.{key}")
        return validated
    raise TypeError(
        f"save-state value at {path} must be JSON-compatible, got {type(value).__name__}"
    )


@dataclass(frozen=True)
class SaveStateEnvelope:
    """Versioned, formula-free container for deterministic runtime state.

    Components are deliberately opaque to this layer. A subsystem owns its own schema and
    can preserve unresolved observations as ``None`` or explicit structured values rather
    than forcing the save layer to invent defaults.
    """

    schema_version: int
    components: dict[str, JsonValue]

    @classmethod
    def capture(
        cls,
        *,
        schema_version: int,
        components: Mapping[str, Any],
    ) -> "SaveStateEnvelope":
        if schema_version < 1:
            raise ValueError("schema_version must be >= 1")

        normalized: dict[str, JsonValue] = {}
        for component_id, payload in components.items():
            if not isinstance(component_id, str) or not component_id:
                raise ValueError("component ids must be non-empty strings")
            normalized[component_id] = _validate_json_value(
                payload,
                path=f"components.{component_id}",
            )
        return cls(schema_version=schema_version, components=normalized)

    def to_document(self) -> dict[str, JsonValue]:
        return {
            "schema_version": self.schema_version,
            "components": _validate_json_value(self.components, path="components"),
        }

    @classmethod
    def from_document(cls, document: Mapping[str, Any]) -> "SaveStateEnvelope":
        expected_keys = {"schema_version", "components"}
        extra_keys = set(document) - expected_keys
        if extra_keys:
            raise ValueError(f"unsupported save-state envelope keys: {sorted(extra_keys)}")

        schema_version = document.get("schema_version")
        if not isinstance(schema_version, int) or isinstance(schema_version, bool):
            raise TypeError("schema_version must be an integer")

        components = document.get("components")
        if not isinstance(components, Mapping):
            raise TypeError("components must be a mapping")

        return cls.capture(schema_version=schema_version, components=components)

    def component(self, component_id: str) -> JsonValue | None:
        """Return a saved component without manufacturing a missing default."""

        return self.components.get(component_id)
