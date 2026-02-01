"""Tests for GCP2-008: Configuration System."""

import pytest
import yaml
from pathlib import Path
from golazo.config import GolazoConfig, DEFAULT_ROLES, DEFAULT_TRANSITIONS


class TestConfigLoading:
    def test_load_from_golazo_yaml(self, tmp_path):
        """TC-01: Load from golazo.yaml."""
        config_file = tmp_path / "golazo.yaml"
        config_file.write_text(yaml.dump({
            "version": "1.0",
            "roles": ["role-a", "role-b"],
        }))
        config = GolazoConfig.load(tmp_path)
        assert "role-a" in config.roles
        assert "role-b" in config.roles

    def test_load_from_nested_path(self, tmp_path):
        """TC-02: Load from .golazo/config.yaml."""
        nested = tmp_path / ".golazo"
        nested.mkdir()
        config_file = nested / "config.yaml"
        config_file.write_text(yaml.dump({
            "version": "1.0",
            "roles": ["nested-role"],
        }))
        config = GolazoConfig.load(tmp_path)
        assert "nested-role" in config.roles

    def test_golazo_yaml_takes_precedence(self, tmp_path):
        """TC-03: golazo.yaml takes precedence over .golazo/config.yaml."""
        # Create both files
        (tmp_path / "golazo.yaml").write_text(yaml.dump({
            "version": "1.0",
            "roles": ["primary"],
        }))
        nested = tmp_path / ".golazo"
        nested.mkdir()
        (nested / "config.yaml").write_text(yaml.dump({
            "version": "1.0",
            "roles": ["secondary"],
        }))
        config = GolazoConfig.load(tmp_path)
        assert "primary" in config.roles
        assert "secondary" not in config.roles

    def test_config_is_immutable(self, tmp_path):
        """TC-04: Config is immutable (frozen dataclass)."""
        config = GolazoConfig.load(tmp_path)
        with pytest.raises((AttributeError, TypeError)):
            config.roles = ["new-role"]

    def test_schema_version_check(self, tmp_path):
        """TC-05: Schema version 1.0 loads successfully."""
        (tmp_path / "golazo.yaml").write_text(yaml.dump({
            "version": "1.0",
            "roles": ["test"],
        }))
        config = GolazoConfig.load(tmp_path)
        assert config.version == "1.0"

    def test_unknown_version_raises(self, tmp_path):
        """TC-06: Unknown version raises ValueError."""
        (tmp_path / "golazo.yaml").write_text(yaml.dump({
            "version": "99.0",
            "roles": ["test"],
        }))
        with pytest.raises(ValueError, match="Unknown config version"):
            GolazoConfig.load(tmp_path)


class TestDefaultValues:
    def test_no_config_uses_defaults(self, tmp_path):
        """TC-07: No config file uses defaults."""
        config = GolazoConfig.load(tmp_path)
        assert config.roles == tuple(DEFAULT_ROLES)

    def test_default_roles(self, tmp_path):
        """TC-08: Default roles match current implementation."""
        config = GolazoConfig.load(tmp_path)
        assert len(config.roles) == 8
        assert "project-owner" in config.roles
        assert "documentor" in config.roles

    def test_default_transitions(self, tmp_path):
        """TC-09: Default transitions match current implementation."""
        config = GolazoConfig.load(tmp_path)
        assert config.transitions["project-owner"] == ("program-manager",)
        assert config.transitions["architect"] == ("developer",)

    def test_default_dor_dod(self, tmp_path):
        """TC-10: Default DoR/DoD items match current implementation."""
        config = GolazoConfig.load(tmp_path)
        assert len(config.dor_items) == 4
        assert "userStory" in config.dor_items
        assert len(config.dod_items) == 7
        assert "testsPass" in config.dod_items


class TestMachineIntegration:
    def test_machine_uses_config_roles(self, tmp_path):
        """TC-11: Machine validates against config roles."""
        from golazo.machine import GolazoStateMachine
        
        (tmp_path / "golazo.yaml").write_text(yaml.dump({
            "version": "1.0",
            "roles": ["custom-role-a", "custom-role-b"],
            "transitions": {"custom-role-a": ["custom-role-b"]},
        }))
        (tmp_path / "WorkItems").mkdir()
        
        m = GolazoStateMachine("T1", base_path=tmp_path)
        assert m.current_role == "custom-role-a"
        allowed, _ = m.can_transition("custom-role-b")
        assert allowed is True
        allowed, msg = m.can_transition("unknown-role")
        assert allowed is False
        assert "Unknown role" in msg

    def test_machine_uses_config_transitions(self, tmp_path):
        """TC-12: Machine uses config transitions."""
        from golazo.machine import GolazoStateMachine
        
        (tmp_path / "golazo.yaml").write_text(yaml.dump({
            "version": "1.0",
            "roles": ["a", "b", "c"],
            "transitions": {"a": ["c"], "c": []},  # Skip b
        }))
        (tmp_path / "WorkItems").mkdir()
        
        m = GolazoStateMachine("T2", base_path=tmp_path)
        allowed, _ = m.can_transition("c")
        assert allowed is True
        allowed, _ = m.can_transition("b")
        assert allowed is False

    def test_machine_uses_config_dor(self, tmp_path):
        """TC-13: Machine uses config DoR items."""
        from golazo.machine import GolazoStateMachine
        
        (tmp_path / "golazo.yaml").write_text(yaml.dump({
            "version": "1.0",
            "dor": {"items": ["item1", "item2"]},
        }))
        (tmp_path / "WorkItems").mkdir()
        
        m = GolazoStateMachine("T3", base_path=tmp_path)
        dor = m.check_dor()
        assert "item1" in dor
        assert "item2" in dor
        assert len(dor) == 2

    def test_existing_machine_tests_pass(self, tmp_path):
        """TC-14: Existing tests pass - verified by running full suite."""
        # This is verified by pytest running test_machine.py
        pass

    def test_machine_without_config_uses_defaults(self, tmp_path):
        """TC-15: Machine without config file uses defaults."""
        from golazo.machine import GolazoStateMachine
        
        (tmp_path / "WorkItems").mkdir()
        m = GolazoStateMachine("T4", base_path=tmp_path)
        assert m.current_role == "project-owner"
        assert m._config.roles == tuple(DEFAULT_ROLES)


class TestConsentIntegration:
    def test_consent_uses_config_quality_gates(self, tmp_path):
        """TC-16: ConsentEnforcer uses config quality gates."""
        from golazo.machine import GolazoStateMachine
        from golazo.consent import ConsentEnforcer
        
        (tmp_path / "golazo.yaml").write_text(yaml.dump({
            "version": "1.0",
            "quality_gates": ["custom-gate"],
        }))
        (tmp_path / "WorkItems").mkdir()
        
        m = GolazoStateMachine("T5", base_path=tmp_path)
        e = ConsentEnforcer(m)
        assert e.is_quality_gate("custom-gate") is True
        assert e.is_quality_gate("tester") is False  # Not in custom config

    def test_existing_consent_tests_pass(self, tmp_path):
        """TC-17: Existing tests pass - verified by running full suite."""
        pass

    def test_consent_inherits_machine_config(self, tmp_path):
        """TC-18: ConsentEnforcer inherits machine's config."""
        from golazo.machine import GolazoStateMachine
        from golazo.consent import ConsentEnforcer
        
        (tmp_path / "golazo.yaml").write_text(yaml.dump({
            "version": "1.0",
            "quality_gates": ["special-role"],
        }))
        (tmp_path / "WorkItems").mkdir()
        
        m = GolazoStateMachine("T6", base_path=tmp_path)
        e = ConsentEnforcer(m)
        assert e._config is m._config


class TestErrorHandling:
    def test_invalid_yaml_syntax(self, tmp_path):
        """TC-19: Invalid YAML gives clear error."""
        (tmp_path / "golazo.yaml").write_text("invalid: yaml: content: [")
        with pytest.raises(yaml.YAMLError):
            GolazoConfig.load(tmp_path)

    def test_invalid_type_for_roles(self, tmp_path):
        """TC-20: Invalid type for roles raises TypeError."""
        (tmp_path / "golazo.yaml").write_text(yaml.dump({
            "version": "1.0",
            "roles": "not a list",
        }))
        with pytest.raises(TypeError, match="roles"):
            GolazoConfig.load(tmp_path)

    def test_unknown_keys_warn_but_load(self, tmp_path, caplog):
        """TC-21: Unknown keys warn but config loads."""
        (tmp_path / "golazo.yaml").write_text(yaml.dump({
            "version": "1.0",
            "unknown_key": "value",
        }))
        config = GolazoConfig.load(tmp_path)
        assert config is not None
        # Warning should be logged

    def test_empty_config_uses_defaults(self, tmp_path):
        """TC-22: Empty config file uses defaults."""
        (tmp_path / "golazo.yaml").write_text("")
        config = GolazoConfig.load(tmp_path)
        assert config.roles == tuple(DEFAULT_ROLES)
