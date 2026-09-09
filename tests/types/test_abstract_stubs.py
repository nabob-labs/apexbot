"""Tests verifying that empty abstract stubs have been deepened."""

import dataclasses

import apexbot.types.abstract


class TestAbstractSimulationResultDeepened:
    def test_abstract_simulation_result_has_fields(self):
        """AbstractSimulationResult is a dataclass with the shared simulation fields."""
        assert dataclasses.is_dataclass(apexbot.types.abstract.AbstractSimulationResult)
        field_names = {
            f.name for f in dataclasses.fields(apexbot.types.abstract.AbstractSimulationResult)
        }
        assert field_names == {"amount0_delta", "amount1_delta", "initial_state", "final_state"}
