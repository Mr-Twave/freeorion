from focs._effects import (
    BuildBuilding,
    Capital,
    Conditional,
    ContainedBy,
    Contains,
    ContentFocus,
    CurrentTurn,
    EffectsGroup,
    EmpireMeterValue,
    EnemyOf,
    Enqueued,
    Fleet,
    GasGiantType,
    GenerateSitRepMessage,
    IsBuilding,
    IsSource,
    LocalCandidate,
    Location,
    Number,
    OneOf,
    OwnedBy,
    OwnerHasTech,
    Planet,
    RootCandidate,
    Ship,
    Source,
    Stationary,
    System,
    Target,
    Turn,
    TurnTechResearched,
    Unowned,
    UserString,
    VisibleToEmpire,
)
from macros.priorities import END_CLEANUP_PRIORITY

ETA_NEXT_TURN = CurrentTurn + LocalCandidate.ETA - 1

# The UserSitRepLabel tags and data are required if the message template (and label) is simply provided here rather than being drawn from the stringtable.
# The data value for the UserSitRepLabel serves as the label to be used in the SitReps filters, and Custom_1 through Custom_4
# will be at the top of the SitReps display.  As seen below, other labels are fine as well, but they cannot have any spaces if you want to use them in the SITREP_PRIORITY_ORDER
# More information on the scripting language used for these is available on our wiki;
# a suitable place to start is http:# www.freeorion.org/index.php/Free_Orion_Content_Script_(FOCS)


# Important, the following line "effectsgroups = [" is functional and important, do not change it
effectsgroups = [
    # normally, for a custom sitrep the player will write their own message here, and label, and not look them up in the Stringtable.  For this first custom sitrep,
    # however, since it is the primary way we introduce the custom sitrep capability to players, we use stringtable references so that the message and label may be more
    # readily translated into multiple languages as part of our standard distribution.
    EffectsGroup(
        scope=IsSource,
        activation=Turn(low=0, high=0),
        effects=GenerateSitRepMessage(
            message="CUSTOM_SITREP_INTRODUCTION",
            label="SITREP_WELCOME_LABEL",
            icon="icons/tech/categories/spy.png",
            parameters={"tech": "SPY_CUSTOM_ADVISORIES", "system": Target.SystemID},
            empire=Source.Owner,
        ),
    ),
    # for reference, the following is fully custom format (in english) of the intrduction sitrep above, except that it has a different label.
    # Note that the message and label are directly provided here rather than being stringtable keys,
    # and the NoStringtableLookup keyword is used afer the label is given.
    # If you are using a stringtable other than English, your translator may have translated the four preset labels for you,
    # so instead of the "Custom_1" below it might be something else for you.  The actual labels can be seen in the Pedia entry for
    # the SPY_CUSTOM_ADVISORIES tech (the tech is named "Empire Intelligence Agency" in the English version)
    #
    # EffectsGroup
    # scope = Source
    # activation = Turn low = 0 high = 0
    # effects =
    # GenerateSitRepMessage
    # message = "This is a sample Custom Sitrep, which is enabled by %tech% and all the busy empire servants reporting information back to %system%"
    # label = "Custom_1"
    # NoStringtableLookup
    # icon = "icons/tech/categories/spy.png"
    # parameters = [
    # tag = "tech" data = "SPY_CUSTOM_ADVISORIES"
    # tag = "system" data = Target.SystemID
    # ]
    # empire = Source.Owner
    #
    # EffectsGroup
    # scope = Source
    # activation = Turn low = 0 high = 0
    # effects =
    # GenerateSitRepMessage
    # message = "A number: %rawtext:number%  A boolean value: %rawtext:boolean%"
    # label = "Custom_1"
    # NoStringtableLookup
    # icon = "icons/tech/categories/spy.png"
    # parameters = [
    # tag = "number" data = GameRule name = "RULE_NUM_COMBAT_ROUNDS"
    # tag = "boolean" data = GameRule name = "RULE_CHEAP_AND_FAST_TECH_RESEARCH"
    # ]
    # empire = Source.Owner
    # Reminder if a Gas Giant you own in a system along with another planet you also own, populated by a species with Industry Focus, and you have the Orbital Generation tech
    # but haven't yet built or enqueued a GG Generator in that system yet
    EffectsGroup(
        scope=Planet()
        & Planet(type=[GasGiantType])
        & OwnedBy(empire=Source.Owner)
        & ~Contains(IsBuilding(name=["BLD_GAS_GIANT_GEN"]))
        & ContainedBy(
            Contains(
                Planet()
                & Location(type=ContentFocus, name=LocalCandidate.Species, name2="FOCUS_INDUSTRY")
                & OwnedBy(empire=Source.Owner)
            )
            & ~Contains(
                Planet()
                & OwnedBy(empire=Source.Owner)
                & (
                    Contains(IsBuilding(name=["BLD_GAS_GIANT_GEN"]))
                    | Enqueued(type=BuildBuilding, name="BLD_GAS_GIANT_GEN")
                )
            )
        ),
        activation=OwnerHasTech(name="PRO_ORBITAL_GEN"),
        effects=GenerateSitRepMessage(
            message="SITREP_GAS_GIANT_GENERATION_REMINDER",
            label="CUSTOM_2",
            icon="icons/building/gas-giant-generator.png",
            parameters={"buildingtype": "BLD_GAS_GIANT_GEN", "planet": Target.ID},
            empire=Source.Owner,
        ),
    ),
    # Tell all the others that you have better detection tech (the information is public anyway)
    EffectsGroup(
        scope=Capital & ~OwnedBy(empire=Source.Owner),
        activation=(CurrentTurn == TurnTechResearched(empire=Source.Owner, name="SPY_DETECT_2"))
        | (CurrentTurn == TurnTechResearched(empire=Source.Owner, name="SPY_DETECT_3"))
        | (CurrentTurn == TurnTechResearched(empire=Source.Owner, name="SPY_DETECT_4"))
        | (CurrentTurn == TurnTechResearched(empire=Source.Owner, name="SPY_DETECT_5")),
        priority=END_CLEANUP_PRIORITY,
        effects=GenerateSitRepMessage(
            message="SITREP_EMPIRE_TECH_RESEARCHED_DETECTION",
            label="SITREP_EMPIRE_TECH_RESEARCHED_DETECTION_LABEL",
            icon="icons/meter/detection.png",
            parameters={
                "empire": Source.Owner,
                "dstrength": EmpireMeterValue(empire=Source.Owner, meter="METER_DETECTION_STRENGTH"),
            },
            empire=Target.Owner,
        ),
    ),
    EffectsGroup(
        scope=System
        &
        # The following assets need protection
        Contains((Planet() | Ship) & OwnedBy(empire=Source.Owner))
        &
        # Don't warn about system where there are already enemies this turn
        ~Contains(
            Ship & (OwnedBy(affiliation=EnemyOf, empire=Source.Owner) | Unowned) & VisibleToEmpire(empire=Source.Owner)
        ),
        activation=IsSource,
        priority=END_CLEANUP_PRIORITY,
        effects=Conditional(
            condition=Number(
                low=1,
                condition=Fleet
                & ~Stationary
                & (OwnedBy(affiliation=EnemyOf, empire=Source.Owner) | Unowned)
                & VisibleToEmpire(empire=Source.Owner)
                & Turn(low=ETA_NEXT_TURN, high=ETA_NEXT_TURN)
                & (RootCandidate.ID == LocalCandidate.NextSystemID),
            ),
            effects=[
                GenerateSitRepMessage(
                    message="SITREP_SYSTEM_GOT_INCOMING_WARNING",
                    label="SITREP_SYSTEM_GOT_INCOMING_WARNING_LABEL",
                    icon="icons/meter/ammo.png",
                    parameters={"system": Target.ID},
                    empire=Source.Owner,
                )
            ],
        ),
    ),
    # *********************************************************************************************************************************************************
    # The other example sitreps below are left in English, but can be translated just by changing the strings provided below for the messages and labels below.
    # It is important to note that, unlike the above entry, these entries all use the  NoStringtableLookup keyword after the label.
    # *********************************************************************************************************************************************************
    # Reminder if a Gas Giant you own in a system along with another planet you also own, populated by a species with Industry Focus, and you have the Orbital Generation tech
    # but haven't yet built or enqueued a GG Generator in that system yet
    # EffectsGroup
    # scope = And [
    # Planet
    # Planet Type = GasGiant
    # OwnedBy empire = Source.Owner
    # Not Contains Building name = "BLD_GAS_GIANT_GEN"
    # ContainedBy And [
    # Contains And [
    # Planet
    # Location type = Focus name = LocalCandidate.Species name = "FOCUS_INDUSTRY"
    # OwnedBy empire = Source.Owner
    # ]
    # Not Contains And [
    # Planet
    # OwnedBy empire = Source.Owner
    # Or [
    # Contains Building name = "BLD_GAS_GIANT_GEN"
    # Enqueued type = Building name = "BLD_GAS_GIANT_GEN"
    # ]
    # ]
    # ]
    # ]
    # activation = OwnerHasTech name = "PRO_ORBITAL_GEN"
    # effects =
    # GenerateSitRepMessage
    # message = "%planet% is a prime location for a %buildingtype%, but none is being built there"
    # label = "Custom_2"
    # NoStringtableLookup
    # icon = "icons/building/gas-giant-generator.png"
    # parameters = [
    # tag = "buildingtype" data = "BLD_GAS_GIANT_GEN"
    # tag = "planet" data = Target.ID
    # ]
    # empire = Source.Owner
    # Reminder if you own a planet with a monster nest but haven't yet researched SHP_DOMESTIC_MONSTER
    # EffectsGroup
    # scope = And [
    # Planet
    # OwnedBy empire = Source.Owner
    # Or [
    # HasSpecial name = "KRAKEN_NEST_SPECIAL"
    # HasSpecial name = "SNOWFLAKE_NEST_SPECIAL"
    # HasSpecial name = "JUGGERNAUT_NEST_SPECIAL"
    # ]
    # ]
    # activation = Not OwnerHasTech name = "SHP_DOMESTIC_MONSTER"
    # effects =
    # GenerateSitRepMessage
    # message = "You own %planet%, with a monster nest, but haven't yet researched %tech%"
    # label = "Custom_2"
    # NoStringtableLookup
    # icon = "icons/monsters/kraken-1.png"
    # parameters = [
    # tag = "planet" data = Target.ID
    # tag = "tech" data = "SHP_DOMESTIC_MONSTER"
    # ]
    # empire = Source.Owner
    # A Call to Arms
    # A prime candidate for being snoozed, but probably good to be periodically reminded about
    # EffectsGroup
    # scope = And [
    # Planet
    # Species
    # Unowned
    # MaxDefense high = 0
    # ContainedBy And [
    # System
    # Not Contains Monster
    # ]
    # VisibleToEmpire empire = Source.Owner
    # ]
    # activation = Source
    # effects =
    # GenerateSitRepMessage
    # message = "There are defenseless natives at %planet%!  Go invade them with [[metertype METER_TROOPS]]!"
    # label = "Custom_4"
    # NoStringtableLookup
    # icon = "icons/meter/troops.png"
    # parameters = [
    # tag = "planet" data = Target.ID
    # ]
    # empire = Source.Owner
    # #####     RANDOM BEGINNER HINTS     ######
    EffectsGroup(
        scope=IsSource,
        activation=Turn(low=0, high=100),
        stackinggroup="HINTSSYSTEM",
        effects=GenerateSitRepMessage(
            message="RANDOM_BEGINNER_HINT",
            label="BEGINNER_HINTS",
            icon="icons/sitrep/beginner_hint.png",
            parameters={
                "rawtext": OneOf(
                    str,
                    UserString("BEGINNER_HINT_01"),
                    UserString("BEGINNER_HINT_02"),
                    UserString("BEGINNER_HINT_03"),
                    UserString("BEGINNER_HINT_04"),
                    UserString("BEGINNER_HINT_05"),
                    UserString("BEGINNER_HINT_06"),
                    UserString("BEGINNER_HINT_07"),
                    UserString("BEGINNER_HINT_08"),
                    UserString("BEGINNER_HINT_09"),
                    UserString("BEGINNER_HINT_10"),
                    UserString("BEGINNER_HINT_11"),
                    UserString("BEGINNER_HINT_12"),
                    UserString("BEGINNER_HINT_13"),
                    UserString("BEGINNER_HINT_14"),
                    UserString("BEGINNER_HINT_15"),
                    UserString("BEGINNER_HINT_16"),
                    UserString("BEGINNER_HINT_17"),
                    UserString("BEGINNER_HINT_18"),
                    UserString("BEGINNER_HINT_19"),
                    UserString("BEGINNER_HINT_20"),
                    UserString("BEGINNER_HINT_21"),
                    UserString("BEGINNER_HINT_22"),
                )
            },
            empire=Source.Owner,
        ),
    ),
    # Note, the "]" on the following line is functional and important; it must be present and all EffectsGroups must be above it.
]
