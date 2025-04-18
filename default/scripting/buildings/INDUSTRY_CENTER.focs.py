from buildings.buildings_macros import SPECIES_LIKES_OR_DISLIKES_BUILDING_STABILITY_EFFECTS
from focs._effects import (
    Contains,
    EffectsGroup,
    Focus,
    Happiness,
    IsBuilding,
    IsSource,
    NamedReal,
    OwnedBy,
    OwnerHasTech,
    Planet,
    ResourceSupplyConnected,
    SetTargetIndustry,
    Source,
    Target,
    TargetPopulation,
    Value,
)
from macros.base_prod import BUILDING_COST_MULTIPLIER, INDUSTRY_PER_POP
from macros.enqueue import ENQUEUE_BUILD_ONE_PER_PLANET

try:
    from focs._buildings import *
except ModuleNotFoundError:
    pass

BuildingType(  # type: ignore[reportUnboundVariable]
    name="BLD_INDUSTRY_CENTER",
    description="BLD_INDUSTRY_CENTER_DESC",
    buildcost=75 * BUILDING_COST_MULTIPLIER,
    buildtime=5,
    location=(
        Planet()
        & ~Contains(IsBuilding(name=["BLD_INDUSTRY_CENTER"]))
        & OwnedBy(empire=Source.Owner)
        & TargetPopulation(low=1)
    ),
    enqueuelocation=ENQUEUE_BUILD_ONE_PER_PLANET,
    effectsgroups=[
        *SPECIES_LIKES_OR_DISLIKES_BUILDING_STABILITY_EFFECTS,
        # Defining the better effect first simplifies the definition.
        # Activation no longer excludes the availibity of the improved effect, thus ensuring
        # lower effects are not lost on planets lacking the higher stability demand for the
        # improved effects.
        # The stacking group not only ensures that multiple centers don't stack, but also that
        # only the best possible effect is used.
        EffectsGroup(
            scope=(
                Planet()
                & OwnedBy(empire=Source.Owner)
                & Happiness(low=NamedReal(name="BLD_INDUSTRY_CENTER_3_MIN_STABILITY", value=12))
                & ResourceSupplyConnected(empire=Source.Owner, condition=IsSource)
                & Focus(type=["FOCUS_INDUSTRY"])
            ),
            activation=(OwnerHasTech(name="PRO_INDUSTRY_CENTER_III")),
            stackinggroup="INDUSTRY_CENTER_STACK",
            effects=[
                SetTargetIndustry(
                    value=Value
                    + Target.Population
                    * NamedReal(name="BLD_INDUSTRY_CENTER_3_TARGET_INDUSTRY_PERPOP", value=0.75 * INDUSTRY_PER_POP)
                )
            ],
        ),
        EffectsGroup(
            scope=(
                Planet()
                & OwnedBy(empire=Source.Owner)
                & Happiness(low=NamedReal(name="BLD_INDUSTRY_CENTER_2_MIN_STABILITY", value=10))
                & ResourceSupplyConnected(empire=Source.Owner, condition=IsSource)
                & Focus(type=["FOCUS_INDUSTRY"])
            ),
            activation=(OwnerHasTech(name="PRO_INDUSTRY_CENTER_II")),
            stackinggroup="INDUSTRY_CENTER_STACK",
            effects=[
                SetTargetIndustry(
                    value=Value
                    + Target.Population
                    * NamedReal(name="BLD_INDUSTRY_CENTER_2_TARGET_INDUSTRY_PERPOP", value=0.5 * INDUSTRY_PER_POP)
                )
            ],
        ),
        EffectsGroup(
            scope=(
                Planet()
                & OwnedBy(empire=Source.Owner)
                & Happiness(low=NamedReal(name="BLD_INDUSTRY_CENTER_1_MIN_STABILITY", value=8))
                & Focus(type=["FOCUS_INDUSTRY"])
                & ResourceSupplyConnected(empire=Source.Owner, condition=IsSource)
            ),
            activation=(OwnerHasTech(name="PRO_INDUSTRY_CENTER_I")),
            stackinggroup="INDUSTRY_CENTER_STACK",
            effects=[
                SetTargetIndustry(
                    value=Value
                    + Target.Population
                    * NamedReal(name="BLD_INDUSTRY_CENTER_1_TARGET_INDUSTRY_PERPOP", value=0.25 * INDUSTRY_PER_POP)
                )
            ],
        ),
    ],
    icon="icons/tech/industrial_centre_ii.png",
)
