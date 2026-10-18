"""Module for choosing which ripple variant to run, from the configuration."""

from water_ripples.baseline import BaselineRipples
from water_ripples.config_model import ConfigModel
from water_ripples.image_overlay import ImageRipples
from water_ripples.simulation import RippleSimulation
from water_ripples.trapezoid import TrapezoidRipples

_SIMULATION_CLASSES: dict[str, type[RippleSimulation]] = {
    "baseline": BaselineRipples,
    "trapezoid": TrapezoidRipples,
    "image": ImageRipples,
}


def create_simulation(config: ConfigModel) -> RippleSimulation:
    """Create the simulation for the variant named in the configuration.

    Args:
        config (ConfigModel): The validated configuration, with the variant to run.

    Returns:
        simulation (RippleSimulation): The simulation, ready to execute.
    """
    simulation_class = _SIMULATION_CLASSES[config.variant]
    simulation = simulation_class(config=config)

    return simulation
