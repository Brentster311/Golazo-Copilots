"""Forward-chaining rule evaluation engine (v2).

Evaluates a set of input facts against the knowledge base rules using
forward chaining. Supports IF/THEN with optional ELSE branches.
Output entity types: CHANGE_STATE, RULED_OUT, GAP.
"""
from __future__ import annotations

from itertools import product

from ees.models import (
    AssertStmt,
    ActStmt,
    Block,
    CheckExpr,
    DecideStmt,
    EvaluationResult,
    Fact,
    GapStmt,
    Goal,
    NoopStmt,
    RetractStmt,
    Rule,
    RuleBlock,
    RuleOutput,
)


class RuleEvaluator:
    """Evaluates rules against input facts using forward chaining."""

    def __init__(self, rules: list[Rule]) -> None:
        self._rules = rules

    def evaluate(self, input_facts: list[Fact], goal: Goal | None = None) -> EvaluationResult:
        """Evaluate all rules against input facts.

        Forward chaining algorithm:
        1. Start with input facts as the working set.
        2. If a goal is declared and its initial fact isn't in input_facts, seed it.
        3. For each CONFIRMED rule:
           a. If conditions met → fire THEN branch, add output to working set
              (unless GAP, which is terminal).
           b. If conditions NOT met and ELSE exists → fire ELSE branch.
        4. After each full iteration, check goal termination:
           - resolved: goal fact reached a terminal value
           - escalated: a GAP fired while goal is in_progress
        5. Repeat until no new facts are derived (fixed-point) or goal terminates.

        Returns EvaluationResult with outputs, fired rules, trace, and goal_status.
        """
        # Build working set keyed by match_key for O(1) lookup
        working_keys: set[tuple] = set()
        working_facts: list[Fact] = list(input_facts)
        for f in input_facts:
            working_keys.add(f.match_key())

        # Seed goal initial fact if not already present (EES-00018)
        if goal is not None:
            goal_seed = Fact(
                noun=goal.noun, instance=goal.instance,
                property=goal.property, operator="==", value=goal.initial,
            )
            if goal_seed.match_key() not in working_keys:
                working_keys.add(goal_seed.match_key())
                working_facts.append(goal_seed)

        # Check if goal is already resolved before first iteration
        if goal is not None and self._goal_resolved(goal, working_keys):
            return EvaluationResult(
                input_facts=list(input_facts),
                derived_facts=[],
                fired_rules=[],
                outputs=[],
                rule_trace=[],
                goal_status="resolved",
            )

        confirmed_rules = [r for r in self._rules if r.status == "CONFIRMED"]

        fired_rules: list[Rule] = []
        fired_rule_ids: set[str] = set()
        derived_facts: list[Fact] = []
        outputs: list[dict] = []
        rule_trace: list[dict] = []
        iteration = 0
        gap_fired_this_iteration = False

        # Forward chaining loop
        changed = True
        while changed:
            changed = False
            iteration += 1
            gap_fired_this_iteration = False
            for rule in confirmed_rules:
                if rule.rule_id in fired_rule_ids:
                    continue

                # Check conditions
                has_vars = any(c.has_variables for c in rule.conditions.items)
                if not has_vars:
                    conditions_met = self._conditions_met(rule, working_keys)
                else:
                    bindings = self._conditions_met_with_bindings(
                        rule, working_facts,
                    )
                    conditions_met = bindings is not None

                if conditions_met:
                    # THEN branch fires
                    output = rule.then
                    branch = "then"
                else:
                    # ELSE branch fires (if present)
                    if rule.else_ is None:
                        continue
                    output = rule.else_
                    branch = "else"

                # Record output
                outputs.append({
                    "rule_id": rule.rule_id,
                    "branch": branch,
                    "output": output,
                })

                # Track GAP firing for goal escalation
                if output.kind == "GAP":
                    gap_fired_this_iteration = True

                # Add derived fact to working set (GAP is terminal — not added)
                if output.kind != "GAP":
                    derived = output.to_fact()
                    derived_key = derived.match_key()
                    if derived_key not in working_keys:
                        working_keys.add(derived_key)
                        working_facts.append(derived)
                        derived_facts.append(derived)
                        changed = True

                fired_rules.append(rule)
                fired_rule_ids.add(rule.rule_id)
                rule_trace.append({
                    "rule_id": rule.rule_id,
                    "iteration": iteration,
                    "branch": branch,
                    "derived": f"{output.kind}(\"{output.description}\")",
                })

                # Per-rule goal termination check (EES-00018)
                if goal is not None:
                    if self._goal_resolved(goal, working_keys):
                        return EvaluationResult(
                            input_facts=list(input_facts),
                            derived_facts=derived_facts,
                            fired_rules=fired_rules,
                            outputs=outputs,
                            rule_trace=rule_trace,
                            goal_status="resolved",
                        )

            # End-of-iteration goal escalation check (EES-00018)
            if goal is not None and gap_fired_this_iteration:
                return EvaluationResult(
                    input_facts=list(input_facts),
                    derived_facts=derived_facts,
                    fired_rules=fired_rules,
                    outputs=outputs,
                    rule_trace=rule_trace,
                    goal_status="escalated",
                )

        # Fixed-point reached — determine final goal_status
        goal_status = "in_progress" if goal is not None else None

        return EvaluationResult(
            input_facts=list(input_facts),
            derived_facts=derived_facts,
            fired_rules=fired_rules,
            outputs=outputs,
            rule_trace=rule_trace,
            goal_status=goal_status,
        )

    # ---- goal helpers ---------------------------------------------------------

    @staticmethod
    def _goal_resolved(goal: Goal, working_keys: set[tuple]) -> bool:
        """Check if any terminal value is in the working set for the goal property."""
        for terminal_val in goal.terminal:
            key = (goal.noun.lower(), goal.instance, goal.property.lower(), "==", terminal_val)
            if key in working_keys:
                return True
        return False

    # ---- condition matching ---------------------------------------------------

    @staticmethod
    def _conditions_met(rule: Rule, working_keys: set[tuple]) -> bool:
        """Check if a rule's conditions are satisfied by the working set (no variables)."""
        if not rule.conditions.items:
            return False

        if rule.conditions.logic == "OR":
            return any(
                item.match_key() in working_keys
                for item in rule.conditions.items
            )
        else:  # AND (default)
            return all(
                item.match_key() in working_keys
                for item in rule.conditions.items
            )

    # ---- variable binding (slow path) ----------------------------------------

    @classmethod
    def _unify_condition(
        cls,
        condition: Fact,
        fact: Fact,
    ) -> dict[str, str] | None:
        """Try to unify *condition* with *fact*, returning a binding dict.

        Non-variable fields must match exactly (case-insensitive for
        noun/property, exact for operator/instance/value). Variable fields
        bind to the corresponding fact field.

        Returns None on mismatch.
        """
        if condition.noun.lower() != fact.noun.lower():
            return None
        if condition.property.lower() != fact.property.lower():
            return None
        if condition.operator != fact.operator:
            return None

        bindings: dict[str, str] = {}

        # Instance field
        if Fact.is_variable(condition.instance):
            bindings[condition.instance] = fact.instance
        elif condition.instance != fact.instance:
            return None

        # Value field
        if Fact.is_variable(condition.value):
            bindings[condition.value] = fact.value
        elif condition.value != fact.value:
            return None

        return bindings

    @classmethod
    def _conditions_met_with_bindings(
        cls,
        rule: Rule,
        working_facts: list[Fact],
    ) -> dict[str, str] | None:
        """Check conditions with variable binding.  Returns bindings dict or None.

        AND logic: all conditions must match with a consistent binding.
        OR logic: any single condition match is sufficient.
        """
        conditions = rule.conditions.items
        if not conditions:
            return None

        if rule.conditions.logic == "OR":
            # Any single condition match is enough
            for cond in conditions:
                for fact in working_facts:
                    b = cls._unify_condition(cond, fact)
                    if b is not None:
                        return b
            return None

        # AND logic — gather candidates per condition, then find consistent binding
        candidates_per_cond: list[list[dict[str, str]]] = []
        for cond in conditions:
            cands: list[dict[str, str]] = []
            for fact in working_facts:
                b = cls._unify_condition(cond, fact)
                if b is not None:
                    cands.append(b)
            if not cands:
                return None  # no match for this condition at all
            candidates_per_cond.append(cands)

        # Try all combinations (Cartesian product) to find consistent binding
        for combo in product(*candidates_per_cond):
            merged: dict[str, str] = {}
            ok = True
            for b in combo:
                for var, val in b.items():
                    if var in merged and merged[var] != val:
                        ok = False
                        break
                    merged[var] = val
                if not ok:
                    break
            if ok:
                return merged

        return None


# ── AST-based evaluator (EES-00019) ──────────────────────────────────


class ASTEvaluator:
    """Forward-chaining evaluator for the deterministic rule language.

    Operates on ``RuleBlock`` AST nodes instead of the legacy ``Rule`` model.
    Working memory is a mutable set of ``Fact`` objects.
    """

    def __init__(
        self,
        rules: list[RuleBlock],
        *,
        max_iterations: int = 100,
    ) -> None:
        # Sort rules by rule_id for deterministic execution order (RC-4)
        self._rules = sorted(rules, key=lambda r: r.rule_id)
        self._max_iterations = max_iterations

    # ── public API ────────────────────────────────────────────────────

    def evaluate(
        self,
        input_facts: list[Fact],
        goal: Goal | None = None,
    ) -> EvaluationResult:
        """Execute all rules against *input_facts* until fixed-point or goal termination.

        Returns an ``EvaluationResult`` with derived facts, trace, and goal_status.
        """
        # Build mutable working memory
        wm: dict[tuple, Fact] = {}
        for f in input_facts:
            wm[f.match_key()] = f

        # Seed goal initial fact if declared and not present
        if goal is not None:
            seed = Fact(
                noun=goal.noun, instance=goal.instance,
                property=goal.property, operator="==", value=goal.initial,
            )
            if seed.match_key() not in wm:
                wm[seed.match_key()] = seed

        # Check if goal already resolved
        if goal is not None and self._goal_resolved(goal, wm):
            return EvaluationResult(
                input_facts=list(input_facts),
                derived_facts=[],
                fired_rules=[],
                outputs=[],
                rule_trace=[],
                goal_status="resolved",
            )

        trace: list[dict] = []
        derived: list[Fact] = []
        fired_rule_ids: list[str] = []
        iteration = 0
        input_keys = {f.match_key() for f in input_facts}

        while iteration < self._max_iterations:
            iteration += 1
            snapshot = set(wm.keys())

            for rule in self._rules:
                self._execute_block(rule.block, rule.rule_id, wm, trace)

                # Goal check after each rule
                if goal is not None and self._goal_resolved(goal, wm):
                    self._collect_derived(wm, input_keys, derived)
                    if rule.rule_id not in fired_rule_ids:
                        fired_rule_ids.append(rule.rule_id)
                    return EvaluationResult(
                        input_facts=list(input_facts),
                        derived_facts=derived,
                        fired_rules=[],  # legacy field, not used for AST rules
                        outputs=[],
                        rule_trace=trace,
                        goal_status="resolved",
                    )

                if rule.rule_id not in fired_rule_ids:
                    fired_rule_ids.append(rule.rule_id)

            # Check for goal escalation (any GAP in this iteration)
            if goal is not None:
                gap_in_iter = any(
                    t.get("stmt_kind") == "GAP" and t.get("iteration") == iteration
                    for t in trace
                )
                if gap_in_iter:
                    self._collect_derived(wm, input_keys, derived)
                    return EvaluationResult(
                        input_facts=list(input_facts),
                        derived_facts=derived,
                        fired_rules=[],
                        outputs=[],
                        rule_trace=trace,
                        goal_status="escalated",
                    )

            # Fixed-point check: did working memory change?
            if set(wm.keys()) == snapshot:
                break

        # Determine final status
        if iteration >= self._max_iterations and set(wm.keys()) != snapshot:
            goal_status = "max_iterations"
        elif goal is not None:
            goal_status = "in_progress"
        else:
            goal_status = None

        self._collect_derived(wm, input_keys, derived)
        return EvaluationResult(
            input_facts=list(input_facts),
            derived_facts=derived,
            fired_rules=[],
            outputs=[],
            rule_trace=trace,
            goal_status=goal_status,
        )

    # ── block / statement execution ───────────────────────────────────

    def _execute_block(
        self,
        block: Block,
        rule_id: str,
        wm: dict[tuple, Fact],
        trace: list[dict],
        iteration: int | None = None,
    ) -> None:
        """Execute all statements in *block* sequentially."""
        for stmt in block.stmts:
            if isinstance(stmt, DecideStmt):
                self._execute_decide(stmt, rule_id, wm, trace, iteration)
            elif isinstance(stmt, AssertStmt):
                self._execute_assert(stmt, rule_id, wm, trace, iteration)
            elif isinstance(stmt, RetractStmt):
                self._execute_retract(stmt, rule_id, wm, trace, iteration)
            elif isinstance(stmt, ActStmt):
                self._execute_act(stmt, rule_id, trace, iteration)
            elif isinstance(stmt, NoopStmt):
                trace.append({
                    "rule_id": rule_id,
                    "stmt_kind": "NOOP",
                    "iteration": iteration,
                })
            elif isinstance(stmt, GapStmt):
                trace.append({
                    "rule_id": rule_id,
                    "stmt_kind": "GAP",
                    "description": stmt.description,
                    "iteration": iteration,
                })

    def _execute_decide(
        self,
        stmt: DecideStmt,
        rule_id: str,
        wm: dict[tuple, Fact],
        trace: list[dict],
        iteration: int | None = None,
    ) -> None:
        """Evaluate CHECK and branch into then or else block."""
        check_result = self._check(stmt.check, wm)
        trace.append({
            "rule_id": rule_id,
            "stmt_kind": "CHECK",
            "expression": f"{stmt.check.noun}({stmt.check.instance}).{stmt.check.property} "
                          f"{stmt.check.operator} {stmt.check.value}",
            "result": check_result,
            "iteration": iteration,
        })
        if check_result:
            self._execute_block(stmt.then_block, rule_id, wm, trace, iteration)
        else:
            self._execute_block(stmt.else_block, rule_id, wm, trace, iteration)

    def _execute_assert(
        self,
        stmt: AssertStmt,
        rule_id: str,
        wm: dict[tuple, Fact],
        trace: list[dict],
        iteration: int | None = None,
    ) -> None:
        """Add (or overwrite) a fact in working memory."""
        fact = Fact(
            noun=stmt.noun,
            instance=stmt.instance,
            property=stmt.property,
            operator=stmt.operator,
            value=stmt.value,
        )
        wm[fact.match_key()] = fact
        trace.append({
            "rule_id": rule_id,
            "stmt_kind": "ASSERT",
            "fact": fact.to_display(),
            "iteration": iteration,
        })

    def _execute_retract(
        self,
        stmt: RetractStmt,
        rule_id: str,
        wm: dict[tuple, Fact],
        trace: list[dict],
        iteration: int | None = None,
    ) -> None:
        """Remove all facts matching (noun, instance, property) from working memory."""
        to_remove = [
            key for key, f in wm.items()
            if f.noun.lower() == stmt.noun.lower()
            and f.instance == stmt.instance
            and f.property.lower() == stmt.property.lower()
        ]
        for key in to_remove:
            removed_fact = wm.pop(key)
            trace.append({
                "rule_id": rule_id,
                "stmt_kind": "RETRACT",
                "fact": removed_fact.to_display(),
                "iteration": iteration,
            })

    def _execute_act(
        self,
        stmt: ActStmt,
        rule_id: str,
        trace: list[dict],
        iteration: int | None = None,
    ) -> None:
        """Record an ACT (side-effect) in the trace."""
        trace.append({
            "rule_id": rule_id,
            "stmt_kind": "ACT",
            "description": stmt.description,
            "iteration": iteration,
        })

    # ── CHECK evaluation ──────────────────────────────────────────────

    @staticmethod
    def _check(expr: CheckExpr, wm: dict[tuple, Fact]) -> bool:
        """Evaluate a CHECK expression against working memory.

        For ``==`` / ``!=``: exact match on (noun, instance, property, op, value).
        For other operators: find a fact matching (noun, instance, property)
        and compare values.
        """
        if expr.operator == "==":
            key = (expr.noun.lower(), expr.instance, expr.property.lower(), "==", expr.value)
            return key in wm
        if expr.operator == "!=":
            eq_key = (expr.noun.lower(), expr.instance, expr.property.lower(), "==", expr.value)
            # True if there's no fact with that exact value
            # (i.e., a fact exists for the property but with a different value, or no fact at all)
            return eq_key not in wm

        # Numeric / string comparison for >, <, >=, <=
        for key, fact in wm.items():
            if (fact.noun.lower() == expr.noun.lower()
                    and fact.instance == expr.instance
                    and fact.property.lower() == expr.property.lower()):
                try:
                    fv = float(fact.value)
                    ev = float(expr.value)
                except (ValueError, TypeError):
                    fv, ev = fact.value, expr.value  # type: ignore[assignment]
                if expr.operator == ">":
                    return fv > ev
                if expr.operator == "<":
                    return fv < ev
                if expr.operator == ">=":
                    return fv >= ev
                if expr.operator == "<=":
                    return fv <= ev
                if expr.operator == "contains":
                    return str(expr.value) in str(fact.value)
                if expr.operator == "!contains":
                    return str(expr.value) not in str(fact.value)
        return False

    # ── goal helpers ──────────────────────────────────────────────────

    @staticmethod
    def _goal_resolved(goal: Goal, wm: dict[tuple, Fact]) -> bool:
        """Check if any terminal value for the goal is in working memory."""
        for terminal_val in goal.terminal:
            key = (goal.noun.lower(), goal.instance, goal.property.lower(), "==", terminal_val)
            if key in wm:
                return True
        return False

    # ── derived-fact collection ────────────────────────────────────────

    @staticmethod
    def _collect_derived(
        wm: dict[tuple, Fact],
        input_keys: set[tuple],
        derived: list[Fact],
    ) -> None:
        """Populate *derived* with facts in *wm* that weren't in the original input."""
        derived.clear()
        for key, fact in wm.items():
            if key not in input_keys:
                derived.append(fact)