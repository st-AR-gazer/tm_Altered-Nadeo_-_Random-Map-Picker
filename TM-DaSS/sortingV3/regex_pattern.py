import json
import re
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from uids import (
    DISCOVERY_CAMPAIGNS,
    OFFICIAL_NADEO_AUTHOR_AND_SUBMITTOR_UIDS,
    special_uids,
    ALL_WEEKLY_SHORTS_MAP_NAMES,
    ALL_TOTD_MAP_NAMES,
    ALL_COMPETITION_MAP_NAMES
)
from assign_mix_attrs import (
    VALID_SEASONS,
    VALID_MAPNUMBER_COLORS,
    CHINESE_SEASON_MAP,
    VALID_SEASONS_SHORT,
    MAPNUMBER_COLOR_REGEX,
    SEASON_REGEX,
    SEASON_SHORT_REGEX,
    SEASON_CHINESE_REGEX
)

# TOTD pattern creation
escaped_totd_names = [re.escape(name) for name in ALL_TOTD_MAP_NAMES]
totd_pattern_group = "(?:" + "|".join(escaped_totd_names) + ")"
totd_full_pattern = re.compile(rf"^{totd_pattern_group}$", re.IGNORECASE)

# Discovery pattern creation
discovery_map_names = []
for campaign in DISCOVERY_CAMPAIGNS:
    discovery_map_names.extend(campaign['maps'].keys())
escaped_discovery_names = [re.escape(name) for name in discovery_map_names]
discovery_pattern_group = "(?:" + "|".join(escaped_discovery_names) + ")"
discovery_full_pattern = re.compile(rf"^{discovery_pattern_group}$", re.IGNORECASE)

# Weekly shorts pattern creation
weekly_shorts_map_names = []
for weekly_shorts in ALL_WEEKLY_SHORTS_MAP_NAMES:
    weekly_shorts_map_names.extend(weekly_shorts["maps"])
escaped_weekly_shorts_names = [re.escape(name) for name in weekly_shorts_map_names]
weeklyshorts_pattern_group = "(?:" + "|".join(escaped_weekly_shorts_names) + ")"
weekly_shorts_full_pattern = re.compile(rf"^{weeklyshorts_pattern_group}$", re.IGNORECASE)

# Competition pattern creation
competition_map_names = []
for competition in ALL_COMPETITION_MAP_NAMES:
    competition_map_names.extend(competition["maps"])

escaped_competition_names = [re.escape(name) for name in competition_map_names]
competition_pattern_group = "(?:" + "|".join(escaped_competition_names) + ")"



# ################ Altered Surface ################ #

    # --------- Dirt ---------- #
# Pattern seasonal: "Dirty <season> <year> - <mapnumber>"
dirt_seasonal_pattern_1 = re.compile(
    rf"^(?P<alteration_mix>Dirty)\s+(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)
# Pattern training: "Dirty Training - <mapnumber>"
dirt_training_pattern_1 = re.compile(
    rf"^(?P<alteration_mix>Dirty)\s+(?P<season>Training)\s*-\s*(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)
# Pattern totd: "<totdname> (Dirt)"
dirt_totd_pattern_1 = re.compile(
    rf"^(?P<name>{totd_pattern_group})\s+\((?P<alteration_mix>Dirt)\)$",
    re.IGNORECASE)
# Pattern weekly shorts: "<weeklyshortsname> (Dirt)"
dirt_weeklyshorts_pattern_1 = re.compile(
    rf"^(?P<name>{weeklyshorts_pattern_group})\s+\((?P<alteration_mix>Dirt)\)$",
    re.IGNORECASE)

    # --------- fast magnet ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> FastMagnet"
fastmagnet_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>FastMagnet)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> - FastMagnet"
fastmagnet_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+-\s*(?P<alteration_mix>FastMagnet)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> - Fast Magnet"
fastmagnet_seasonal_pattern_3 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+-\s*(?P<alteration_mix>Fast Magnet)$",
    re.IGNORECASE)
# Pattern training: "Training - <mapnumber> FastMagnet"
fastmagnet_training_pattern_1 = re.compile(
    rf"^(?P<season>Training)\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>FastMagnet)$",
    re.IGNORECASE)

    # --------- Flooded ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> Flooded"
flooded_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Flooded)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> - Flooded"
flooded_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+-\s+(?P<alteration_mix>Flooded)$",
    re.IGNORECASE)
# Pattern training: "Training - <mapnumber> - Flooded"
flooded_training_pattern_1 = re.compile(
    rf"^(?P<season>Training)\s*-\s*(?P<mapnumber>\d{{1,2}})\s+-\s+(?P<alteration_mix>Flooded)$",
    re.IGNORECASE)
# Pattern spring2020: "<spring2020><mapnumber> - Flooded"
flooded_spring2020_pattern_1 = re.compile(
    r"^(?P<spring2020>[STst][0-1]\d)\s+-\s+(?P<alteration_mix>Flooded)$",
    re.IGNORECASE)
# Pattern discovery: "<discoveryname> - Flooded"
flooded_discovery_pattern_1 = re.compile(
    rf"^(?P<discoveryname>{discovery_pattern_group})\s+-\s+(?P<alteration_mix>Flooded)$",
    re.IGNORECASE)

    # --------- Grass ---------- #
# Pattern seasonal: "Grassy <season> <year> - <mapnumber>"
grass_seasonal_pattern_1 = re.compile(
    rf"^(?P<alteration_mix>Grassy)\s+(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)
# Pattern Training: "Grassy Training - <mapnumber>"
grass_training_pattern_2 = re.compile(
    rf"^(?P<alteration_mix>Grassy)\s+(?P<season>Training)\s*-\s*(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)
# Pattern totd: "<totdname> (grass)"
grass_totd_pattern_1 = re.compile(
    rf"^(?P<name>{totd_pattern_group})\s+\((?P<alteration_mix>grass)\)$",
    re.IGNORECASE)

    # --------- Ice ---------- #
# Pattern seasonal: "Icy <season> <year> - <mapnumber>"
ice_seasonal_pattern_1 = re.compile(
    rf"^(?P<alteration_mix>Icy)\s+(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)
# Pattern seasonal: "<alteration_mix><season> <year> - <mapnumber>"
ice_seasonal_pattern_2 = re.compile(
    rf"^(?P<alteration_mix>Ice)\s*(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> Ice Edition - <mapnumber>"
ice_seasonal_pattern_3 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s+(?P<alteration_mix>Ice Edition)\s*-\s*(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)
# Pattern training: "Icy Training - <mapnumber>"
ice_training_pattern_1 = re.compile(
    rf"^(?P<alteration_mix>Icy)\s+(?P<season>Training)\s*-\s*(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)
# Pattern spring2020: "Icy <spring2020><mapnumber>"
ice_spring2020_pattern_1 = re.compile(
    r"^(?P<alteration_mix>Icy)\s+(?P<spring2020>[STst][0-1]\d)$",
    re.IGNORECASE)
# Pattern discovery: Icy "<discoveryname>"
ice_discovery_pattern_1 = re.compile(
    rf"^(?P<alteration_mix>Icy)\s+(?P<discoveryname>{discovery_pattern_group})$",
    re.IGNORECASE)
# Pattern totd: "Icy <totdname>"
ice_totd_pattern_1 = re.compile(
    rf"^(?P<alteration_mix>Icy)\s+(?P<name>{totd_pattern_group})$",
    re.IGNORECASE)
# Pattern weekly shorts: "Icy <weeklyshortsname>"
ice_weeklyshorts_pattern_1 = re.compile(
    rf"^(?P<alteration_mix>Icy)\s+(?P<name>{weeklyshorts_pattern_group})$",
    re.IGNORECASE)

    # --------- Magnet ---------- #
# Pattern season: "<season> <year> - <mapnumber> Magnet"
magnet_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Magnet)$",
    re.IGNORECASE)
# Pattern training: "Training - <mapnumber> Magnet"
magnet_training_pattern_2 = re.compile(
    rf"^(?P<season>Training)\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Magnet)$",
    re.IGNORECASE)
# Pattern spring2020: "<spring2020><mapnumber> Magnet"
magnet_spring2020_pattern_1 = re.compile(
    r"^(?P<spring2020>[STst][0-1]\d)\s+(?P<alteration_mix>Magnet)$",
    re.IGNORECASE)
# Pattern discovery: "<discoveryname> Magnet"
magnet_discovery_pattern_1 = re.compile(
    rf"^(?P<discoveryname>{discovery_pattern_group})\s+(?P<alteration_mix>Magnet)$",
    re.IGNORECASE)
# Pattern totd: "<totdname> (Magnet)"
magnet_totd_pattern_1 = re.compile(
    rf"^(?P<name>{totd_pattern_group})\s+\((?P<alteration_mix>Magnet)\)$",
    re.IGNORECASE)
# Pattern totd: "<totdname> Magnet"
magnet_totd_pattern_2 = re.compile(
    rf"^(?P<name>{totd_pattern_group})\s+(?P<alteration_mix>Magnet)$",
    re.IGNORECASE)
# Pattern weekly shorts: "<weeklyshortsname> Magnet"
magnet_weeklyshorts_pattern_1 = re.compile(
    rf"^(?P<name>{weeklyshorts_pattern_group})\s+(?P<alteration_mix>Magnet)$",
    re.IGNORECASE)

    # --------- Mixed ---------- #
# Pattern seasonal: "Mixed <season> <year> - <mapnumber>"
mixed_seasonal_pattern_1 = re.compile(
    rf"^(?P<alteration_mix>Mixed)\s+(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)
# Pattern training: "Mixed Training - <mapnumber>"
mixed_training_pattern_1 = re.compile(
    rf"^(?P<alteration_mix>Mixed)\s+(?P<season>Training)\s*-\s*(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)
# Pattern training: "Mixed Training - <mapnumber_1>-<mapnumber_2>"
mixed_training_pattern_2 = re.compile(
    rf"^(?P<alteration_mix>Mixed)\s+(?P<season>Training)\s*-\s*(?P<mapnumber_1>\d{{1,2}})-(?P<mapnumber_2>\d{{1,2}})$",
    re.IGNORECASE)
# Pattern weekly shorts: "<weeklyshortsname> (Mixed)"
mixed_weeklyshorts_pattern_1 = re.compile(
    rf"^(?P<name>{weeklyshorts_pattern_group})\s+\((?P<alteration_mix>Mixed)\)$",
    re.IGNORECASE)

    # --------- Penalty ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> Penalty"
penalty_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Penalty)$",
    re.IGNORECASE)
# Pattern training: "Training - <mapnumber> Penalty"
penalty_training_pattern_1 = re.compile(
    rf"^(?P<season>Training)\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Penalty)$",
    re.IGNORECASE)
# Pattern weekly shorts: "<weeklyshortsname> Penalty"
penalty_weeklyshorts_pattern_1 = re.compile(
    rf"^(?P<name>{weeklyshorts_pattern_group})\s+(?P<alteration_mix>Penalty)$",
    re.IGNORECASE)

    # --------- Plastic ---------- #
# Pattern seasonal: "Plastic <season> <year> - <mapnumber>"
plastic_seasonal_pattern_1 = re.compile(
    rf"^(?P<alteration_mix>Plastic)\s+(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)
# Pattern training: "Plastic Training - <mapnumber>"
plastic_training_pattern_1 = re.compile(
    rf"^(?P<alteration_mix>Plastic)\s+(?P<season>Training)\s*-\s*(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)
# Pattern training: "Plastic Training - <mapnumber_1> & <mapnumber_2>"
plastic_training_pattern_2 = re.compile(
    rf"^(?P<alteration_mix>Plastic)\s+(?P<season>Training)\s*-\s*(?P<mapnumber_1>\d{{1,2}})\s+&\s+(?P<mapnumber_2>\d{{1,2}})$",
    re.IGNORECASE)
# Pattern spring2020: "Plastic <spring2020><mapnumber>"
plastic_spring2020_pattern_1 = re.compile(
    r"^(?P<alteration_mix>Plastic)\s+(?P<spring2020>[STst][0-1]\d)$",
    re.IGNORECASE)
# Pattern discovery: "Plastic <discoveryname>"
plastic_discovery_pattern_1 = re.compile(
    rf"^(?P<alteration_mix>Plastic)\s+(?P<discoveryname>{discovery_pattern_group})$",
    re.IGNORECASE)
# Pattern discovery: "<discoveryname> Plastic"
plastic_discovery_pattern_2 = re.compile(
    rf"^(?P<discoveryname>{discovery_pattern_group})\s+(?P<alteration_mix>Plastic)$",
    re.IGNORECASE)
# Pattern weekly shorts: "<weeklyshortsname> (Plastic)"
plastic_weeklyshorts_pattern_1 = re.compile(
    rf"^(?P<name>{weeklyshorts_pattern_group})\s+\((?P<alteration_mix>Plastic)\)$",
    re.IGNORECASE)

    # --------- Road ---------- #
# Pattern seasonal: "Roady <season> <year> - <mapnumber>"
road_seasonal_pattern_1 = re.compile(
    rf"^(?P<alteration_mix>Roady)\s+(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> Road - <mapnumber>"
road_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s+(?P<alteration_mix>Road)\s*-\s*(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> Road"
road_seasonal_pattern_3 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Road)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> Asphalt"
roadasphalt_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Asphalt)$",
    re.IGNORECASE)
# Pattern seasonal: "(Tech) <season> <year> - <mapnumber>"
roadtech_seasonal_pattern_1 = re.compile(
    rf"^\(Tech\)\s+(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)
# Pattern training: "Roady Training - <mapnumber>"
road_training_pattern_1 = re.compile(
    rf"^(?P<alteration_mix>Roady)\s+(?P<season>Training)\s*-\s*(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)
# Pattern weekly shorts: "<weeklyshortsname> (Road)"
road_weeklyshorts_pattern_1 = re.compile(
    rf"^(?P<name>{weeklyshorts_pattern_group})\s+\((?P<alteration_mix>Road)\)$",
    re.IGNORECASE)

    # --------- Wood ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> Wood"
wood_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Wood)$",
    re.IGNORECASE)
# Pattern training: "Training - <mapnumber> Wood"
wood_training_pattern_1 = re.compile(
    rf"^(?P<season>Training)\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Wood)$",
    re.IGNORECASE)
# Pattern training: "Training - <mapnumber_1> & <mapnumber_2> Wood"
wood_training_pattern_2 = re.compile(
    rf"^(?P<season>Training)\s*-\s*(?P<mapnumber_21>\d{{1,2}})\s+&\s+(?P<mapnumber_24>\d{{1,2}})\s+(?P<alteration_mix>Wood)$",
    re.IGNORECASE)
# Pattern spring2020: "Wood <spring2020><mapnumber>"
wood_spring2020_pattern_1 = re.compile(
    r"^(?P<alteration_mix>Wood)\s+(?P<spring2020>[STst][0-1]\d)$",
    re.IGNORECASE)
# Pattern discovery: "<discoveryname> Wood"
wood_discovery_pattern_1 = re.compile(
    rf"^(?P<discoveryname>{discovery_pattern_group})\s+(?P<alteration_mix>Wood)$",
    re.IGNORECASE)
# Pattern weekly shorts: "<weeklyshortsname> (Wood)"
wood_weeklyshorts_pattern_1 = re.compile(
    rf"^(?P<name>{weeklyshorts_pattern_group})\s+\((?P<alteration_mix>Wood)\)$",
    re.IGNORECASE)
# Pattern totd: "<totdname> (Wood)"
wood_totd_pattern_1 = re.compile(
    rf"^(?P<name>{totd_pattern_group})\s+\((?P<alteration_mix>Wood)\)$",
    re.IGNORECASE)

####################################################################################################################################################

    # --------- Bobsleigh ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> (bobsleigh)"
bobsleigh_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>bobsleigh)\)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> Bobsleigh"
bobsleigh_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Bobsleigh)$",
    re.IGNORECASE)
# Pattern seasonal: "Bobsleigh <season> <year> - <mapnumber>"
bobsleigh_seasonal_pattern_3 = re.compile(
    rf"^(?P<alteration_mix>Bobsleigh)\s+(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)
# Pattern training: "Training - <mapnumber> Bobsleigh"
bobsleigh_training_pattern_1 = re.compile(
    rf"^(?P<season>Training)\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Bobsleigh)$",
    re.IGNORECASE)

    # --------- Pipe ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> (Pipe)"
pipe_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>Pipe)\)$",
    re.IGNORECASE)

    # --------- Sausage ---------- #
# Pattern seasonal: "Saussage <season> <year> - <mapnumber>"
sausage_seasonal_pattern_1 = re.compile(
    rf"^(?P<alteration_mix>Sausage)\s+(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)
# Pattern training: "Training - <mapnumber> Sausage"
sausage_training_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Sausage)$",
    re.IGNORECASE)

    # --------- Slot Track ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> Slot Track"
slottrack_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Slot Track)$",
    re.IGNORECASE)

    # --------- Surfaceless ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> Surfaceless"
surfaceless_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Surfaceless)$",
    re.IGNORECASE)
# Pattern training: "Training - <mapnumber> Surfaceless"
surfaceless_training_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Surfaceless)$",
    re.IGNORECASE)
# Pattern training - 16 17 18 19: "<season> - <mapnumber_16> <mapnumber_17> <mapnumber_18> <mapnumber_19> Surfaceless"
surfaceless_training_pattern_16171819 = re.compile(
    rf"^(?P<season>Training)\s*-\s*(?P<mapnumber_16>\d{{1,2}})\s+(?P<mapnumber_17>\d{{1,2}})\s+(?P<mapnumber_18>\d{{1,2}})\s+(?P<mapnumber_19>\d{{1,2}})\s+(?P<alteration_mix>Surfaceless)$",
    re.IGNORECASE)
# Pattern weekly shorts: "<weeklyshortsname> (Surfaceless)"
surfaceless_weeklyshorts_pattern_1 = re.compile(
    rf"^(?P<name>{weeklyshorts_pattern_group})\s+\((?P<alteration_mix>Surfaceless)\)$",
    re.IGNORECASE)

    # --------- Underwater ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> (Underwater)"
underwater_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>Underwater)\)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> (UW)"
underwater_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>UW)\)$",
    re.IGNORECASE)
# Pattern training: "Training - <mapnumber> Underwater"
underwater_training_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Underwater)$",
    re.IGNORECASE)
# Pattern spring2020: "<spring2020><mapnumber> (Underwater)"
underwater_spring2020_pattern_1 = re.compile(
    r"^(?P<spring2020>[STst][0-1]\d)\s+(?P<alteration_mix>Underwater)$",
    re.IGNORECASE)
# Pattern discovery: "<discoveryname> (Underwater)"
underwater_discovery_pattern_1 = re.compile(
    rf"^(?P<discoveryname>{discovery_pattern_group})\s+\((?P<alteration_mix>Underwater)\)$",
    re.IGNORECASE)
# Pattern discovery: "<discoveryname> Underwater"
underwater_discovery_pattern_2 = re.compile(
    rf"^(?P<discoveryname>{discovery_pattern_group})\s+(?P<alteration_mix>Underwater)$",
    re.IGNORECASE)
# Pattern discovery: "<discoveryname> - Underwater"
underwater_discovery_pattern_3 = re.compile(
    rf"^(?P<discoveryname>{discovery_pattern_group})\s+-\s+(?P<alteration_mix>Underwater)$",
    re.IGNORECASE)
# Pattern discovery: "<discoveryname> (UW)"
underwater_discovery_pattern_4 = re.compile(
    rf"^(?P<discoveryname>{discovery_pattern_group})\s+\((?P<alteration_mix>UW)\)$",
    re.IGNORECASE)
# Pattern totd: "<totdname> (Underwater)"
underwater_totd_pattern_1 = re.compile(
    rf"^(?P<name>{totd_pattern_group})\s+\((?P<alteration_mix>Underwater)\)$",
    re.IGNORECASE)
# Pattern weekly shorts: "<weeklyshortsname> Underwater"
underwater_weeklyshorts_pattern_1 = re.compile(
    rf"^(?P<name>{weeklyshorts_pattern_group})\s+(?P<alteration_mix>Underwater)$",
    re.IGNORECASE)
# Pattern weekly shorts: "<weeklyshortsname> - Underwater"
underwater_weeklyshorts_pattern_2 = re.compile(
    rf"^(?P<name>{weeklyshorts_pattern_group})\s+-\s+(?P<alteration_mix>Underwater)$",
    re.IGNORECASE)


# ################ Altered Effects ################ #

    # -------- Antibooster ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> AntiBoosters"
antibooster_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>AntiBoosters)$",
    re.IGNORECASE)

    # -------- Boosterless ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> (Boosterless)"
boosterless_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>Boosterless)\)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> Boosterless - <mapnumber>"
boosterless_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s+(?P<alteration_mix>Boosterless)\s*-\s*(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)
# Pattern training: "Training - <mapnumber> Boosterless"
boosterless_training_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Boosterless)$",
    re.IGNORECASE)
# Pattern spring2020: "<spring2020><mapnumber> Boosterless"
boosterless_spring2020_pattern_1 = re.compile(
    r"^(?P<spring2020>[STst][0-1]\d)\s+(?P<alteration_mix>Boosterless)$",
    re.IGNORECASE)

    # -------- Broken ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> Broken"
broken_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Broken)$",
    re.IGNORECASE)

    # -------- Cleaned ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> Cleaned"
cleaned_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Cleaned)$",
    re.IGNORECASE)

    # -------- Cruise Control ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> Cruise Control"
cruisecontrol_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Cruise Control)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> - Cruise Control"
cruisecontrol_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+-\s+(?P<alteration_mix>Cruise Control)$",
    re.IGNORECASE)
# Pattern weekly shorts: "<weeklyshortsname> Cruise Control"
cruisecontrol_weeklyshorts_pattern_1 = re.compile(
    rf"^(?P<name>{weeklyshorts_pattern_group})\s+(?P<alteration_mix>Cruise Control)$",
    re.IGNORECASE)

    # -------- Cruise Effects ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> Cruise Effects"
cruiseeffects_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Cruise Effects)$",
    re.IGNORECASE)
# Pattern sesaonal: "Training - <mapnumber> Cruise Effects"
cruiseeffects_training_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Cruise Effects)$",
    re.IGNORECASE
)

    # -------- Fast ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> (Fast)"
fast_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>Fast)\)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> Fast"
fast_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Fast)$",
    re.IGNORECASE)

    # -------- Fragile ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> (Fragile)"
fragile_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>Fragile)\)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> Fragile"
fragile_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Fragile)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> but it's Fragile"
fragile_seasonal_pattern_3 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+but\s+it's\s+(?P<alteration_mix>Fragile)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> but its Fragile"
fragile_seasonal_pattern_4 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+but\s+its\s+(?P<alteration_mix>Fragile)$",
    re.IGNORECASE)
# Pattern training: "Training - <mapnumber> Fragile"
fragile_training_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Fragile)$",
    re.IGNORECASE)

    # -------- Full Fragile ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> (Full Fragile)"
fullfragile_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>Full Fragile)\)$",
    re.IGNORECASE)

    # -------- FreeWheel ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> FreeWheel"
freewheel_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>FreeWheel)$",
    re.IGNORECASE)
# Pattern training: "Training - <mapnumber> FreeWheel"
freewheel_training_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>FreeWheel)$",
    re.IGNORECASE)
# Pattern spring2020: "Spring 2020 - <spring2020><mapnumber> FreeWheel"
freewheel_spring2020_pattern_1 = re.compile(
    r"^Spring 2020 - (?P<spring2020>[STst][0-1]\d)\s+(?P<alteration_mix>FreeWheel)$",
    re.IGNORECASE)
    

    # -------- Glider ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> - Glider"
glider_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+-\s+(?P<alteration_mix>Glider)$",
    re.IGNORECASE)

    # -------- No Brakes ---------- #
# Pattern seasonal: "No Brakes - <season> <year> - <mapnumber>"
nobrakes_seasonal_pattern_1 = re.compile(
    rf"^(?P<alteration_mix>No Brakes)\s*-\s*(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> NoBrakes"
nobrakes_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>NoBrakes)$",
    re.IGNORECASE)

    # -------- No Effects ---------- #
# Pattern seasonal: "<season> <year> Effectless - <mapnumber>"
noeffects_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s+(?P<alteration_mix>Effectless)\s*-\s*(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)

    # -------- No Grip ---------- #
# Pattern seasonal: "<season> <year> No Grip - <mapnumber>"
nogrip_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s+(?P<alteration_mix>No Grip)\s*-\s*(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> - No Grip"
nogrip_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+-\s+(?P<alteration_mix>No Grip)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> No-Grip"
nogrip_seasonal_pattern_3 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>No-Grip).*$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> NoGrip - <mapnumber>"
nogrip_seasonal_pattern_4 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s+(?P<alteration_mix>NoGrip)\s*-\s*(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)

    # -------- No Steering ---------- #
# Pattern seasonal: "<season> <year> No Steering - <mapnumber>"
nosteering_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s+(?P<alteration_mix>No Steering)\s*-\s*(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)
# Pattern training: "Training - <mapnumber> No Steering"
nosteering_training_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>No Steering)$",
    re.IGNORECASE)
# Pattern weekly shorts: "<weeklyshortsname> (No-Steer)"
nosteering_weeklyshorts_pattern_1 = re.compile(
    rf"^(?P<name>{weeklyshorts_pattern_group})\s+\((?P<alteration_mix>No-Steer)\)$",
    re.IGNORECASE)

    # -------- Random Dankness ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> - Random Dankness"
randomdankness_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+-\s+(?P<alteration_mix>Random Dankness)$",
    re.IGNORECASE)
# Pattern training: "Training - <mapnumber> Random Dankness"
randomdankness_training_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Random Dankness)$",
    re.IGNORECASE)

    # -------- Random Effects ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> - Random Effects"
randomeffects_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+-\s+(?P<alteration_mix>Random Effects)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> - Random Effects <additionalinfo>"
randomeffects_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+-\s+(?P<alteration_mix>Random Effects)\s+(?P<additionalinfo>.+)$",
    re.IGNORECASE)

    # -------- Reactor ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> Reactor"
reactor_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Reactor)$",
    re.IGNORECASE)
# Pattern training: "Training - <mapnumber> Reactor"
reactor_training_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Reactor)$",
    re.IGNORECASE)
# Pattern training: "Training Reactor - <mapnumber>"
reactor_training_pattern_2 = re.compile(
    rf"^(?P<season>Training)\s+(?P<alteration_mix>Reactor)\s*-\s*(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)

    # -------- Reactor Down ---------- #
# Pattern1: "<season> <year> - <mapnumber> (Reactor Down)"
reactordown_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>Reactor Down)\)$",
    re.IGNORECASE)
# Pattern2: "<season> <year> - <mapnumber> Reactordown"
reactordown_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Reactordown)$",
    re.IGNORECASE)

    # -------- Red Effects ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> Red Effects"
redeffects_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Red Effects)$",
    re.IGNORECASE)
# Pattern training: "Training - <mapnumber> Red Effects"
redeffects_training_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Red Effects)$",
    re.IGNORECASE)

    # -------- RNG Boosters ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> RNG Booster"
rngboosters_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>RNG Booster)$",
    re.IGNORECASE)
# Pattern spring2020: "<spring2020season><mapnumber> RNG Booster"
rngboosters_spring2020_pattern_1 = re.compile(
    r"^(?P<spring2020>[STst][0-1]\d)\s+(?P<alteration_mix>RNG Booster)$",
    re.IGNORECASE)

    # -------- Slowmo ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> slowmo"
slowmo_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>slowmo)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> <mapnumber> slowmo"
slowmo_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s+(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>slowmo)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> slow mo"
slowmo_seasonal_pattern_3 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>slow mo)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> (slowmo)"
slowmo_seasonal_pattern_4 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>slowmo)\)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> - Slowmotion"
slowmo_seasonal_pattern_5 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+-\s+(?P<alteration_mix>Slowmotion)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> - Slowmo"
slowmo_seasonal_pattern_6 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+-\s*(?P<alteration_mix>Slowmo)$",
    re.IGNORECASE)

    # -------- Wet Wheels ---------- #
# Pattern1: "<season> <year> - <mapnumber> (Wet-Wheels)"
wetwheels_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>Wet-Wheels)\)$",
    re.IGNORECASE)

    # -------- Worn Tires ---------- #
# Pattern1: "<season> <year> - <mapnumber> (Worn Tires)"
worntires_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>Worn Tires)\)$",
    re.IGNORECASE)


# ################ Altered Finish Location ################ #

    # -------- 1 Back / 1 Forwards ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> (1-back)"
oneback_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s*\((?P<alteration_mix>1-back)\)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> - one back"
oneback_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+-\s+(?P<alteration_mix>one back)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> - 1-back"
oneback_seasonal_pattern_3 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+-\s+(?P<alteration_mix>1-back)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> (1Back)"
oneback_seasonal_pattern_4 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>1Back)\)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> 1-back"
oneback_seasonal_pattern_5 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>1-back)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> 1-forward - <mapnumber>"
oneforward_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s+(?P<alteration_mix>1-forward)\s*-\s*(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)
# Pattern training: "Training 1-forward - <mapnumber>"
oneforward_training_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s*(?P<alteration_mix>1-forward)\s*-\s*(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)
# Pattern training: "Training - <mapnumber> 1-back"
oneback_training_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>1-back)$",
    re.IGNORECASE)
# Pattern spring2020: "<spring2020><mapnumber> 1-forward"
oneforward_spring2020_pattern_1 = re.compile(
    r"^(?P<spring2020>[STst][0-1]\d)\s+(?P<alteration_mix>1-forward)$",
    re.IGNORECASE)
# Pattern totd: "<totdname> (1-Forward)"
oneforward_totd_pattern_1 = re.compile(
    rf"^(?P<name>{totd_pattern_group})\s+\((?P<alteration_mix>1-Forward)\)$",
    re.IGNORECASE)
# Pattern totd: "<totdname> (1-For)"
oneforward_totd_pattern_2 = re.compile(
    rf"^(?P<name>{totd_pattern_group})\s+\((?P<alteration_mix>1-For)\)$",
    re.IGNORECASE)

    # -------- 1 Down ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> (1-DOWN)"
onedown_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>1-DOWN)\)$",
    re.IGNORECASE)
# Pattern training: "Training - <mapnumber> (1-DOWN)"
onedown_training_pattern_1 = re.compile(
    rf"^(?P<season>Training)\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>1-DOWN)\)$",
    re.IGNORECASE)
# Pattern spring2020: "<spring2020><mapnumber> (1-DOWN)"
onedown_spring2020_pattern_1 = re.compile(
    r"^(?P<spring2020>[STst][0-1]\d)\s+\((?P<alteration_mix>1-DOWN)\)$",
    re.IGNORECASE)
# Pattern discovery: "<discoveryname> (1-DOWN)"
onedown_discovery_pattern_1 = re.compile(
    rf"^(?P<discoveryname>{discovery_pattern_group})\s+\((?P<alteration_mix>1-DOWN)\)$",
    re.IGNORECASE)
# Pattern totd: "<totdname> (1-Down)"
onedown_totd_pattern_1 = re.compile(
    rf"^(?P<name>{totd_pattern_group})\s+\((?P<alteration_mix>1-DOWN)\)$",
    re.IGNORECASE)
# Pattern weekly shorts: "<weeklyshortsname> (1-DOWN)"
onedown_weeklyshorts_pattern_1 = re.compile(
    rf"^(?P<name>{weeklyshorts_pattern_group})\s+\((?P<alteration_mix>1-DOWN)\)$",
    re.IGNORECASE)

    # -------- 1 Left / 1 Right ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> 1 Left"
oneleft_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>1 Left)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> 1-Left"
oneleft_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>1-Left)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> 1 Right"
oneright_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>1 Right)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> 1-Right"
oneright_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>1-Right)$",
    re.IGNORECASE)

    # -------- 1 Up ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> (1-UP)"
oneup_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>1-UP)\)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> (1UP)"
oneup_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>1UP)\)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> 1UP - <mapnumber>"
oneup_seasonal_pattern_3 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s+(?P<alteration_mix>1UP)\s*-\s*(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> 1-UP"
oneup_seasonal_pattern_4 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>1-UP)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> - 1-UP"
oneup_seasonal_pattern_5 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+-\s+(?P<alteration_mix>1-UP)$",
    re.IGNORECASE)
# Pattern training: "Training - <mapnumber> - 1UP"
oneup_training_pattern_1 = re.compile(
    rf"^(?P<season>Training)\s*-\s*(?P<mapnumber>\d{{1,2}})\s+-\s+(?P<alteration_mix>1UP)$",
    re.IGNORECASE)
# Pattern training: "Training - <mapnumber> (1-UP)"
oneup_training_pattern_2 = re.compile(
    rf"^(?P<season>Training)\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>1-UP)\)$",
    re.IGNORECASE)
# Pattern spring2020: "<spring2020><mapnumber> (1-UP)"
oneup_spring2020_pattern_1 = re.compile(
    r"^(?P<spring2020>[STst][0-1]\d)\s+\((?P<alteration_mix>1-UP)\)$",
    re.IGNORECASE)
# Pattern discovery: "<discoveryname> (1-UP)"
oneup_discovery_pattern_1 = re.compile(
    rf"^(?P<discoveryname>{discovery_pattern_group})\s+\((?P<alteration_mix>1-UP)\)$",
    re.IGNORECASE)
# Pattern totd: "<totdname> (1-up)"
oneup_totd_pattern_1 = re.compile(
    rf"^(?P<name>{totd_pattern_group})\s+\((?P<alteration_mix>1-up)\)$",
    re.IGNORECASE)

    # -------- 2 Up ---------- #
# Pattern1: "<season> <year> - <mapnumber> (2-UP)"
twoup_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>2-UP)\)$",
    re.IGNORECASE)

    # -------- Better Reverse ---------- #
# Pattern1: "<season> <year> - <mapnumber> (BeVerse)"
betterreverse_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>BeVerse)\)$",
    re.IGNORECASE)
# Pattern2: "<season> <year> - <mapnumber> - Better Reverse"
betterreverse_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+-\s+(?P<alteration_mix>Better Reverse)$",
    re.IGNORECASE)
# Pattern3: "<season> <year> - <mapnumber> - Reverse Magna"
betterreverse_seasonal_pattern_3 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+-\s+(?P<alteration_mix>Reverse Magna)$",
    re.IGNORECASE)

    # -------- CP1 is End ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> CP1 Ends"
cp1isend_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>CP1 Ends)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> CP1 is End"
cp1isend_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>CP1 is End)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> CP is End"
cp1isend_seasonal_pattern_3 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>CP is End)$",
    re.IGNORECASE)
# Pattern training: "Training - <mapnumber> CP1 is End"
cp1isend_training_pattern_1 = re.compile(
    rf"^(?P<season>Training)\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>CP1 is End)$",
    re.IGNORECASE)
# Pattern trainin: "Training - <mapnumber> CP1 End"
cp1isend_training_pattern_2 = re.compile(
    rf"^(?P<season>Training)\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>CP1 End)$",
    re.IGNORECASE)
# Pattern spring2020: "<spring2020><mapnumber> CP1 is End"
cp1isend_spring2020_pattern_1 = re.compile(
    r"^(?P<spring2020>[STst][0-1]\d)\s+(?P<alteration_mix>CP1 is End)$",
    re.IGNORECASE)
# Pattern totd: "<totdname> (CP1-End)"
cp1isend_totd_pattern_1 = re.compile(
    rf"^(?P<name>{totd_pattern_group})\s+\((?P<alteration_mix>CP1-End)\)$",
    re.IGNORECASE)
# Pattern totd: "<totdname> (CP1)"
cp1isend_totd_pattern_2 = re.compile(
    rf"^(?P<name>{totd_pattern_group})\s+\((?P<alteration_mix>CP1)\)$",
    re.IGNORECASE)

    # -------- Floor Fin ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> Floor-fin"
floorfin_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Floor-fin)$",
    re.IGNORECASE)
# Pattern weekly shorts: "<mapname> Floor-Fin"
floorfin_weeklyshorts_pattern_1 = re.compile(
    rf"^(?P<mapname>{weeklyshorts_pattern_group})\s+(?P<alteration_mix>Floor-Fin)$",
    re.IGNORECASE)

    # -------- Ground Clippers ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> (Ground Clippers)"
groundclippers_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>Ground Clippers)\)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> (Ground Clippers <alteration_mixinfo>)"
groundclippers_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>Ground Clippers)\s+(?P<alteration_mixinfo>.+)\)$",
    re.IGNORECASE)

    # -------- Inclined ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> Inclined"
inclined_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Inclined)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> (Inclined)"
inclined_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s*\((?P<alteration_mix>Inclined)\)$",
    re.IGNORECASE)

    # -------- Manslaughter ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> Manslaughter"
manslaughter_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Manslaughter)$",
    re.IGNORECASE)

    # -------- No Gear 5 ---------- #
# Pattern1: "<season> <year> - <mapnumber> No Gear 5"
nogear5_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>No Gear 5)$",
    re.IGNORECASE)

    # -------- Podium ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> - Podium"
podium_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+-\s+(?P<alteration_mix>Podium)$",
    re.IGNORECASE)
# Pattern competition: "<competitionname> - Podium"
podium_competition_pattern_1 = re.compile(
    rf"^(?P<competitionname>{competition_pattern_group})\s+-\s+(?P<alteration_mix>Podium)$",
    re.IGNORECASE)

    # -------- Puzzle ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> (Puzzle)"
puzzle_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>Puzzle)\)$",
    re.IGNORECASE)
# Pattern training: "Training Puzzle - <mapnumber>"
puzzle_training_pattern_1 = re.compile(
    rf"^(?P<season>Training)\s+(?P<alteration_mix>Puzzle)\s*-\s*(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)
# Pattern totd: "<totwname> (Puzzle)"
puzzle_totd_pattern_1 = re.compile(
    rf"^{totd_pattern_group}\s+\((?P<alteration_mix>Puzzle)\)$",
    re.IGNORECASE)

    # -------- Reverse ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> - Reverse"
reverse_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+-\s+(?P<alteration_mix>Reverse)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> Reverse"
reverse_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Reverse)$",
    re.IGNORECASE)
# Pattern training: "Training - <mapnumber> - Reverse"
reverse_training_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+-\s+(?P<alteration_mix>Reverse)$",
    re.IGNORECASE)
# Pattern spring2020: "<spring2020><mapnumber> - Reverse"
reverse_spring2020_pattern_1 = re.compile(
    r"^(?P<spring2020>[STst][0-1]\d)\s+-\s+(?P<alteration_mix>Reverse)$",
    re.IGNORECASE)
# Pattern spring2020: "<spring2020><mapnumber> Reverse"
reverse_spring2020_pattern_2 = re.compile(
    r"^(?P<spring2020>[STst][0-1]\d)\s+(?P<alteration_mix>Reverse)$",
    re.IGNORECASE)
# Pattern discovery: "<discoveryname> - Reverse"
reverse_discovery_pattern_1 = re.compile(
    rf"^{discovery_pattern_group}\s+-\s+(?P<alteration_mix>Reverse)$",
    re.IGNORECASE)
# Pattern totd: "<totdname> (Reverse)"
reverse_totd_pattern_1 = re.compile(
    rf"^{totd_pattern_group}\s+\((?P<alteration_mix>Reverse)\)$",
    re.IGNORECASE)
# Pattern totd: "<totdname> - Reverse"
reverse_totd_pattern_2 = re.compile(
    rf"^{totd_pattern_group}\s+-\s+(?P<alteration_mix>Reverse)$",
    re.IGNORECASE)
# Pattern weekly shorts: "<mapname> - Reverse"
reverse_weeklyshorts_pattern_1 = re.compile(
    rf"^{weeklyshorts_pattern_group}\s+-\s+(?P<alteration_mix>Reverse)$",
    re.IGNORECASE)

    # -------- Roofing ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> (Roofing)"
roofing_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>Roofing)\)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> - Roofing"
roofing_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+-\s+(?P<alteration_mix>Roofing)$",
    re.IGNORECASE)

    # --------- SHORT ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> | Short"
short_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s*\|\s*(?P<alteration_mix>Short)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> Short"
short_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Short)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> shorts"
short_seasonal_pattern_3 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>shorts)$",
    re.IGNORECASE)
short_seasonal_pattern_4 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s+(?P<alteration_mix>Short)\s*-\s*(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)
# Pattern training: "Training - <mapnumber> Short"
short_training_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Short)$",
    re.IGNORECASE)
# Pattern spring2020: "<spring2020><mapnumber> Short"
short_spring2020_pattern_1 = re.compile(
    r"^(?P<spring2020>[STst][0-1]\d)\s+(?P<alteration_mix>Short)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> Short - <mapnumber>"


    # --------- Sky is the Finish ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> Sky Finish"
skyfinish_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Sky Finish)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> (SITF)"
skyfinish_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>SITF)\)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> - Sky is the Finish"
skyfinish_seasonal_pattern_3 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+-\s+(?P<alteration_mix>Sky is the Finish)$",
    re.IGNORECASE)
# Pattern spring2020: "<spring2020><mapnumber> - Sky Finish"
skyfinish_spring2020_pattern_1 = re.compile(
    r"^(?P<spring2020>[STst][0-1]\d)\s+-\s+(?P<alteration_mix>Sky Finish)$",
    re.IGNORECASE)
# Pattern totd: "<totdname> (SITF)"
skyfinish_totd_pattern_1 = re.compile(
    rf"^{totd_pattern_group}\s+\((?P<alteration_mix>SITF)\)$",
    re.IGNORECASE)

    # --------- There&Back/Boomerang ---------- #
# Pattern seasonal: "<season> <year> - There&Back <mapnumber>"
thereandback_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<alteration_mix>There&Back)\s+(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> Boomerang"
thereandback_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Boomerang)$",
    re.IGNORECASE)
# Pattern training: "Training There and Back - <mapnumber>"
thereandback_training_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<alteration_mix>There and Back)\s*-\s*(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)

    # --------- YEP Tree Puzzle ---------- #
# Pattern1: "<season> <year> - <mapnumber> YEP TREE PUZZLE"
yeptreepuzzle_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>YEP TREE PUZZLE)$",
    re.IGNORECASE)


# ################ Altered Enviroments ################ #

    # -------- [Stadium] ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> [Stadium]"
stadium_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>\[Stadium\])$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> - CarSport"
stadium_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+-\s+(?P<alteration_mix>CarSport)$",
    re.IGNORECASE)
# Pattern discovery: "<discoveryname> - CarSport"
stadium_discovery_pattern_1 = re.compile(
    rf"^(?P<dicoveryname>{discovery_pattern_group})\s*-\s*(?P<alteration_mix>CarSport)$",
    re.IGNORECASE)
# Pattern discovery: "<discoveryname> [Stadium]"
stadium_discovery_pattern_2 = re.compile(
    rf"^(?P<dicoveryname>{discovery_pattern_group})\s+\[Stadium\]$",
    re.IGNORECASE)
# Pattern totd: "<totdname> (CarSport)"
stadium_totd_pattern_1 = re.compile(
    rf"^{totd_pattern_group}\s+\((?P<alteration_mix>CarSport)\)$",
    re.IGNORECASE)
# Pattern weekly shorts: "<mapname> - CarSport"
stadium_weeklyshorts_pattern_1 = re.compile(
    rf"^(?P<mapname>{weeklyshorts_pattern_group})\s+-\s+(?P<alteration_mix>CarSport)$",
    re.IGNORECASE)

    # -------- [Stadium] To The Top ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> Stadium To The Top"
stadiumtothetop_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Stadium To The Top)$",
    re.IGNORECASE)
# Pattern weekly shorts: "<mapname> Stadium To The Top"
stadiumtothetop_weeklyshorts_pattern_1 = re.compile(
    rf"^(?P<mapname>{weeklyshorts_pattern_group})\s+(?P<alteration_mix>Stadium To The Top)$",
    re.IGNORECASE)

    # -------- [Stadium] Underwater ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> [Stadium] (UW)"
stadiumunderwater_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\[Stadium\]\s+\((?P<alteration_mix>UW)\)$",
    re.IGNORECASE)

    # -------- [Stadium] Wet Plastic ---------- #
# Pattern seasonal: "Wet Plastic <season> <year> - <mapnumber> (Stadium)"
stadiumwetplastic_seasonal_pattern_1 = re.compile(
    rf"^(?P<alteration_mix_1>Wet Plastic)\s+(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix_2>Stadium)\)$",
    re.IGNORECASE)

    # -------- [Stadium] Wet Wood ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> (Wet Wood Stadium Car)"
stadiumwetwood_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>Wet Wood Stadium Car)\)$",
    re.IGNORECASE)

    # -------- [Snow] ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> [Snow]"
snow_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>\[Snow\])$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> - CarSnow"
snow_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+-\s+(?P<alteration_mix>CarSnow)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> - Snowcar"
snow_seasonal_pattern_3 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+-\s*(?P<alteration_mix>Snowcar)$",
    re.IGNORECASE)
# Pattern training: "Training <mapnumber> - CarSnow"
snow_training_pattern_1 = re.compile(
    rf"^(?P<special_map_name>.*?)\s*-\s*(?P<alteration_mix>CarSnow)$",
    re.IGNORECASE)
# Pattern discovery: "<discoveryname> [Snow]"
snow_discovery_pattern_1 = re.compile(
    rf"^{discovery_pattern_group}\s+\[Snow\]$",
    re.IGNORECASE)
# Pattern totd: "<totdname> (SnowCar)"
snow_totd_pattern_1 = re.compile(
    rf"^{totd_pattern_group}\s+\((?P<alteration_mix>SnowCar)\)$",
    re.IGNORECASE)
# Pattern totd: "<totdname> (Snow)"
snow_totd_pattern_2 = re.compile(
    rf"^{totd_pattern_group}\s+\((?P<alteration_mix>Snow)\)$",
    re.IGNORECASE)
# Pattern weekly shorts: "[Snow] <mapname>"
snow_weeklyshorts_pattern_1 = re.compile(
    rf"^\[(?P<alteration_mix>Snow)\]\s+(?P<mapname>{weeklyshorts_pattern_group})$",
    re.IGNORECASE)

    # -------- [Snow] Carswitch ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> Snowcarswitch"
snowcarswitch_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Snowcarswitch)$",
    re.IGNORECASE)
# Pattern totd: "<totdname> (CS-SC)"
snowcarswitch_totd_pattern_1 = re.compile(
    rf"^{totd_pattern_group}\s+\((?P<alteration_mix>CS-SC)\)$",
    re.IGNORECASE)
# Pattern totd: "<totdname> (Carswitch SnowCar)"
snowcarswitch_totd_pattern_2 = re.compile(
    rf"^{totd_pattern_group}\s+\((?P<alteration_mix>Carswitch SnowCar)\)$",
    re.IGNORECASE)
# Pattern totd: "<totdname> (CS-SnowCar)"
snowcarswitch_totd_pattern_3 = re.compile(
    rf"^{totd_pattern_group}\s+\((?P<alteration_mix>CS-SnowCar)\)$",
    re.IGNORECASE)
# Pattern totd: "<totdname> (CS_SC)"
snowcarswitch_totd_pattern_4 = re.compile(
    rf"^{totd_pattern_group}\s+\((?P<alteration_mix>CS_SC)\)$",
    re.IGNORECASE)
# Pattern totd: "<totdname> (Car Switch)"
snowcarswitch_totd_pattern_5 = re.compile(
    rf"^{totd_pattern_group}\s+\((?P<alteration_mix>Car Switch)\)$",
    re.IGNORECASE)

    # -------- [Snow] Checkpointless ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> Checkpointless snow"
snowcheckpointless_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Checkpointless snow)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> - Checkpointless snow"
snowcheckpointless_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+-\s+(?P<alteration_mix>Checkpointless snow)$",
    re.IGNORECASE)

    # -------- [Snow] Ice ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> (Icy [Snow])"
snowice_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>Icy \[Snow\])\)$",
    re.IGNORECASE)

    # -------- [Snow] Puzzle ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> Snow Puzzle"
snowpuzzle_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Snow Puzzle)$",
    re.IGNORECASE)

    # -------- [Snow] To The Top ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> Snow To The Top"
snowtothetop_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Snow To The Top)$",
    re.IGNORECASE)
# Pattern weekly shorts: "<mapname> Snow To The Top"
snowtothetop_weeklyshorts_pattern_1 = re.compile(
    rf"^(?P<mapname>{weeklyshorts_pattern_group})\s+(?P<alteration_mix>Snow To The Top)$",
    re.IGNORECASE)

    # -------- [Snow] Underwater ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> [Snow] (UW)"
snowunderwater_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>\[Snow\]\s+\(UW\))$",
    re.IGNORECASE)
# Pattern seasonal: "<seasonal> <year> - <mapnumber> (SnowCar UW)"
snowunderwater_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>SnowCar UW)\)$",
    re.IGNORECASE)
# Pattern seasonal: "<seasonal> <year> - <mapnumber> (Snow Car UW)"
snowunderwater_seasonal_pattern_3 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>Snow Car UW)\)$",
    re.IGNORECASE)
# Pattern training: "Training - <mapnumber> [Snow] (UW)"
snowunderwater_training_pattern_1 = re.compile(
    rf"^(?P<season>Training)\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>\[Snow\]\s+\(UW\))$",
    re.IGNORECASE)
# Pattern discovery: "<discoveryname> [Snow] (UW)"
snowunderwater_discovery_pattern_1 = re.compile(
    rf"^{discovery_pattern_group}\s+\[(?P<alteration_mix_1>Snow)\]\s+\((?P<alteration_mix_2>UW)\)$",
    re.IGNORECASE)
# Pattern discovery: "<discoveryname> [Snow] UW"
snowunderwater_discovery_pattern_2 = re.compile(
    rf"^{discovery_pattern_group}\s+\[(?P<alteration_mix_1>Snow)\]\s+(?P<alteration_mix_2>UW)$",
    re.IGNORECASE)
# Pattern totd: "<totdname> (SnowCar UW)"
snowunderwater_totd_pattern_1 = re.compile(
    rf"^{totd_pattern_group}\s+\((?P<alteration_mix>SnowCar UW)\)$",
    re.IGNORECASE)
# Pattern weekly shorts: "<weeklyshortsname> - Underwater [Snow]"
snowunderwater_weeklyshorts_pattern_1 = re.compile(
    rf"^{weeklyshorts_pattern_group}\s+-\s+(?P<alteration_mix_1>Underwater) \[(?P<alteration_mix_2>Snow)\]$",
    re.IGNORECASE)
# Pattern weekly shorts: "<weeklyshortsname> - Underwater Snow"
snowunderwater_weeklyshorts_pattern_2 = re.compile(
    rf"^{weeklyshorts_pattern_group}\s+-\s+(?P<alteration_mix>Underwater Snow)$",
    re.IGNORECASE)

    # -------- [Snow] Wet Plastic ---------- #
# Pattern1: "(Snow) Wet Plastic <season> <year> - <mapnumber>"
snowwetplastic_seasonal_pattern_1 = re.compile(
    rf"^(?P<alteration_mix>\(Snow\) Wet Plastic)\s+(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)

    # -------- [Snow] Wood ---------- #
# Pattern seasonal: "[Snow] <season> <year> - <mapnumber> Wood"
snowwood_seasonal_pattern_1 = re.compile(
    rf"^(?P<alteration_mix_1>\[Snow\])\s+(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix_2>Wood)$",
    re.IGNORECASE)
# Pattern training: "[Snow] Training - <mapnumber> Wood"
snowwood_training_pattern_1 = re.compile(
    rf"^(?P<alteration_mix_1>\[Snow\])\s+(?P<season>Training)\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix_2>Wood)$",
    re.IGNORECASE)
# Pattern training: "[Snow] Training - <mapnumber_21> & <mapnumber_24> Wood" [Snow] Training - 21 & 24 Wood
snowwood_training_pattern_2124 = re.compile(
    rf"^(?P<alteration_mix_1>\[Snow\])\s+(?P<season>Training)\s*-\s*(?P<mapnumber_21>\d{{1,2}})\s*&\s*(?P<mapnumber_24>\d{{1,2}})\s+(?P<alteration_mix_2>Wood)$",
    re.IGNORECASE)

    # -------- [Rally] ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> [Rally]"
rally_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>\[Rally\])$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> - CarRally"
rally_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+-\s+(?P<alteration_mix>CarRally)$",
    re.IGNORECASE)
# Pattern training: "Training <mapnumber> - CarRally"
rally_training_pattern_1 = re.compile(
    rf"^(?P<special_map_name>.*?)\s+-\s+(?P<alteration_mix>CarRally)$",
    re.IGNORECASE)
# Pattern4: "<totd> (RallyCar)"
rally_totd_pattern_1 = re.compile(
    rf"^{totd_pattern_group}\s+\((?P<alteration_mix>RallyCar)\)$",
    re.IGNORECASE)

    # -------- [Rally] Carswitch ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> Rallycarswitch"
rallycarswitch_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Rallycarswitch)$",
    re.IGNORECASE)
# Pattern totd: "<totdname> (CS-RC)"
rallycarswitch_totd_pattern_1 = re.compile(
    rf"^{totd_pattern_group}\s+\((?P<alteration_mix>CS-RC)\)$",
    re.IGNORECASE)
# Pattern totd: "<totdname> (Carswitch RallyCar)"
rallycarswitch_totd_pattern_2 = re.compile(
    rf"^{totd_pattern_group}\s+\((?P<alteration_mix>Carswitch RallyCar)\)$",
    re.IGNORECASE)
# Pattern totd: "<totdname> (CS-Rally)"
rallycarswitch_totd_pattern_3 = re.compile(
    rf"^{totd_pattern_group}\s+\((?P<alteration_mix>CS-Rally)\)$",
    re.IGNORECASE)
# Pattern totd: "<totdname> (CS-RallyCar)"
rallycarswitch_totd_pattern_4 = re.compile(
    rf"^{totd_pattern_group}\s+\((?P<alteration_mix>CS-RallyCar)\)$",
    re.IGNORECASE)
# Pattern totd: "<totdname> (RallyCar)"
rallycarswitch_totd_pattern_5 = re.compile(
    rf"^{totd_pattern_group}\s+\((?P<alteration_mix>RallyCar)\)$",
    re.IGNORECASE)
# Pattern totd: "<totdname> (RallyCar"
rallycarswitch_totd_pattern_6 = re.compile(
    rf"^{totd_pattern_group}\s+\((?P<alteration_mix>RallyCar)$",
    re.IGNORECASE)

    # -------- [Rally] CP1 is End ---------- #
# Pattern seasonal: "[Rally] <season> <year> - <mapnumber> Cp1 is End"
rallycp1isend_seasonal_pattern_1 = re.compile(
    rf"^(?P<alteration_mix_1>\[Rally\])\s+(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix_2>Cp1 is End)$",
    re.IGNORECASE)
# Pattern seasonal: "[Rally] <season> <year> - <mapnumber> - Cp1 is End"
rallycp1isend_seasonal_pattern_2 = re.compile(
    rf"^(?P<alteration_mix_1>\[Rally\])\s+(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+-\s+(?P<alteration_mix_2>Cp1 is End)$",
    re.IGNORECASE)
# Pattern spring2020: "[Rally] <spring2020><mapnumber> - Cp1 is End"
rallycp1isend_spring2020_pattern_1 = re.compile(
    r"^(?P<alteration_mix_1>\[Rally\])\s+(?P<spring2020>[STst][0-1]\d)\s*-\s*(?P<alteration_mix_2>Cp1 is End)$",
    re.IGNORECASE)

    # -------- [Rally] Ice ---------- #
# Pattern seasonal: "Ricy <season> <year> - <mapnumber>"
rallyice_seasonal_pattern_1 = re.compile(
    rf"^(?P<alteration_mix>Ricy)\s+(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)

    # -------- [Rally] To The Top ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> Rally to the Top"
rallytothetop_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Rally to the Top)$",
    re.IGNORECASE)
# Pattern weekly shorts: "<weeklyshortsname> Rally To The Top"
rallytothetop_weeklyshorts_pattern_1 = re.compile(
    rf"^{weeklyshorts_pattern_group}\s+(?P<alteration_mix>Rally To The Top)$",
    re.IGNORECASE)

    # -------- [Rally] Underwater ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> [Rally] (Underwater)"
rallyunderwater_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\[Rally\]\s+\((?P<alteration_mix>Underwater)\)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> [Rally] (UW)"
rallyunderwater_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\[Rally\]\s+\((?P<alteration_mix>UW)\)$",
    re.IGNORECASE)
# Pattern training: "Training - <mapnumber> [Rally] (UW)"
rallyunderwater_training_pattern_1 = re.compile(
    rf"^(?P<season>Training)\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\[Rally\]\s+\((?P<alteration_mix>UW)\)$",
    re.IGNORECASE)
# Pattern discovery: "<discoveryname> [Rally] (UW)"
rallyunderwater_discovery_pattern_1 = re.compile(
    rf"^{discovery_pattern_group}\s+\[Rally\]\s+\((?P<alteration_mix>UW)\)$",
    re.IGNORECASE)

    # -------- [Desert] ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> [Desert]"
desert_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>\[Desert\])$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> - CarDesert"
desert_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+-\s+(?P<alteration_mix>CarDesert)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> - DesertCar"
desert_seasonal_pattern_3 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+-\s+(?P<alteration_mix>DesertCar)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> (DesertCar)"
desert_seasonal_pattern_4 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>DesertCar)\)$",
    re.IGNORECASE)
# Pattern training: "Training - <mapnumber> - CarDesert"
desert_training_pattern_1 = re.compile(
    rf"^(?P<season>Training)\s*-\s*(?P<mapnumber>\d{{1,2}})\s+-\s+(?P<alteration_mix>CarDesert)$",
    re.IGNORECASE)
# Pattern spring2020: "<spring2020><mapnumber> - CarDesert"
desert_spring2020_pattern_1 = re.compile(
    r"^(?P<spring2020>[STst][0-1]\d)\s+-\s+(?P<alteration_mix>CarDesert)$",
    re.IGNORECASE)
# Pattern discovery: "<discoveryname> - CarDesert"
desert_discovery_pattern_1 = re.compile(
    rf"^(?P<discoveryname>{discovery_pattern_group})\s+-\s+(?P<alteration_mix>CarDesert)$",
    re.IGNORECASE)
# Pattern totd: "<totdname> (DesertCar)"
desert_totd_pattern_1 = re.compile(
    rf"^{totd_pattern_group}\s+\((?P<alteration_mix>DesertCar)\)$",
    re.IGNORECASE)


    # -------- [Desert] Antiboost ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> - DAB"
desertantiboost_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+-\s+(?P<alteration_mix>DAB)$",
    re.IGNORECASE)
# Pattern discovery: "<discoveryname> - DAB"
desertantiboost_discovery_pattern_1 = re.compile(
    rf"^(?P<discoveryname>{discovery_pattern_group})\s+-\s+(?P<alteration_mix>DAB)$",
    re.IGNORECASE)
# Pattern weekly shorts: "<mapname> - DAB"
desertantiboost_weeklyshorts_pattern_1 = re.compile(
    rf"^(?P<mapname>{weeklyshorts_pattern_group})\s+-\s+(?P<alteration_mix>DAB)$",
    re.IGNORECASE)

    # -------- [Desert] Carswitch ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> Desertcarswitch"
desertcarswitch_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Desertcarswitch)$",
    re.IGNORECASE)
# Pattern totd: "<totdname> (CS-DC)"
desertcarswitch_totd_pattern_1 = re.compile(
    rf"^{totd_pattern_group}\s+\((?P<alteration_mix>CS-DC)\)$",
    re.IGNORECASE)
# Pattern totd: "<totdname> (CS-DesertCar)"
desertcarswitch_totd_pattern_2 = re.compile(
    rf"^{totd_pattern_group}\s+\((?P<alteration_mix>CS-DesertCar)\)$",
    re.IGNORECASE)
# Pattern totd: "<totdname> (Carswitch DesertCar)"
desertcarswitch_totd_pattern_3 = re.compile(
    rf"^{totd_pattern_group}\s+\((?P<alteration_mix>Carswitch DesertCar)\)$",
    re.IGNORECASE)
# Pattern totd: "<totdname> (Cawswitch DesertCar)"
desertcarswitch_totd_pattern_4 = re.compile(
    rf"^{totd_pattern_group}\s+\((?P<alteration_mix>Cawswitch DesertCar)\)$",
    re.IGNORECASE)

    # -------- [Desert] Ice ---------- #
# Pattern seasonal: "Dicy <season> <year> - <mapnumber>"
desertice_seasonal_pattern_1 = re.compile(
    rf"^(?P<alteration_mix>Dicy)\s+(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)

    # -------- [Desert] Icy Red Reactor Down ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> IDRRD" Fall 2024 - 12 IDRRD
deserticyredreactordown_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>IDRRD)$",
    re.IGNORECASE)

    # -------- [Desert] To The Top ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> Desert to the Top"
deserttothetop_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Desert to the Top)$",
    re.IGNORECASE)
# Pattern weekly shorts: "<mapname> Desert to the Top"
deserttothetop_weeklyshorts_pattern_1 = re.compile(
    rf"^(?P<mapname>{weeklyshorts_pattern_group})\s+(?P<alteration_mix>Desert to the Top)$",
    re.IGNORECASE)

    # -------- [Desert] Underwater ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> [Desert] (UW)"
desertunderwater_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>\[Desert\]\s+\(UW\))$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> (Desert) (UW)"
desertunderwater_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>Desert)\)\s+\(UW\)$",
    re.IGNORECASE)
# Pattern training: "Training - <mapnumber> [Desert] (UW)"
desertunderwater_training_pattern_1 = re.compile(
    rf"^(?P<season>Training)\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\[Desert\]\s+\(UW\)$",
    re.IGNORECASE)
# Pattern discovery: "<discoveryname> [Desert] UW"
desertunderwater_discovery_pattern_1 = re.compile(
    rf"^{discovery_pattern_group}\s+\[Desert\]\s+UW$",
    re.IGNORECASE)
# Pattern weekly shorts: "<weeklyshorts_pattern_group> [Desert] UW"
desertunderwater_weeklyshorts_pattern_1 = re.compile(
    rf"^(?P<name>{weeklyshorts_pattern_group})\s+\[Desert\]\s+UW$",
    re.IGNORECASE)

    # -------- [Desert] Reverse ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> - Reverse Desert"
desertreverse_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+-\s+(?P<alteration_mix>Reverse Desert)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> - Desert Reverse"
desertreverse_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+-\s+(?P<alteration_mix>Desert Reverse)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> Desert Reverse"
desertreverse_seasonal_pattern_3 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Desert Reverse)$",
    re.IGNORECASE)


    # -------- All Cars ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> all cars"
allcars_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>all cars)$",
    re.IGNORECASE)

    # -------- All Carswitch ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> 4CS"
allcarswitch_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>4CS)$",
    re.IGNORECASE)


# ################ Altered Game Mode ################ #

    # -------- [Race] ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> [Race]"
race_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>\[Race\])$",
    re.IGNORECASE)
# Pattern discovery: "<discovery> [Race]"
race_discovery_pattern_1 = re.compile(
    rf"^(?P<discoveryname>{discovery_pattern_group})\s+\[(?P<alteration_mix>Race)\]$",
    re.IGNORECASE)
# Pattern discovery: "<discovery> (Race)"
race_discovery_pattern_2 = re.compile(
    rf"^(?P<discoveryname>{discovery_pattern_group})\s+\((?P<alteration_mix>Race)\)$",
    re.IGNORECASE)
# Pattern discovery: "<discovery>_Race"
race_discovery_pattern_3 = re.compile(
    rf"^(?P<discoveryname>{discovery_pattern_group})_(?P<alteration_mix>Race)$",
    re.IGNORECASE)

    # -------- [Stunt] ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> [Stunt]"
stunt_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>\[Stunt\])$",
    re.IGNORECASE)

    # -------- [Platform] ---------- #
# Pattern1: "<season> <year> - <mapnumber> [Platform]"
platform_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>\[Platform\])$",
    re.IGNORECASE)


# ################ Multi alteration_mixs ################ #

    # -------- Checkpointless Reverse ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> (Checkpointless Reverse)"
checkpointlessreverse_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>Checkpointless Reverse)\)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> - CPLess, Reverse"
checkpointlessreverse_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+-\s+(?P<alteration_mix>CPLess, Reverse)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> - CPLess, Reverse (G)"
checkpointlessreverse_seasonal_pattern_3 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+-\s+(?P<alteration_mix>CPLess, Reverse \(G\))$",
    re.IGNORECASE)
# Pattern seasonal: "(G) <season> <year> - <mapnumber> - CPLess, Reverse"
checkpointlessreverse_seasonal_pattern_4 = re.compile(
    rf"^(?P<alteration_mix_1>\(G\))\s+(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+-\s+(?P<alteration_mix_2>CPLess, Reverse)$",
    re.IGNORECASE)
# Pattern seasonal: "<spring2020><mapnumber> (Checkpointless Reverse)"
checkpointlessreverse_spring2020_pattern_1 = re.compile(
    r"^(?P<spring2020>[STst][0-1]\d)\s+\((?P<alteration_mix>Checkpointless Reverse)\)$",
    re.IGNORECASE)

    # -------- DEET To The Top ---------- #
# Pattern1: "<season> <year> - <mapnumber> (DEET to the Top)"
deettothetop_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>DEET to the Top)\)$",
    re.IGNORECASE)

    # -------- Ice Reverse ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> IR"
icereverse_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>IR)$",
    re.IGNORECASE)
# Pattern seasonal: "Icy <season> <year> - <mapnumber> Reverse"
icereverse_seasonal_pattern_2 = re.compile(
    rf"^(?P<alteration_mix_1>Icy)\s+(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix_2>Reverse)$",
    re.IGNORECASE)

    # -------- Ice Reverse Reactor ---------- #
# Pattern seasonal: "Icy RR <season> <year> <mapnumber>"
icereversereactor_seasonal_pattern_1 = re.compile(
    rf"^(?P<alteration_mix>Icy RR)\s+(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s+(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)

    # -------- Ice Short ---------- #
# Pattern seasonal: "short - Icy <season> <year> - <mapnumber>" short - Icy Winter 2023 - 17
iceshort_seasonal_pattern_1 = re.compile(
    rf"^(?P<alteration_mix_1>short)\s+-\s+(?P<alteration_mix_2>Icy)\s+(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)
    
    # -------- Magnet Reverse ---------- #
# Pattern1: "<season> <year> - <mapnumber> Magnet Reverse"
magnetreverse_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Magnet Reverse)$",
    re.IGNORECASE)

    # -------- Plastic Reverse ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> PR"
plasticreverse_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>PR)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> PlasticReverse"
plasticreverse_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>PlasticReverse)$",
    re.IGNORECASE)

    # -------- Reverse Sky is the Finish ---------- #
# Pattern1: "<season> <year> - <mapnumber> - Rev Sky is Finish"
reverseskyfinish_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+-\s+(?P<alteration_mix>Rev Sky is Finish)$",
    re.IGNORECASE)
# Pattern2: "<season> <year> - <mapnumber> - Rev Sky Finish"
reverseskyfinish_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+-\s+(?P<alteration_mix>Rev Sky Finish)$",
    re.IGNORECASE)
# Pattern3: "<season> <year> - <mapnumber> - Rev Sky Fin"
reverseskyfinish_seasonal_pattern_3 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+-\s+(?P<alteration_mix>Rev Sky Fin)$",
    re.IGNORECASE)

    # -------- Start Water 2 UP 1 Left - Checkpoints Unlinked - Finish 2 Down 1 Right ---------- #
# Pattern1: "<season> <year> - <mapnumber> sw2u1l-cpu-f2d1r"
sw2u1lcpuf2d1r_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>sw2u1l-cpu-f2d1r)$",
    re.IGNORECASE)

    # -------- Underwater Reverse ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> (UW Reverse)"
underwaterreverse_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>UW Reverse)\)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> UW Reverse"
underwaterreverse_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>UW Reverse)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> (UW) (Reverse)"
underwaterreverse_seasonal_pattern_3 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix_1>UW)\)\s+\((?P<alteration_mix_2>Reverse)\)$",
    re.IGNORECASE)
# Pattern training: "Training - <mapnumber> (UW Reverse)"
underwaterreverse_training_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+-\s+(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>UW Reverse)\)$",
    re.IGNORECASE)

    # -------- Wet Plastic ---------- #
# Pattern seasonal: "Wet Plastic <season> <year> - <mapnumber>"
wetplastic_seasonal_pattern_1 = re.compile(
    rf"^(?P<alteration_mix>Wet Plastic)\s+(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s*$",
    re.IGNORECASE)
# Pattern training: "Wet Plastic Training - <mapnumber>"
wetplastic_training_pattern_1 = re.compile(
    rf"^(?P<alteration_mix>Wet Plastic)\s+Training\s+-\s+(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)
# Pattern training 21&24: "Wet Plastic Training - <mapnumber_1> & <mapnumber_2>"
wetplastic_training_pattern_2 = re.compile(
    rf"^(?P<alteration_mix>Wet Plastic)\s+Training\s+-\s+(?P<mapnumber_21>\d{{1,2}})\s+&\s+(?P<mapnumber_24>\d{{1,2}})$",
    re.IGNORECASE)
# Pattern weekly shorts: "<mapname> (Wet Plastic)"
wetplastic_weeklyshorts_pattern_1 = re.compile(
    rf"^(?P<mapname>{weeklyshorts_pattern_group})\s+\((?P<alteration_mix>Wet Plastic)\)$",
    re.IGNORECASE)
    
    # -------- Wet Wood ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> (Wet Wood)"
wetwood_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>Wet Wood)\)$",
    re.IGNORECASE)
# Pattern training: "Training - <mapnumber> (Wet Wood)"
wetwood_training_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+-\s+(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>Wet Wood)\)$",
    re.IGNORECASE)
# Pattern training 21&24: "Training - <mapnumber_1> & <mapnumber_2> (Wet Wood)"
wetwood_training_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+-\s+(?P<mapnumber_21>\d{{1,2}})\s+&\s+(?P<mapnumber_24>\d{{1,2}})\s+\((?P<alteration_mix>Wet Wood)\)$",
    re.IGNORECASE)
# Pattern spring2020: "<spring2020><mapnumber> (Wet Wood)"
wetwood_spring2020_pattern_1 = re.compile(
    r"^(?P<spring2020>[STst][0-1]\d)\s+\((?P<alteration_mix>Wet Wood)\)$",
    re.IGNORECASE)
# Pattern totd: "<totdname> (Wet Wood)"
wetwood_totd_pattern_1 = re.compile(
    rf"^{totd_pattern_group}\s+\((?P<alteration_mix>Wet Wood)\)$",
    re.IGNORECASE)
# Pattern weekly shorts: "<mapname> (Wet Wood)"
wetwood_weeklyshorts_pattern_1 = re.compile(
    rf"^(?P<mapname>{weeklyshorts_pattern_group})\s+\((?P<alteration_mix>Wet Wood)\)$",
    re.IGNORECASE)
# ------------------------------------------------------------------------------ #
# Pattern seasonal: "<season> <year> - <mapnumber> (Wet Wood Yellow Reactor Down)"
wetwoodyrd_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>Wet Wood Yellow Reactor Down)\)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> (Wet Wood Red Reactor Down)"
wetwoodrrd_seasonal_pattern_3 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>Wet Wood Red Reactor Down)\)$",
    re.IGNORECASE)

    # -------- Wet Icy Wood ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> (Wet Icy Wood)"
weticywood_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>Wet Icy Wood)\)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> (WetIcyWood)"
weticywood_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>WetIcyWood)\)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> (100% Wet Icy Wood)"
weticywood_seasonal_pattern_3 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>100% Wet Icy Wood)\)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> (Pure Wet Icy Wood)"
weticywood_seasonal_pattern_4 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>Pure Wet Icy Wood)\)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> (Pure WetIcyWood)"
weticywood_seasonal_pattern_5 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>Pure WetIcyWood)\)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> (100% WetIcyWood)"
weticywood_seasonal_pattern_6 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>100% WetIcyWood)\)$",
    re.IGNORECASE)
# Pattern training: "Training - <mapnumber> (Wet Icy Wood)"
weticywood_training_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+-\s+(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>Wet Icy Wood)\)$",
    re.IGNORECASE)
# Pattern training: "Training - <mapnumber> (100% Wet Icy Wood)"
weticywood_training_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+-\s+(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>100% Wet Icy Wood)\)$",
    re.IGNORECASE)
# Pattern training: "Training - <mapnumber> (Pure Wet Icy Wood)"
weticywood_training_pattern_3 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+-\s+(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>Pure Wet Icy Wood)\)$",
    re.IGNORECASE)
# Pattern training 21,22,23,24: "Training - <mapnumber_21>,<mapnumber_22>,<mapnumber_23> & <mapnumber_24> (100% Wet Icy Wood)"
weticywood_training_pattern_4 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+-\s+(?P<mapnumber_21>\d{{1,2}}),\s*(?P<mapnumber_22>\d{{1,2}}),\s*(?P<mapnumber_23>\d{{1,2}})\s*&\s*(?P<mapnumber_24>\d{{1,2}})\s+\((?P<alteration_mix>100% Wet Icy Wood)\)$",
    re.IGNORECASE)
# Pattern training 21,22,23,24: "Training - <mapnumber_21>,<mapnumber_22>,<mapnumber_23> & <mapnumber_24> (Pure Wet Icy Wood)"
weticywood_training_pattern_5 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+-\s+(?P<mapnumber_21>\d{{1,2}}),\s*(?P<mapnumber_22>\d{{1,2}}),\s*(?P<mapnumber_23>\d{{1,2}})\s*&\s*(?P<mapnumber_24>\d{{1,2}})\s+\((?P<alteration_mix>Pure Wet Icy Wood)\)$",
    re.IGNORECASE)
# Pattern spring2020: "<spring2020><mapnumber> (Wet Icy Wood)"
weticywood_spring2020_pattern_1 = re.compile(
    r"^(?P<spring2020>[STst][0-1]\d)\s+\((?P<alteration_mix>Wet Icy Wood)\)$",
    re.IGNORECASE)
# Pattern discovery: "<discoveryname> (Wet Icy Wood)"
weticywood_discovery_pattern_1 = re.compile(
    rf"^(?P<discoveryname>{discovery_pattern_group})\s+\((?P<alteration_mix>Wet Icy Wood)\)$",
    re.IGNORECASE)
# Pattern discovery: "<discoveryname> (100% Wet Icy Wood)"
weticywood_discovery_pattern_2 = re.compile(
    rf"^(?P<discoveryname>{discovery_pattern_group})\s+\((?P<alteration_mix>100% Wet Icy Wood)\)$",
    re.IGNORECASE)
# Pattern discovery: "<discoveryname> (Pure Wet Icy Wood)"
weticywood_discovery_pattern_3 = re.compile(
    rf"^(?P<discoveryname>{discovery_pattern_group})\s+\((?P<alteration_mix>Pure Wet Icy Wood)\)$",
    re.IGNORECASE)
# Pattern totd: "<totdname> (Wet Icy Wood)"
weticywood_totd_pattern_1 = re.compile(
    rf"^{totd_pattern_group}\s+\((?P<alteration_mix>Wet Icy Wood)\)$",
    re.IGNORECASE)
# Pattern totd: "<totdname> (100% WIW)"
weticywood_totd_pattern_2 = re.compile(
    rf"^{totd_pattern_group}\s+\((?P<alteration_mix>100% WIW)\)$",
    re.IGNORECASE)
# Pattern weekly shorts: "<mapname> (Wet Icy Wood)"
weticywood_weeklyshorts_pattern_1 = re.compile(
    rf"^(?P<mapname>{weeklyshorts_pattern_group})\s+\((?P<alteration_mix>Wet Icy Wood)\)$",
    re.IGNORECASE)

    # -------- Wet Icy Plastic ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> (Wet Icy Plastic)"
weticyplastic_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>Wet Icy Plastic)\)$",
    re.IGNORECASE)
# Pattern training: "Training - <mapnumber> (Wet Icy Plastic)"
weticyplastic_training_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+-\s+(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>Wet Icy Plastic)\)$",
    re.IGNORECASE)
# Pattern training 21&24: "Training - <mapnumber_21> & <mapnumber_24> (Wet Icy Plastic)"
weticyplastic_training_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+-\s+(?P<mapnumber_21>\d{{1,2}})\s+&\s+(?P<mapnumber_24>\d{{1,2}})\s+\((?P<alteration_mix>Wet Icy Plastic)\)$",
    re.IGNORECASE)
# Pattern totd: "<totdname> (Wet Icy Plastic)"
weticyplastic_totd_pattern_1 = re.compile(
    rf"^{totd_pattern_group}\s+\((?P<alteration_mix>Wet Icy Plastic)\)$",
    re.IGNORECASE)
# Pattern discovery: "<discoveryname> (Wet Icy Plastic)"
weticyplastic_discovery_pattern_1 = re.compile(
    rf"^(?P<discoveryname>{discovery_pattern_group})\s+\((?P<alteration_mix>Wet Icy Plastic)\)$",
    re.IGNORECASE)
# Pattern weekly shorts: "<mapname> (Wet Icy Plastic)"
weticyplastic_weeklyshorts_pattern_1 = re.compile(
    rf"^(?P<mapname>{weeklyshorts_pattern_group})\s+\((?P<alteration_mix>Wet Icy Plastic)\)$",
    re.IGNORECASE)

    # -------- YEET Max-Up ---------- #
# Pattern seasonal: "YEET <season> <year> - <mapnumber> Max-up"
yeetmaxup_seasonal_pattern_1 = re.compile(
    rf"^(?P<alteration_mix_1>YEET)\s+(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{2,4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix_2>Max-up)$",
    re.IGNORECASE)

    # -------- YEET (Random) Puzzle ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> (YEET Puzzle)"
yeetpuzzle_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>Yeet Puzzle)\)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> (YEET Random Puzzle)"
yeetrandompuzzle_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>Yeet Random Puzzle)\)$",
    re.IGNORECASE)
# Pattern training: "Training - <mapnumber> YEET Puzzle"
yeetpuzzle_training_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+-\s+(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>YEET Puzzle)$",
    re.IGNORECASE)

    # -------- YEET Reverse ---------- #
# Pattern1: "YEET <season> <year> - <mapnumber> Reverse"
yeetreverse_seasonal_pattern_1 = re.compile(
    rf"^(?P<alteration_mix_1>YEET)\s+(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{2,4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix_2>Reverse)$",
    re.IGNORECASE)


# ################ Other alteration_mixs ################ #

    # -------- XX-But ---------- #
# Pattern1: ""
#xxbut_seasonal_pattern_1 = re.compile(
#    rf"",
#    re.IGNORECASE
#)

    # -------- Flat/2D ---------- #
# Pattern seasonal: "FLAT <season> <year> - <mapnumber>"
flat_seasonal_pattern_1 = re.compile(
    rf"^(?P<alteration_mix>FLAT)\s+(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{2,4}})\s*-\s*(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)
# Pattern seasonal: "Flat<season>'<year> - <mapnumber>"
flat_seasonal_pattern_2 = re.compile(
    rf"^(?P<alteration_mix>Flat)(?P<season>{SEASON_REGEX})['’](?P<year>\d{{2}})\s+-\s+(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)
# Pattern seasonal: "2D-<season><year>-<mapnumber>"
flat_seasonal_pattern_3 = re.compile(
    rf"^(?P<alteration_mix>2D)-(?P<season>{SEASON_REGEX})(?P<year>\d{{4}})-(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)    
# Pattern training: "Flat Training - <mapnumber>"
flat_training_pattern_1 = re.compile(
    rf"^(?P<alteration_mix>Flat)\s(?P<season>Training)\s+-\s+(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)
# Pattern training: "Training - <mapnumber> Flat"
flat_training_pattern_2 = re.compile(
    rf"^(?P<season>Training)\s+-\s+(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Flat)$",
    re.IGNORECASE)

    # -------- A08 ---------- #
# Pattern1: "<season> <year> - <mapnumber> - 08"
a08_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+-\s+(?P<alteration_mix>08)$",
    re.IGNORECASE)

    # -------- Backwards ---------- #
# Pattern1: "<season> <year> - <mapnumber> backwards"
backwards_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>backwards)$",
    re.IGNORECASE)

    # -------- BOSS ---------- #
# Pattern seasonal: "<mapnumber_color> BOSS - <season>'<year>"
boss_seasonal_pattern_1 = re.compile(
    rf"^(?P<mapnumber_color>{MAPNUMBER_COLOR_REGEX})\s+(?P<alteration_mix>BOSS)\s+-\s+(?P<season>{SEASON_REGEX})['’](?P<year>\d{{2}})$",
    re.IGNORECASE)
# Pattern seasonal: "BOSS <mapnumber_color> of <season> <year>"
boss_seasonal_pattern_2 = re.compile(
    rf"^(?P<alteration_mix>BOSS)\s+(?P<mapnumber_color>{MAPNUMBER_COLOR_REGEX})\s+of\s+(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})$",
    re.IGNORECASE)
# Pattern seasonal: "<mapnumber_color> BOSS <season> <year>"
boss_seasonal_pattern_3 = re.compile(
    rf"^(?P<mapnumber_color>{MAPNUMBER_COLOR_REGEX})\s+(?P<alteration_mix>BOSS)\s+(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})$",
    re.IGNORECASE)


    # -------- Bumper ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> - Bumper"
bumper_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+-\s+(?P<alteration_mix>Bumper)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> - Bumper"
bumper_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{2}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+-\s+(?P<alteration_mix>Bumper)$",
    re.IGNORECASE)
# Pattern seasonal: "Training - <mapnumber> Bumper"
bumper_training_pattern_2 = re.compile(
    rf"^(?P<season>Training)\s+-\s+(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Bumper)$",
    re.IGNORECASE)

# #### Altered Camera #### #
    # -------- Blind ---------- #
# Pattern seasonal: "<season> <mapnumber> (Blind)"
blind_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>Blind)\)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> But Blind"
blind_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>But Blind)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> Blindfolded"
blind_seasonal_pattern_3 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Blindfolded)$",
    re.IGNORECASE)
# Pattern training: "Blind Training - <mapnumber>"
blind_training_pattern_1 = re.compile(
    rf"^(?P<alteration_mix>Blind)\s+(?P<season>Training)\s+-\s+(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)
    # -------- Egocentrism ---------- #
# Pattern1: "<season> <year> - <mapnumber> Egocentrism"
egocentrism_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Egocentrism)$",
    re.IGNORECASE)
    # -------- Replay ---------- #
# Pattern1: "<season> <year> - Replay <mapnumber>"
replay_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s+(?P<alteration_mix>Replay)\s+(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)
# #### End of Altered Camera #### #

    # -------- N'golo ---------- #
# Pattern seasonal: "<season>N'golo <year> - <mapnumber>"
ngolo_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})N'golo\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)
# Pattern seasonal: "<season>olo <year> - <mapnumber>"
ngolo_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>Spring)olo\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)

    # -------- Checkpoin't ---------- #
# Pattern seasonal: "<season> <year> Checkpoin't - <mapnumber>"
checkpoin_t_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s+(?P<alteration_mix>Checkpoin't)\s+-\s+(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - Checkpoin't - <mapnumber>"
checkpoin_t_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s+(?P<alteration_mix>Checkpoin't)\s+-\s+(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - Checkpoin't <mapnumber>"
checkpoin_t_seasonal_pattern_3 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s+(?P<alteration_mix>Checkpoin't)\s+(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)

    # -------- Colour Combined ---------- #
# Pattern seasonal: "<season> <year> - <each map number in sets from 1-5 shown in sets using colours, white = 1-5, green = 6-10, blue = 11-15, red 16-20 black 21-25> Combined"
colourcombined_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s+(?P<mapnumber_color>{MAPNUMBER_COLOR_REGEX})\s+(?P<alteration_mix>Combined)$",
    re.IGNORECASE)
# Pattern training: "Training - <mapnumber_color> Combined"
colourcombined_training_pattern_1 = re.compile(
    rf"^(?P<season>Training)\s+-\s+(?P<mapnumber_color>{MAPNUMBER_COLOR_REGEX})\s+(?P<alteration_mix>Combined)$",
    re.IGNORECASE)

    # -------- Checkpoint Boost Swap ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> CP-Boost Swap"
checkpointboostswap_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>CP-Boost Swap)$",
    re.IGNORECASE)
# Pattern training: "Training - <mapnumber> (CP-Boost)"
checkpointboostswap_training_pattern_1 = re.compile(
    rf"^(?P<season>Training)\s+-\s+(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>CP-Boost)\)$",
    re.IGNORECASE)
# Pattern spring2020: "<spring2020><mapnumber> CP-Boost"
checkpointboostswap_spring2020_pattern_1 = re.compile(
    r"^(?P<spring2020>[STst][0-1]\d)\s+(?P<alteration_mix>CP-Boost)$",
    re.IGNORECASE)

    # -------- Checkpoint 1 Kept ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> CP1 Kept"
checkpoint1kept_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>CP1 Kept)$",
    re.IGNORECASE)

    # -------- Checkpointfull ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> CPfull"
checkpointfull_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>CPfull)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> CPfull (-NN)"
checkpointfull_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>CPfull)\s+\((?P<alteration_mixinfo>-?\d+)\)$",
    re.IGNORECASE)
# Pattern training: "Training - <mapnumber> CPfull"
checkpointfull_training_pattern_1 = re.compile(
    rf"^(?P<season>Training)\s+-\s+(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>CPfull)$",
    re.IGNORECASE)
# Pattern weekly shorts: "<mapname> CPfull"
checkpointfull_weeklyshorts_pattern_1 = re.compile(
    rf"^(?P<mapname>{weeklyshorts_pattern_group})\s+(?P<alteration_mix>CPfull)$",
    re.IGNORECASE)
# Pattern weekly shorts: "<mapname> CPfull (-NN)"
checkpointfull_weeklyshorts_pattern_2 = re.compile(
    rf"^(?P<mapname>{weeklyshorts_pattern_group})\s+(?P<alteration_mix>CPfull)\s+\((?P<alteration_mixinfo>-?\d+)\)$",
    re.IGNORECASE)

    # -------- Checkpointless ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> - Checkpointless"
checkpointless_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+-\s+(?P<alteration_mix>Checkpointless)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> Checkpointless"
checkpointless_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Checkpointless)$",
    re.IGNORECASE)
# Pattern training: "Training - <mapnumber> - Checkpointless"
checkpointless_training_pattern_1 = re.compile(
    rf"^(?P<season>Training)\s+-\s+(?P<mapnumber>\d{{1,2}})\s+-\s+(?P<alteration_mix>Checkpointless)$",
    re.IGNORECASE)
# Pattern training: "Training - <mapnumber> - CPLess"
checkpointless_training_pattern_2 = re.compile(
    rf"^(?P<season>Training)\s+-\s+(?P<mapnumber>\d{{1,2}})\s+-\s+(?P<alteration_mix>CPLess)$",
    re.IGNORECASE)
# Pattern training: "Training - <mapnumber> cpless"
checkpointless_training_pattern_3 = re.compile(
    rf"^(?P<season>Training)\s+-\s+(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>cpless)$",
    re.IGNORECASE)
# Pattern spring2020: "<spring2020><mapnumber> - Checkpointless"
checkpointless_spring2020_pattern_1 = re.compile(
    r"^(?P<spring2020>[STst][0-1]\d)\s+-\s+(?P<alteration_mix>Checkpointless)$",
    re.IGNORECASE)
# Pattern spring2020: "<spring2020><mapnumber> cpless"
checkpointless_spring2020_pattern_2 = re.compile(
    r"^(?P<spring2020>[STst][0-1]\d)\s+(?P<alteration_mix>cpless)$",
    re.IGNORECASE)
# Pattern discovery: "<discoveryname> - Checkpointless"
checkpointless_discovery_pattern_1 = re.compile(
    rf"^(?P<discoveryname>{discovery_pattern_group})\s+-\s+(?P<alteration_mix>Checkpointless)$",
    re.IGNORECASE)
# Pattern totd: "<totdname> (cpless)"
checkpointless_totd_pattern_1 = re.compile(
    rf"^{totd_pattern_group}\s+\((?P<alteration_mix>cpless)\)$",
    re.IGNORECASE)
# Pattern totd: "<mapname> (CPLess-STTF)"
checkpointless_totd_pattern_2 = re.compile(
    rf"^{totd_pattern_group}\s+\((?P<alteration_mix>CPLess-STTF)\)$",
    re.IGNORECASE)
# Pattern totd: "<mapname> (STTF-CPLess)"
checkpointless_totd_pattern_3 = re.compile(
    rf"^{totd_pattern_group}\s+\((?P<alteration_mix>STTF-CPLess)\)$",
    re.IGNORECASE)
# Pattern totd: "<mapname> (CPLess - STTF)"
checkpointless_totd_pattern_4 = re.compile(
    rf"^{totd_pattern_group}\s+\((?P<alteration_mix>CPLess\s*-\s*STTF)\)$",
    re.IGNORECASE)
# Pattern totd: "<totdname> (STTF - CPLess)"
checkpointless_totd_pattern_5 = re.compile(
    rf"^{totd_pattern_group}\s+\((?P<alteration_mix>STTF\s*-\s*CPLess)\)$",
    re.IGNORECASE)
# Pattern weekly shorts: "<mapname> - Checkpointless"
checkpointless_weeklyshorts_pattern_1 = re.compile(
    rf"^(?P<mapname>{weeklyshorts_pattern_group})\s+-\s+(?P<alteration_mix>Checkpointless)$",
    re.IGNORECASE)

    # -------- Checkpointlink ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> CPLink"
checkpointlink_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>CPLink)$",
    re.IGNORECASE)

    # -------- Checkpoints Rotated 90° / Got Rotated ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> - CPs Rotated 90°"
checkpointsrotated90_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+-\s+(?P<alteration_mix>CPs Rotated 90°)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> CPs Rotated 90°"
checkpointsrotated90_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>CPs Rotated 90°)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> - CPs Rotated 90"
checkpointsrotated90_seasonal_pattern_3 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+-\s+(?P<alteration_mix>CPs Rotated 90)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> Got Rotated"
gotrotated_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Got Rotated)$",
    re.IGNORECASE)

    # -------- DragonYeet ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> (DragonYeet)"
dragonyeet_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>DragonYeet)\)$",
    re.IGNORECASE)

    # -------- Earthquake ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> Earthquake"
earthquake_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Earthquake)$",
    re.IGNORECASE)
# Pattern training: "Training - <mapnumber> Earthquake"
earthquake_training_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+-\s+(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Earthquake)$",
    re.IGNORECASE)

    # -------- Extra Checkpoint ---------- #
# Pattern1: "<season> <year> - <mapnumber> Extra CP"
extracheckpoint_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Extra CP)$",
    re.IGNORECASE)

    # -------- Flipped ---------- #
# Pattern1: "<season> <year> - <mapnumber> (Flipped)"
flipped_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>Flipped)\)$",
    re.IGNORECASE)
# Pattern2: "<season><year>UpsideDown - <mapnumber>"
flipped_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})(?P<year>\d{{4}})(?P<alteration_mix>UpsideDown)\s+-\s+(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)
# Pattern weekly shorts: "<mapname> (Flipped)"
flipped_weeklyshorts_pattern_1 = re.compile(
    rf"^(?P<mapname>{weeklyshorts_pattern_group})\s+\((?P<alteration_mix>Flipped)\)$",
    re.IGNORECASE)

    # -------- Holes ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> (Holes)"
holes_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>Holes)\)$",
    re.IGNORECASE)
# Pattern training: "Training - <mapnumber> Holes"
holes_training_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+-\s+(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Holes)$",
    re.IGNORECASE)
# Pattern weekly shorts: "<mapname> (Holes)"
holes_weeklyshorts_pattern_1 = re.compile(
    rf"^(?P<mapname>{weeklyshorts_pattern_group})\s+\((?P<alteration_mix>Holes)\)$",
    re.IGNORECASE)

    # -------- Invisible ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> (Invisible)"
invisible_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>Invisible)\)$",
    re.IGNORECASE)
# Pattern training: "Training - <mapnumber> (Invisible)"
invisible_training_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+-\s+(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>Invisible)\)$",
    re.IGNORECASE)

    # -------- Lunatic ---------- #
# Pattern1: "Lunatic <season> <year> - <mapnumber>"
lunatic_seasonal_pattern_1 = re.compile(
    rf"^(?P<alteration_mix>Lunatic)\s+(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)
# Pattern2: "Harder <season> <year> - <mapnumber>"
lunatic_seasonal_pattern_2 = re.compile(
    rf"^(?P<alteration_mix>Harder)\s+(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)

    # -------- Mini-RPG ---------- #
# Pattern seasonal: "RPG <season><year> - <mapnumber>"
minirpg_seasonal_pattern_1 = re.compile(
    rf"^(?P<alteration_mix>RPG)\s+(?P<season>{SEASON_SHORT_REGEX})(?P<year>\d{{2}})\s*-\s*(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> Mini RPG"
minirpg_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Mini RPG)$",
    re.IGNORECASE)

    # -------- Mirrored ---------- #
# Pattern seasonal: "<season> <mapnumber> (Mirror)"
mirrored_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>Mirror)\)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> Mirrored"
mirrored_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Mirrored)$",
    re.IGNORECASE)
# Pattern training: "Training - <mapnumber> Mirrored"
mirrored_training_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+-\s+(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Mirrored)$",
    re.IGNORECASE)

    # -------- No Items ---------- #
# Pattern1: "<season> <year> - <mapnumber> NoItems"
noitems_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>NoItems)$",
    re.IGNORECASE)

    # -------- Pool Hunters ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> Pool Hunters"
poolhunters_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Pool Hunters)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> poolhunter - <mapnumber>"
poolhunters_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s+(?P<alteration_mix>poolhunter)\s*-\s*(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)
# Pattern seasonal: "Poolhunter <season> <year> - <mapnumber>"
poolhunters_seasonal_pattern_3 = re.compile(
    rf"^(?P<alteration_mix>Poolhunter)\s+(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> poolhunters - <mapnumber>"
poolhunters_seasonal_pattern_4 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{2}})\s+(?P<alteration_mix>poolhunters)\s*-\s*(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)

    # -------- Random ---------- #
# Pattern1: "Random <season> <year> - <mapnumber>"
random_seasonal_pattern_1 = re.compile(
    rf"^(?P<alteration_mix>Random)\s+(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)

    # -------- Ring Checkpoint ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> Ring CP"
ringcheckpoint_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Ring CP)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> (Ring CP)"
ringcheckpoint_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>Ring CP)\)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> Ring CP%"
ringcheckpoint_seasonal_pattern_3 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Ring CP%)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> - ring cp"
ringcheckpoint_seasonal_pattern_4 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+-\s+(?P<alteration_mix>ring cp)$",
    re.IGNORECASE)
# Pattern training: "Training - <mapnumber> Ring CP"
ringcheckpoint_training_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+-\s+(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Ring CP)$",
    re.IGNORECASE)

    # -------- Sections Joined ---------- #
# FIXME: This alteration_mix is fundamentally different regarding "mapnumber", as it applies to multiple maps, I will likely say that 'map 1 is the first section of each set' etc
# Pattern seasonal: "<season> <year> - Section [Index] joined"
sectionsjoined_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<alteration_mix>Section\s*(?P<mapnumber>\d{{1,2}})\s*joined)\.*$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - Last Section Joined (All Ends)"
sectionsjoined_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<alteration_mix>Last Section Joined)\s+\((?P<alteration_mixinfo>All Ends)\)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - Last Section Joined"
sectionsjoined_seasonal_pattern_3 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<alteration_mix>Last Section Joined)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - Section 1 Joined (All Starts)"
sectionsjoined_seasonal_pattern_4 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<alteration_mix>Section 1 Joined)\s+\((?P<alteration_mixinfo>All Starts)\)$",
    re.IGNORECASE)

    # -------- Select DEL ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> (Select DEL)"
selectdel_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>Select DEL)\)$",
    re.IGNORECASE)

    # -------- Speedlimit ---------- #
# Pattern seaonal: "<season> <year> - <mapnumber> (Speedlimit)"
speedlimit_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>Speedlimit)\)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> Speed Limit"
speedlimit_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Speed Limit)\s*$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> Speedlimit"
speedlimit_seasonal_pattern_3 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Speedlimit)$",
    re.IGNORECASE)

    # -------- Start 1-Down ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> (Start 1-Down)"
start1down_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>Start 1-Down)\)$",
    re.IGNORECASE)

    # -------- Supersized ---------- #
# FIXME: Supersized_Spring_2024_-_05 just found out that cases like <--- exist, so I have to replace "_" with " " before doing any regex? (or is this also counted as a whitespace?)
# Pattern seasonal: "Supersized <season> <year> - <mapnumber>"
supersized_seasonal_pattern_1 = re.compile(
    rf"^(?P<alteration_mix>Supersized)\s+(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> <mapnumber> Big"
supersized_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s+(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Big)$",
    re.IGNORECASE)
# Pattern seasonal: "Super<mapnumber>"
supersized_seasonal_pattern_3 = re.compile(
    rf"^(?P<alteration_mix>Super)(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> Supersized <mapnumber>"
supersized_seasonal_pattern_4 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s+(?P<alteration_mix>Supersized)\s+(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> <mapnumber> Supersized"
supersized_seasonal_pattern_5 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s+(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Supersized)$",
    re.IGNORECASE)
# Pattern seasonal: "Supersized Training - <mapnumber>"
supersized_training_pattern_1 = re.compile(
    rf"^(?P<alteration_mix>Supersized)\s+(?P<season>Training)\s+-\s+(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)

    # -------- Straight to the Finish ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> Straight to the Finish"
straighttothefinish_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Straight to the Finish)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> STTF"
straighttothefinish_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>STTF)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> - sttf"
straighttothefinish_seasonal_pattern_3 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+-\s+(?P<alteration_mix>sttf)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> (STTF)"
straighttothefinish_seasonal_pattern_4 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>STTF)\)$",
    re.IGNORECASE)
# Pattern training: "Training - <mapnumber> STTF"
straighttothefinish_training_pattern_1 = re.compile(
    rf"^(?P<season>Training)\s+-\s+(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>STTF)$",
    re.IGNORECASE)
# Pattern spring2020: "<spring2020><mapnumber> STTF"
straighttothefinish_spring2020_pattern_1 = re.compile(
    r"^(?P<spring2020>[STst][0-1]\d)\s+(?P<alteration_mix>STTF)$",
    re.IGNORECASE)
# Pattern discovery: "<discoveryname> (STTF)"
straighttothefinish_discovery_pattern_1 = re.compile(
    rf"^(?P<discoveryname>{discovery_pattern_group})\s+\((?P<alteration_mix>STTF)\)$",
    re.IGNORECASE)
# Pattern totd: "<totdname> (STTF)"
straighttothefinish_totd_pattern_1 = re.compile(
    rf"^{totd_pattern_group}\s+\((?P<alteration_mix>STTF)\)$",
    re.IGNORECASE)
# Pattern weekly shorts: "<mapname> (STTF)"
straighttothefinish_weeklyshorts_pattern_1 = re.compile(
    rf"^(?P<mapname>{weeklyshorts_pattern_group})\s+\((?P<alteration_mix>STTF)\)$",
    re.IGNORECASE)

    # -------- Stunt Mode ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> Stunt"
stuntmode_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Stunt)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> Stunt Mode"
stuntmode_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Stunt Mode)$",
    re.IGNORECASE)

    # -------- Symmetrical ---------- #
# Pattern seasonal: "Symmetrical <season> <year> - <mapnumber>"
symmetrical_seasonal_pattern_1 = re.compile(
    rf"^(?P<alteration_mix>Symmetrical)\s+(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)

    # -------- Tilted ---------- #
# Pattern seasonal: "<season> <mapnumber> - Tilted"
tilted_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<mapnumber>\d{{1,2}})\s+-\s+(?P<alteration_mix>Tilted)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> Tilted"
tilted_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Tilted)$",
    re.IGNORECASE)
# Pattern training: "Training - <mapnumber> Tilted"
tilted_training_pattern_1 = re.compile(
    rf"^(?P<season>Training)\s+-\s+(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Tilted)$",
    re.IGNORECASE)

    # -------- YEET ---------- #
# Pattern seasonal: "YEET <season> <year> - <mapnumber>"
yeet_seasonal_pattern_1 = re.compile(
    rf"^(?P<alteration_mix>YEET)\s+(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)
# Pattern training: "YEET Training - <mapnumber>"
yeet_training_pattern_1 = re.compile(
    rf"^(?P<alteration_mix>YEET)\s+(?P<season>Training)\s+-\s+(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)
# Pattern spring2020: "YEET <spring2020><mapnumber>"
yeet_spring2020_pattern_1 = re.compile(
    r"^(?P<alteration_mix>YEET)\s+(?P<spring2020>[STst][0-1]\d).*$",
    re.IGNORECASE)
# Pattern discovery: "YEET <discoveryname>"
yeet_discovery_pattern_1 = re.compile(
    rf"^(?P<alteration_mix>YEET)\s+(?P<discoveryname>{discovery_pattern_group})$",
    re.IGNORECASE)
# Pattern totd: "<totdname> (Yeet)"
yeet_totd_pattern_1 = re.compile(
    rf"^{totd_pattern_group}\s+\((?P<alteration_mix>Yeet)\)$",
    re.IGNORECASE)


    # -------- YEET Down ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> (DEET)"
yeetdown_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+\((?P<alteration_mix>DEET)\)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> - Deet"
yeetdown_seasonal_pattern_2 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+-\s+(?P<alteration_mix>Deet)$",
    re.IGNORECASE)
# Pattern seasonal: "<season> <year> - <mapnumber> Deet"
yeetdown_seasonal_pattern_3 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Deet)$",
    re.IGNORECASE)


# ################ Competition alteration_mixs

    # -------- Easy Mode ---------- #
# Pattern competition: "<competitionname> [Easy Mode]"
easymode_competition_pattern_1 = re.compile(
    rf"^(?P<competitionname>{competition_pattern_group})\s+\[(?P<alteration_mix>Easy Mode)\]$",
    re.IGNORECASE)



# ################ Other alteration_mixs ################ #

    # -------- Chinese ---------- #
# Pattern seasonal: "<season_chinese> <year> - <mapnumber>"
chinese_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_CHINESE_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)
# Pattern training: "<season_chinese> - <mapnumber>"
chinese_training_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_CHINESE_REGEX})\s+-\s+(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)

    # -------- All 1-Up ---------- #
# Pattern seasonal: "<season> <year> - <mapnumber> All 1-Up"
all1up_seasonal_pattern_1 = re.compile(
    rf"^(?P<season>{SEASON_REGEX})\s+(?P<year>\d{{4}})\s*-\s*(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>All 1-Up)$",
    re.IGNORECASE)



# ################ Sorted as only training ################ #

    # -------- Walmart Mini ---------- #
# Pattern training: "Training - <mapnumber> Walmart Mini"
wallmartmini_training_pattern_1 = re.compile(
    rf"^(?P<season>Training)\s+-\s+(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Walmart Mini)$",
    re.IGNORECASE)

    # -------- Staircase ---------- #
# Pattern training: "Training Staircase - <mapnumber>"
staircase_training_pattern_1 = re.compile(
    rf"^(?P<season>Training)\s+(?P<alteration_mix>Staircase)\s+-\s+(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)

    # -------- Ice Reactor ---------- #
# Pattern training: "Icy Reactor Training - <mapnumber>"
icereactor_training_pattern_1 = re.compile(
    rf"^(?P<alteration_mix>Icy Reactor)\s+(?P<season>Training)\s+-\s+(?P<mapnumber>\d{{1,2}})$",
    re.IGNORECASE)

    # -------- Better Mixed ---------- #
# Pattern training: "Training - <mapnumber> Better Mixed"
bettermixed_training_pattern_1 = re.compile(
    rf"^(?P<season>Training)\s+-\s+(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Better Mixed)$",
    re.IGNORECASE)

    # -------- No Cut ---------- #
# Pattern training: "Training - <mapnumber> No-Cut"
nocut_training_pattern_1 = re.compile(
    rf"^(?P<season>Training)\s+-\s+(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>No-Cut)$",
    re.IGNORECASE)

    # -------- Platform ---------- #
# Pattern training: "Training - <mapnumber> Platform"
platform_training_pattern_1 = re.compile(
    rf"^(?P<season>Training)\s+-\s+(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Platform)$",
    re.IGNORECASE)

    # -------- Road Dirt ---------- #
# Pattern training: "Training - <mapnumber> Road Dirt"
roaddirt_training_pattern_1 = re.compile(
    rf"^(?P<season>Training)\s+-\s+(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Road Dirt)$",
    re.IGNORECASE)

    # -------- Scuba Diving ---------- #
# Pattern training: "Training - <mapnumber> Scuba Diving"
scubadiving_training_pattern_1 = re.compile(
    rf"^(?P<season>Training)\s+-\s+(?P<mapnumber>\d{{1,2}})\s+(?P<alteration_mix>Scuba Diving)$",
    re.IGNORECASE)






ALL_PATTERNS = [
    dirt_seasonal_pattern_1, dirt_training_pattern_1, dirt_weeklyshorts_pattern_1, 
    fastmagnet_seasonal_pattern_1, fastmagnet_seasonal_pattern_2, fastmagnet_seasonal_pattern_3, fastmagnet_training_pattern_1, 
    flooded_seasonal_pattern_1, flooded_seasonal_pattern_2, flooded_training_pattern_1, flooded_spring2020_pattern_1, flooded_discovery_pattern_1,
    grass_seasonal_pattern_1, grass_training_pattern_2, grass_totd_pattern_1,
    ice_seasonal_pattern_1, ice_seasonal_pattern_2, ice_seasonal_pattern_3, ice_training_pattern_1, ice_spring2020_pattern_1, ice_discovery_pattern_1, ice_totd_pattern_1, ice_weeklyshorts_pattern_1, 
    magnet_seasonal_pattern_1, magnet_training_pattern_2, magnet_spring2020_pattern_1, magnet_discovery_pattern_1, magnet_totd_pattern_1, magnet_totd_pattern_2, magnet_weeklyshorts_pattern_1, 
    mixed_seasonal_pattern_1, mixed_training_pattern_1, mixed_training_pattern_2, mixed_weeklyshorts_pattern_1, 
    penalty_seasonal_pattern_1, penalty_training_pattern_1, penalty_weeklyshorts_pattern_1, 
    plastic_seasonal_pattern_1, plastic_training_pattern_1, plastic_training_pattern_2, plastic_spring2020_pattern_1, plastic_discovery_pattern_1, plastic_discovery_pattern_2, plastic_weeklyshorts_pattern_1, 
    road_seasonal_pattern_1, road_seasonal_pattern_2, road_seasonal_pattern_3, road_training_pattern_1, roadasphalt_seasonal_pattern_1, roadtech_seasonal_pattern_1, road_weeklyshorts_pattern_1, 
    wood_seasonal_pattern_1, wood_training_pattern_1, wood_training_pattern_2, wood_spring2020_pattern_1, wood_discovery_pattern_1, wood_totd_pattern_1, wood_weeklyshorts_pattern_1,
    bobsleigh_seasonal_pattern_1, bobsleigh_seasonal_pattern_2, bobsleigh_seasonal_pattern_3, bobsleigh_training_pattern_1,
    pipe_seasonal_pattern_1,
    sausage_seasonal_pattern_1, sausage_training_pattern_2,
    slottrack_seasonal_pattern_1,
    surfaceless_seasonal_pattern_1, surfaceless_training_pattern_1, surfaceless_training_pattern_16171819, surfaceless_weeklyshorts_pattern_1, 
    underwater_seasonal_pattern_1, underwater_seasonal_pattern_2, underwater_training_pattern_1, underwater_spring2020_pattern_1, underwater_discovery_pattern_1, underwater_discovery_pattern_2, underwater_discovery_pattern_3, underwater_totd_pattern_1, underwater_weeklyshorts_pattern_1, underwater_weeklyshorts_pattern_2, 
    
    antibooster_seasonal_pattern_1,
    boosterless_seasonal_pattern_1, boosterless_seasonal_pattern_2, boosterless_training_pattern_1, boosterless_spring2020_pattern_1,
    broken_seasonal_pattern_1,
    cleaned_seasonal_pattern_1,
    cruisecontrol_seasonal_pattern_1, cruisecontrol_seasonal_pattern_2, cruisecontrol_weeklyshorts_pattern_1, 
    cruiseeffects_seasonal_pattern_1, cruiseeffects_training_pattern_2,
    fast_seasonal_pattern_1, fast_seasonal_pattern_2, 
    fragile_seasonal_pattern_1, fragile_seasonal_pattern_2, fragile_seasonal_pattern_3, fragile_seasonal_pattern_4, fragile_training_pattern_1,
    fullfragile_seasonal_pattern_1,
    freewheel_seasonal_pattern_1, freewheel_training_pattern_1, freewheel_spring2020_pattern_1, 
    glider_seasonal_pattern_1,
    nobrakes_seasonal_pattern_1, nobrakes_seasonal_pattern_2,
    noeffects_seasonal_pattern_1, 
    nogrip_seasonal_pattern_1, nogrip_seasonal_pattern_2, nogrip_seasonal_pattern_3, nogrip_seasonal_pattern_4, 
    nosteering_seasonal_pattern_1, nosteering_training_pattern_1, nosteering_weeklyshorts_pattern_1, 
    randomdankness_seasonal_pattern_1, randomdankness_training_pattern_1,
    randomeffects_seasonal_pattern_1, randomeffects_seasonal_pattern_2,
    reactor_seasonal_pattern_1,
    reactordown_seasonal_pattern_1, reactordown_seasonal_pattern_2,
    redeffects_seasonal_pattern_1, redeffects_training_pattern_1,
    rngboosters_seasonal_pattern_1, rngboosters_spring2020_pattern_1,
    slowmo_seasonal_pattern_1, slowmo_seasonal_pattern_2, slowmo_seasonal_pattern_3, slowmo_seasonal_pattern_4, slowmo_seasonal_pattern_5, slowmo_seasonal_pattern_6, 
    wetwheels_seasonal_pattern_1,
    worntires_seasonal_pattern_1,
    
    oneback_seasonal_pattern_1, oneback_seasonal_pattern_2, oneback_seasonal_pattern_3, oneback_seasonal_pattern_4, oneback_seasonal_pattern_5, oneback_training_pattern_1, oneforward_seasonal_pattern_1, oneforward_training_pattern_1, oneforward_spring2020_pattern_1, oneforward_totd_pattern_1, oneforward_totd_pattern_2,
    onedown_seasonal_pattern_1, onedown_training_pattern_1, onedown_spring2020_pattern_1, onedown_discovery_pattern_1, onedown_totd_pattern_1, onedown_weeklyshorts_pattern_1, 
    oneleft_seasonal_pattern_1, oneleft_seasonal_pattern_2, oneright_seasonal_pattern_1, oneright_seasonal_pattern_2,
    oneup_seasonal_pattern_1, oneup_seasonal_pattern_2, oneup_seasonal_pattern_3, oneup_seasonal_pattern_4, oneup_seasonal_pattern_5, oneup_training_pattern_1, oneup_training_pattern_2, oneup_spring2020_pattern_1, oneup_discovery_pattern_1, oneup_totd_pattern_1,
    twoup_seasonal_pattern_1,
    betterreverse_seasonal_pattern_1, betterreverse_seasonal_pattern_2, betterreverse_seasonal_pattern_3,
    cp1isend_seasonal_pattern_1, cp1isend_seasonal_pattern_2, cp1isend_seasonal_pattern_3, cp1isend_training_pattern_1, cp1isend_training_pattern_2, cp1isend_spring2020_pattern_1, cp1isend_totd_pattern_1, cp1isend_totd_pattern_2, 
    floorfin_seasonal_pattern_1, floorfin_weeklyshorts_pattern_1, 
    groundclippers_seasonal_pattern_1, groundclippers_seasonal_pattern_2, 
    inclined_seasonal_pattern_1, inclined_seasonal_pattern_2, 
    manslaughter_seasonal_pattern_1,
    nogear5_seasonal_pattern_1,
    podium_seasonal_pattern_1, podium_competition_pattern_1,
    puzzle_seasonal_pattern_1, puzzle_training_pattern_1,
    reverse_seasonal_pattern_1, reverse_seasonal_pattern_2, reverse_training_pattern_1, reverse_spring2020_pattern_1, reverse_spring2020_pattern_2, reverse_discovery_pattern_1, reverse_totd_pattern_1, reverse_totd_pattern_2, reverse_weeklyshorts_pattern_1, 
    roofing_seasonal_pattern_1, roofing_seasonal_pattern_2,
    short_seasonal_pattern_1, short_seasonal_pattern_2, short_seasonal_pattern_3, short_seasonal_pattern_4, short_training_pattern_1, short_spring2020_pattern_1,
    skyfinish_seasonal_pattern_1, skyfinish_seasonal_pattern_2, skyfinish_seasonal_pattern_3, skyfinish_spring2020_pattern_1, skyfinish_totd_pattern_1,
    thereandback_seasonal_pattern_1, thereandback_seasonal_pattern_2, thereandback_training_pattern_1,
    yeptreepuzzle_seasonal_pattern_1,
    
    stadium_seasonal_pattern_1, stadium_seasonal_pattern_2, stadium_discovery_pattern_1, stadium_discovery_pattern_2, stadium_totd_pattern_1, stadium_weeklyshorts_pattern_1, 
    stadiumtothetop_seasonal_pattern_1, stadiumtothetop_weeklyshorts_pattern_1, 
    stadiumunderwater_seasonal_pattern_1,
    stadiumwetplastic_seasonal_pattern_1,
    stadiumwetwood_seasonal_pattern_1,
    snow_seasonal_pattern_1, snow_seasonal_pattern_2, snow_seasonal_pattern_3, snow_training_pattern_1, snow_discovery_pattern_1, snow_totd_pattern_1, snow_totd_pattern_2, snow_weeklyshorts_pattern_1, 
    snowcarswitch_seasonal_pattern_1, snowcarswitch_totd_pattern_1, snowcarswitch_totd_pattern_2, snowcarswitch_totd_pattern_3, snowcarswitch_totd_pattern_4, snowcarswitch_totd_pattern_5, 
    snowcheckpointless_seasonal_pattern_1, snowcheckpointless_seasonal_pattern_2,
    snowice_seasonal_pattern_1,
    snowpuzzle_seasonal_pattern_1,
    snowtothetop_seasonal_pattern_1, snowtothetop_weeklyshorts_pattern_1, 
    snowunderwater_seasonal_pattern_1, snowunderwater_seasonal_pattern_2, snowunderwater_seasonal_pattern_3, snowunderwater_training_pattern_1, snowunderwater_discovery_pattern_1, snowunderwater_discovery_pattern_2, snowunderwater_totd_pattern_1, snowunderwater_weeklyshorts_pattern_1, snowunderwater_weeklyshorts_pattern_2, 
    snowwetplastic_seasonal_pattern_1,
    snowwood_seasonal_pattern_1, snowwood_training_pattern_1, snowwood_training_pattern_2124,
    rally_seasonal_pattern_1, rally_seasonal_pattern_2, rally_training_pattern_1, rally_totd_pattern_1,
    rallycarswitch_seasonal_pattern_1, rallycarswitch_totd_pattern_1, rallycarswitch_totd_pattern_2, rallycarswitch_totd_pattern_3, rallycarswitch_totd_pattern_4, rallycarswitch_totd_pattern_5, rallycarswitch_totd_pattern_6,
    rallycp1isend_seasonal_pattern_1, rallycp1isend_seasonal_pattern_2, rallycp1isend_spring2020_pattern_1,
    rallyice_seasonal_pattern_1,
    rallytothetop_seasonal_pattern_1, rallytothetop_weeklyshorts_pattern_1, 
    rallyunderwater_seasonal_pattern_1, rallyunderwater_seasonal_pattern_2, rallyunderwater_training_pattern_1, rallyunderwater_discovery_pattern_1, 
    desert_seasonal_pattern_1, desert_seasonal_pattern_2, desert_seasonal_pattern_3, desert_seasonal_pattern_4, desert_training_pattern_1, desert_spring2020_pattern_1, desert_discovery_pattern_1, desert_totd_pattern_1,
    desertantiboost_seasonal_pattern_1, desertantiboost_discovery_pattern_1, desertantiboost_weeklyshorts_pattern_1, 
    desertcarswitch_seasonal_pattern_1, desertcarswitch_totd_pattern_1, desertcarswitch_totd_pattern_2, desertcarswitch_totd_pattern_3, desertcarswitch_totd_pattern_4, 
    desertice_seasonal_pattern_1,
    deserticyredreactordown_seasonal_pattern_1,
    deserttothetop_seasonal_pattern_1, deserttothetop_weeklyshorts_pattern_1,
    desertunderwater_seasonal_pattern_1, desertunderwater_seasonal_pattern_2, desertunderwater_training_pattern_1, desertunderwater_discovery_pattern_1, desertunderwater_weeklyshorts_pattern_1, 
    desertreverse_seasonal_pattern_1, desertreverse_seasonal_pattern_2, 
    allcars_seasonal_pattern_1,
    allcarswitch_seasonal_pattern_1,

    race_seasonal_pattern_1, race_discovery_pattern_1, race_discovery_pattern_2, race_discovery_pattern_3, 
    stunt_seasonal_pattern_1,
    platform_seasonal_pattern_1,
    
    checkpointlessreverse_seasonal_pattern_1, checkpointlessreverse_seasonal_pattern_2, checkpointlessreverse_seasonal_pattern_3, checkpointlessreverse_seasonal_pattern_4, checkpointlessreverse_spring2020_pattern_1,
    deettothetop_seasonal_pattern_1,
    icereverse_seasonal_pattern_1, icereverse_seasonal_pattern_2,
    icereversereactor_seasonal_pattern_1, reactor_training_pattern_1, reactor_training_pattern_2,
    iceshort_seasonal_pattern_1,
    magnetreverse_seasonal_pattern_1,
    plasticreverse_seasonal_pattern_1, plasticreverse_seasonal_pattern_2,
    reverseskyfinish_seasonal_pattern_1, reverseskyfinish_seasonal_pattern_2, reverseskyfinish_seasonal_pattern_3,
    sw2u1lcpuf2d1r_seasonal_pattern_1, 
    underwaterreverse_seasonal_pattern_1, underwaterreverse_seasonal_pattern_2, underwaterreverse_seasonal_pattern_3, underwaterreverse_training_pattern_1,
    wetplastic_seasonal_pattern_1, wetplastic_training_pattern_1, wetplastic_training_pattern_2, wetplastic_weeklyshorts_pattern_1, 
    wetwood_seasonal_pattern_1, wetwood_training_pattern_1, wetwood_training_pattern_2, wetwood_spring2020_pattern_1, wetwood_totd_pattern_1, wetwood_weeklyshorts_pattern_1, wetwoodyrd_seasonal_pattern_2, wetwoodrrd_seasonal_pattern_3, 
    weticywood_seasonal_pattern_1, weticywood_seasonal_pattern_2, weticywood_seasonal_pattern_3, weticywood_seasonal_pattern_4, weticywood_training_pattern_1, weticywood_training_pattern_2, weticywood_training_pattern_3, weticywood_training_pattern_4, weticywood_training_pattern_5, weticywood_spring2020_pattern_1, weticywood_discovery_pattern_1, weticywood_discovery_pattern_2, weticywood_discovery_pattern_3, weticywood_totd_pattern_1, weticywood_totd_pattern_2, weticywood_weeklyshorts_pattern_1, 
    weticyplastic_seasonal_pattern_1, weticyplastic_training_pattern_1, weticyplastic_training_pattern_2, weticyplastic_totd_pattern_1, weticyplastic_discovery_pattern_1, weticyplastic_weeklyshorts_pattern_1, 
    yeetmaxup_seasonal_pattern_1,
    yeetpuzzle_seasonal_pattern_1, yeetpuzzle_training_pattern_1, yeetrandompuzzle_seasonal_pattern_1,
    yeetreverse_seasonal_pattern_1,
    
    # xxbut_seasonal_pattern_1,
    flat_seasonal_pattern_1, flat_seasonal_pattern_2, flat_seasonal_pattern_3, flat_training_pattern_1, flat_training_pattern_2,
    a08_seasonal_pattern_1,
    backwards_seasonal_pattern_1,
    boss_seasonal_pattern_1, boss_seasonal_pattern_2, boss_seasonal_pattern_3,
    bumper_seasonal_pattern_1, bumper_seasonal_pattern_2, bumper_training_pattern_2,
    # Camera
    blind_seasonal_pattern_1, blind_seasonal_pattern_2, blind_seasonal_pattern_3, blind_training_pattern_1,
    egocentrism_seasonal_pattern_1,
    replay_seasonal_pattern_1,
    #
    ngolo_seasonal_pattern_1, ngolo_seasonal_pattern_2,
    checkpoin_t_seasonal_pattern_1, checkpoin_t_seasonal_pattern_2, checkpoin_t_seasonal_pattern_3,
    colourcombined_seasonal_pattern_1, colourcombined_training_pattern_1,
    checkpointboostswap_seasonal_pattern_1, checkpointboostswap_training_pattern_1, checkpointboostswap_spring2020_pattern_1,
    checkpoint1kept_seasonal_pattern_1,
    checkpointfull_seasonal_pattern_1, checkpointfull_seasonal_pattern_2, checkpointfull_training_pattern_1, checkpointfull_weeklyshorts_pattern_1, checkpointfull_weeklyshorts_pattern_2, 
    checkpointless_seasonal_pattern_1, checkpointless_seasonal_pattern_2, checkpointless_training_pattern_1, checkpointless_training_pattern_2, checkpointless_training_pattern_3, checkpointless_spring2020_pattern_1, checkpointless_spring2020_pattern_2, checkpointless_discovery_pattern_1, checkpointless_totd_pattern_1, checkpointless_totd_pattern_2, checkpointless_totd_pattern_3, checkpointless_totd_pattern_4, checkpointless_totd_pattern_5, checkpointless_weeklyshorts_pattern_1, 
    checkpointlink_seasonal_pattern_1,
    checkpointsrotated90_seasonal_pattern_1, checkpointsrotated90_seasonal_pattern_2, checkpointsrotated90_seasonal_pattern_3, gotrotated_seasonal_pattern_1,
    dragonyeet_seasonal_pattern_1,
    earthquake_seasonal_pattern_1, earthquake_training_pattern_1,
    extracheckpoint_seasonal_pattern_1,
    flipped_seasonal_pattern_1, flipped_seasonal_pattern_2, flipped_weeklyshorts_pattern_1, 
    holes_seasonal_pattern_1, holes_training_pattern_1, holes_weeklyshorts_pattern_1, 
    invisible_seasonal_pattern_1, invisible_training_pattern_1,
    lunatic_seasonal_pattern_1, lunatic_seasonal_pattern_2,
    minirpg_seasonal_pattern_1, minirpg_seasonal_pattern_2,
    mirrored_seasonal_pattern_1, mirrored_seasonal_pattern_2, mirrored_training_pattern_1,
    noitems_seasonal_pattern_1,
    poolhunters_seasonal_pattern_1, poolhunters_seasonal_pattern_2, poolhunters_seasonal_pattern_3, poolhunters_seasonal_pattern_4, 
    random_seasonal_pattern_1,
    ringcheckpoint_seasonal_pattern_1, ringcheckpoint_seasonal_pattern_2, ringcheckpoint_seasonal_pattern_3, ringcheckpoint_seasonal_pattern_4, ringcheckpoint_training_pattern_1,
    sectionsjoined_seasonal_pattern_1, sectionsjoined_seasonal_pattern_2, sectionsjoined_seasonal_pattern_3, sectionsjoined_seasonal_pattern_4, 
    selectdel_seasonal_pattern_1,
    speedlimit_seasonal_pattern_1, speedlimit_seasonal_pattern_2, speedlimit_seasonal_pattern_3,
    start1down_seasonal_pattern_1,
    supersized_seasonal_pattern_1, supersized_seasonal_pattern_2, supersized_seasonal_pattern_3, supersized_seasonal_pattern_4, supersized_seasonal_pattern_5, supersized_training_pattern_1, 
    straighttothefinish_seasonal_pattern_1, straighttothefinish_seasonal_pattern_2, straighttothefinish_seasonal_pattern_3, straighttothefinish_seasonal_pattern_4, straighttothefinish_training_pattern_1, straighttothefinish_spring2020_pattern_1, straighttothefinish_discovery_pattern_1, straighttothefinish_totd_pattern_1, straighttothefinish_weeklyshorts_pattern_1, 
    stuntmode_seasonal_pattern_1, stuntmode_seasonal_pattern_2,
    symmetrical_seasonal_pattern_1,
    tilted_seasonal_pattern_1, tilted_seasonal_pattern_2, tilted_training_pattern_1,
    yeet_seasonal_pattern_1, yeet_training_pattern_1, yeet_spring2020_pattern_1, yeet_discovery_pattern_1, yeet_totd_pattern_1,
    yeetdown_seasonal_pattern_1, yeetdown_seasonal_pattern_2, yeetdown_seasonal_pattern_3, 
    
    easymode_competition_pattern_1,
    
    # Other
    chinese_seasonal_pattern_1, chinese_training_pattern_1,
    all1up_seasonal_pattern_1,
    
    # Sorted as only training (as of rn)
    wallmartmini_training_pattern_1,
    staircase_training_pattern_1,
    icereactor_training_pattern_1,
    bettermixed_training_pattern_1,
    nocut_training_pattern_1,
    platform_training_pattern_1,
    roaddirt_training_pattern_1,
    scubadiving_training_pattern_1
]