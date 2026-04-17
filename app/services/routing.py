from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Callable

from app.models import Profile, RoutingRule


@dataclass(slots=True)
class EmailContext:
    account_id: int
    account_name: str
    sender: str
    subject: str
    has_attachments: bool
    metadata: dict[str, Any] = field(default_factory=dict)


class RoutingEngine:
    """Детерминированный и расширяемый rule-engine.

    Порядок:
    1. Профиль должен быть enabled.
    2. Rule-матчинг по account/sender/subject.
    3. Базовая фильтрация (attachments + raw_expr_json).
    """

    def __init__(self) -> None:
        self._operators: dict[str, Callable[[Any, EmailContext], bool]] = {
            "eq": self._op_eq,
            "contains": self._op_contains,
            "regex": self._op_regex,
            "in": self._op_in,
        }

    def register_operator(self, name: str, fn: Callable[[Any, EmailContext], bool]) -> None:
        """Позволяет расширять движок пользовательскими операторами."""
        self._operators[name] = fn

    def select_rules(self, profile: Profile, email: EmailContext) -> list[RoutingRule]:
        """Возвращает список совпавших правил в детерминированном порядке."""
        if not profile.enabled:
            return []

        ordered_rules = sorted(
            (rule for rule in profile.routing_rules if rule.enabled),
            key=lambda rule: (rule.priority, rule.id),
        )

        matches: list[RoutingRule] = []
        for rule in ordered_rules:
            if not self._matches_account_sender_subject(rule, email):
                continue
            if not self._matches_basic_filters(rule, email):
                continue
            matches.append(rule)
        return matches

    def match_first(self, profile: Profile, email: EmailContext) -> RoutingRule | None:
        rules = self.select_rules(profile, email)
        return rules[0] if rules else None

    def _matches_account_sender_subject(self, rule: RoutingRule, email: EmailContext) -> bool:
        if rule.account_match and not self._match_account(rule.account_match, email):
            return False
        if rule.sender_regex and not re.search(rule.sender_regex, email.sender):
            return False
        if rule.subject_regex and not re.search(rule.subject_regex, email.subject):
            return False
        return True

    def _matches_basic_filters(self, rule: RoutingRule, email: EmailContext) -> bool:
        if rule.has_attachments is not None and rule.has_attachments != email.has_attachments:
            return False
        if rule.raw_expr_json and not self._eval_expr(rule.raw_expr_json, email):
            return False
        return True

    def _match_account(self, account_match: str, email: EmailContext) -> bool:
        normalized_match = account_match.strip().lower()
        return normalized_match in {str(email.account_id), email.account_name.lower()}

    def _eval_expr(self, expr: dict[str, Any], email: EmailContext) -> bool:
        """Оценивает JSON-выражение формата:

        {
          "field": "metadata.priority",
          "op": "eq",
          "value": "high"
        }
        """
        field = expr.get("field")
        operator = expr.get("op", "eq")
        value = expr.get("value")

        if not field or operator not in self._operators:
            return False

        actual_value = self._extract_field_value(field, email)
        return self._operators[operator](
            {
                "actual": actual_value,
                "expected": value,
            },
            email,
        )

    @staticmethod
    def _extract_field_value(field: str, email: EmailContext) -> Any:
        parts = field.split(".")

        if parts[0] == "metadata":
            current: Any = email.metadata
            for part in parts[1:]:
                if not isinstance(current, dict):
                    return None
                current = current.get(part)
            return current

        if hasattr(email, parts[0]):
            return getattr(email, parts[0])
        return None

    @staticmethod
    def _op_eq(payload: Any, _: EmailContext) -> bool:
        return payload["actual"] == payload["expected"]

    @staticmethod
    def _op_contains(payload: Any, _: EmailContext) -> bool:
        actual = payload["actual"]
        expected = payload["expected"]
        if actual is None:
            return False
        return str(expected) in str(actual)

    @staticmethod
    def _op_regex(payload: Any, _: EmailContext) -> bool:
        actual = payload["actual"]
        expected = payload["expected"]
        if actual is None:
            return False
        return re.search(str(expected), str(actual)) is not None

    @staticmethod
    def _op_in(payload: Any, _: EmailContext) -> bool:
        expected = payload["expected"]
        if not isinstance(expected, list):
            return False
        return payload["actual"] in expected
