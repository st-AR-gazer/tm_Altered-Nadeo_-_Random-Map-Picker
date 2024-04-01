void LoadMapFromStorageObject() {
    string mapUrl = FetchRandomMapUrl();

    if (mapUrl.Length == 0) {
        log("Failed to get map URL from storage objects. URL is: '" + mapUrl + "'", LogLevel::Error, 5); // mapUrl will always be empty xdd
        NotifyWarn("Failed to get map URL from storage objects. Please try and use with UID in General Alteratin settings.");
        return;
    }

    PlayMap(mapUrl);
}

Json::Value LoadMapsFromConsolidatedFile() {
    string filePath = IO::FromStorageFolder("Data/consolidated_maps.json");
    
    if (!IO::FileExists(filePath)) {
        log("Consolidated map file does not exist. Creating a new one with dummy data: " + filePath, LogLevel::Error, 17);
        
        Json::Value dummyMap = Json::Object();
        dummyMap["fileUrl"] = "dummy_url";

        
        Json::Value mapArray = Json::Array();
        mapArray.Add(dummyMap);

        
        Json::ToFile(filePath, mapArray);

        
        return mapArray;
    }
    
    Json::Value maps = Json::FromFile(filePath);
    return maps;
}

string FetchRandomMapUrl() {
    Json::Value allMaps = LoadMapsFromConsolidatedFile();

    if (allMaps.Length == 1 && allMaps[0].HasKey("fileUrl") && allMaps[0]["fileUrl"] == "dummy_url") {
        log("Dummy map data found. No real maps available.", LogLevel::Error, 41);
        return "";
    }
    
    array<Json::Value@> seasonFilteredMaps;
    array<Json::Value@> finalFilteredMaps;

    // Filter out 'season' and 'year' settings
    for (uint i = 0; i < allMaps.Length; ++i) {
        Json::Value map = allMaps[i];
        
        if (MatchesSeasonalSettings(map)) {
            seasonFilteredMaps.InsertLast(map);
        }
    }
    for (uint i = 0; i < allMaps.Length; ++i) {
        Json::Value map = allMaps[i];
        
        if (MatchesSeasonalSettings(map)) {
            seasonFilteredMaps.InsertLast(map);
        }
    }

    // Filter 'alteration' settings
    for (uint i = 0; i < seasonFilteredMaps.Length; ++i) {
        Json::Value map = seasonFilteredMaps[i];
        
        if (MatchesAlterationSettings(map)) {
            finalFilteredMaps.InsertLast(map);
        }
    }

    if (finalFilteredMaps.IsEmpty() && NoAlterationSettingActive()) {
        finalFilteredMaps = seasonFilteredMaps;
    }

    // Select random from filtered
    if (!finalFilteredMaps.IsEmpty()) {
        uint randomIndex = Math::Rand(0, finalFilteredMaps.Length);
        Json::Value@ selectedMap = finalFilteredMaps[randomIndex];
        
        if (selectedMap !is null && selectedMap.HasKey("fileUrl") && selectedMap["fileUrl"].GetType() == Json::Type::String) {
            return string(selectedMap["fileUrl"]);
        }
    }

    log("No maps match the selected criteria", LogLevel::Error, 87);
    return "";
}

bool MatchesSeasonalSettings(Json::Value map) {
    
    if (IsUsing_Spring2020Maps && (map["season"] == "Spring" || map["season"] == "spring") && map["year"] == "2020") return true;
    if (IsUsing_Summer2020Maps && (map["season"] == "Summer" || map["season"] == "summer") && map["year"] == "2020") return true;
    if (IsUsing_Fall2020Maps   && (map["season"] == "Fall"   || map["season"] == "fall")   && map["year"] == "2020") return true;
    if (IsUsing_Spring2021Maps && (map["season"] == "Spring" || map["season"] == "spring") && map["year"] == "2021") return true;
    if (IsUsing_Summer2021Maps && (map["season"] == "Summer" || map["season"] == "summer") && map["year"] == "2021") return true;
    if (IsUsing_Fall2021Maps   && (map["season"] == "Fall"   || map["season"] == "fall")   && map["year"] == "2021") return true;
    if (IsUsing_Spring2022Maps && (map["season"] == "Spring" || map["season"] == "spring") && map["year"] == "2022") return true;
    if (IsUsing_Summer2022Maps && (map["season"] == "Summer" || map["season"] == "summer") && map["year"] == "2022") return true;
    if (IsUsing_Fall2022Maps   && (map["season"] == "Fall"   || map["season"] == "fall")   && map["year"] == "2022") return true;
    if (IsUsing_Spring2023Maps && (map["season"] == "Spring" || map["season"] == "spring") && map["year"] == "2023") return true;
    if (IsUsing_Summer2023Maps && (map["season"] == "Summer" || map["season"] == "summer") && map["year"] == "2023") return true;
    if (IsUsing_Fall2023Maps   && (map["season"] == "Fall"   || map["season"] == "fall")   && map["year"] == "2023") return true;
    if (IsUsing_Spring2024Maps && (map["season"] == "Spring" || map["season"] == "spring") && map["year"] == "2024") return true;
    if (IsUsing_Summer2024Maps && (map["season"] == "Summer" || map["season"] == "summer") && map["year"] == "2024") return true;
    if (IsUsing_Fall2024Maps   && (map["season"] == "Fall"   || map["season"] == "fall")   && map["year"] == "2024") return true;
    if (IsUsing_Spring2025Maps && (map["season"] == "Spring" || map["season"] == "spring") && map["year"] == "2025") return true;
    if (IsUsing_Summer2025Maps && (map["season"] == "Summer" || map["season"] == "summer") && map["year"] == "2025") return true;

    if (IsUsing_AllSnowDiscovery   && map["season"] == "AllSnowDiscovery")   return true;
    if (IsUsing_AllRallyDiscovery  && map["season"] == "AllRallyDiscovery")  return true;
    if (IsUsing_AllDesertDiscovery && map["season"] == "AllDesertDiscovery") return true;

    if (IsUsing__AllOfficialCompetitions && map["season"] == "!AllOfficialCompetitions") return true;
    if (IsUsing_AllOfficialCompetitions  && map["season"] == "AllOfficialCompetitions")  return true;

    if (IsUsing_AllTOTD && map["season"] == "AllTOTD") return true;

    return false;
}

bool MatchesAlterationSettings(Json::Value map) {
    if (IsUsing_Dirt                         && map["alteration"] == "Dirt") return true;
    if (IsUsing_Fast_Magnet                  && map["alteration"] == "Fast Mangnet") return true;
    if (IsUsing_Flooded                      && map["alteration"] == "Flooded") return true;
    if (IsUsing_Grass                        && map["alteration"] == "Grass") return true;
    if (IsUsing_Ice                          && map["alteration"] == "Ice") return true;
    if (IsUsing_Magnet                       && map["alteration"] == "Magnet") return true;
    if (IsUsing_Mixed                        && map["alteration"] == "Mixed") return true;
    if (IsUsing_Better_Mixed                 && map["alteration"] == "Better Mixed") return true;
    if (IsUsing_Penalty                      && map["alteration"] == "Penalty") return true;
    if (IsUsing_Plastic                      && map["alteration"] == "Plastic") return true;
    if (IsUsing_Road                         && map["alteration"] == "Road") return true;
    if (IsUsing_Wood                         && map["alteration"] == "Wood") return true;
    if (IsUsing_Bobsleigh                    && map["alteration"] == "Bobsleigh") return true;
    if (IsUsing_Pipe                         && map["alteration"] == "Pipe") return true;
    if (IsUsing_Sausage                      && map["alteration"] == "Sausage") return true;
    if (IsUsing_Underwater                   && map["alteration"] == "Underwater") return true;

    if (IsUsing_Cruise                       && map["alteration"] == "Cruise") return true;
    if (IsUsing_Fragile                      && map["alteration"] == "Fragile") return true;
    if (IsUsing_Full_Fragile                 && map["alteration"] == "Full Fragile") return true;
    if (IsUsing_Freewheel                    && map["alteration"] == "Freewheel") return true;
    if (IsUsing_Glider                       && map["alteration"] == "Glider") return true;
    if (IsUsing_No_Brakes                    && map["alteration"] == "No Brakes") return true;
    if (IsUsing_No_Effects                   && map["alteration"] == "No Effects") return true;
    if (IsUsing_No_Grip                      && map["alteration"] == "No Grip") return true;
    if (IsUsing_No_Steer                     && map["alteration"] == "No Steer") return true;
    if (IsUsing_Random_Dankness              && map["alteration"] == "Random Dankness") return true;
    if (IsUsing_Random_Effects               && map["alteration"] == "Random Effects") return true;
    if (IsUsing_Reactor                      && map["alteration"] == "Reactor") return true;
    if (IsUsing_Reactor_Down                 && map["alteration"] == "Reactor Down") return true;
    if (IsUsing_Slowmo                       && map["alteration"] == "Slowmo") return true;
    if (IsUsing_Wet_Wheels                   && map["alteration"] == "Wet Wheels") return true;
    if (IsUsing_Worn_Tires                   && map["alteration"] == "Worn Tires") return true;

    if (IsUsing_1Down                        && map["alteration"] == "1 Down") return true;
    if (IsUsing_1Back                        && map["alteration"] == "1 Back") return true;
    if (IsUsing_1Left                        && map["alteration"] == "1 Left") return true;
    if (IsUsing_1Right                       && map["alteration"] == "1 Right") return true;
    if (IsUsing_1Up                          && map["alteration"] == "1 Up") return true;
    if (IsUsing_2Up                          && map["alteration"] == "2 Up") return true;
    if (IsUsing_Better_Reverse               && map["alteration"] == "Better Reverse") return true;
    if (IsUsing_CP1_is_End                   && map["alteration"] == "CP1 is End") return true;
    if (IsUsing_Floor_Fin                    && map["alteration"] == "Floor Fin") return true;
    if (IsUsing_Inclined                     && map["alteration"] == "Inclined") return true;
    if (IsUsing_Manslaughter                 && map["alteration"] == "Manslaughter") return true;
    if (IsUsing_No_Gear_5                    && map["alteration"] == "No Gear 5") return true;
    if (IsUsing_Podium                       && map["alteration"] == "Podium") return true;
    if (IsUsing_Puzzle                       && map["alteration"] == "Puzzle") return true;
    if (IsUsing_Reverse                      && map["alteration"] == "Reverse") return true;
    if (IsUsing_Roofing                      && map["alteration"] == "Roofing") return true;
    if (IsUsing_Short                        && map["alteration"] == "Short") return true;
    if (IsUsing_Sky_is_the_Finish            && map["alteration"] == "Sky is the Finish") return true;
    if (IsUsing_There_and_Back_Boomerang     && map["alteration"] == "There and Back_Boomerang") return true;
    if (IsUsing_YEP_Tree_Puzzle              && map["alteration"] == "YEP Tree Puzzle") return true;

    if (IsUsing_Stadium_                     && map["alteration"] == "[Stadium]") return true;
    if (IsUsing_Stadium_Wet_Wood             && map["alteration"] == "[Stadium] Wet Wood") return true;
    if (IsUsing_Snow_                        && map["alteration"] == "[Snow]") return true;
    if (IsUsing_Snow_Carswitch               && map["alteration"] == "[Snow] Carswitch") return true;
    if (IsUsing_Snow_Checkpointless          && map["alteration"] == "[Snow] Checkpointless") return true;
    if (IsUsing_Snow_Icy                     && map["alteration"] == "[Snow] Icy") return true;
    if (IsUsing_Snow_Underwater              && map["alteration"] == "[Snow] Underwater") return true;
    if (IsUsing_Snow_Wet_Plastic             && map["alteration"] == "[Snow] Wet-Plastic") return true;
    if (IsUsing_Snow_Wood                    && map["alteration"] == "[Snow] Wood") return true;
    if (IsUsing_Rally_                       && map["alteration"] == "[Rally]") return true;
    if (IsUsing_Rally_Carswitch              && map["alteration"] == "[Rally] Carswitch") return true;
    if (IsUsing_Rally_CP1_is_End             && map["alteration"] == "[Rally] CP1 is End") return true;
    if (IsUsing_Rally_Underwater             && map["alteration"] == "[Rally] Underwater") return true;
    if (IsUsing_Rally_Icy                    && map["alteration"] == "[Rally] Icy") return true;

    if (IsUsing_Checkpointless_Reverse       && map["alteration"] == "Checkpointless Reverse") return true;
    if (IsUsing_Ice_Reverse                  && map["alteration"] == "Ice Reverse") return true;
    if (IsUsing_Ice_Reverse_Reactor          && map["alteration"] == "Ice Reverse Reactor") return true;
    if (IsUsing_Ice_Short                    && map["alteration"] == "Ice Short") return true;
    if (IsUsing_Magnet_Reverse               && map["alteration"] == "Magnet Reverse") return true;
    if (IsUsing_Plastic_Reverse              && map["alteration"] == "Plastic Reverse") return true;
    if (IsUsing_Sky_is_the_Finish_Reverse    && map["alteration"] == "Sky is the Finish Reverse") return true;
    if (IsUsing_sw2u1l_cpu_f2d1r             && map["alteration"] == "sw2u1l-cpu-f2d1r") return true;
    if (IsUsing_Underwater_Reverse           && map["alteration"] == "Underwater Reverse") return true;
    if (IsUsing_Wet_Plastic                  && map["alteration"] == "Wet Plastic") return true;
    if (IsUsing_Wet_Wood                     && map["alteration"] == "Wet Wood") return true;
    if (IsUsing_Wet_Icy_Wood                 && map["alteration"] == "Wet Icy Wood") return true;
    if (IsUsing_Yeet_Max_Up                  && map["alteration"] == "YEET Max-Up") return true;
    if (IsUsing_YEET_Puzzle                  && map["alteration"] == "YEET Puzzle") return true;
    if (IsUsing_YEET_Random_Puzzle           && map["alteration"] == "YEET Random Puzzle") return true;
    if (IsUsing_YEET_Reverse                 && map["alteration"] == "YEET Reverse") return true;

    if (IsUsing_XX_But                       && map["alteration"] == "XX-But") return true;
    if (IsUsing_Flat_2D                      && map["alteration"] == "Flat_2D") return true;
    if (IsUsing_A08                          && map["alteration"] == "A08") return true;
    if (IsUsing_Antibooster                  && map["alteration"] == "Antibooster") return true;
    if (IsUsing_Backwards                    && map["alteration"] == "Backwards") return true;
    if (IsUsing_Boosterless                  && map["alteration"] == "Boosterless") return true;
    if (IsUsing_BOSS                         && map["alteration"] == "BOSS") return true;
    if (IsUsing_Broken                       && map["alteration"] == "Broken") return true;
    if (IsUsing_Bumper                       && map["alteration"] == "Bumper") return true;
    if (IsUsing_Ngolo_Cacti                  && map["alteration"] == "Ngolo_Cacti") return true;
    if (IsUsing_Checkpoin_t                  && map["alteration"] == "Checkpoin't") return true;
    if (IsUsing_Cleaned                      && map["alteration"] == "Cleaned") return true;
    if (IsUsing_Colours_Combined             && map["alteration"] == "Colours Combined") return true;
    if (IsUsing_CP_Boost                     && map["alteration"] == "CP_Boost") return true;
    if (IsUsing_CP1_Kept                     && map["alteration"] == "CP1 Kept") return true;
    if (IsUsing_CPfull                       && map["alteration"] == "CPfull") return true;
    if (IsUsing_Checkpointless               && map["alteration"] == "Checkpointless") return true;
    if (IsUsing_CPLink                       && map["alteration"] == "CPLink") return true;
    if (IsUsing_Earthquake                   && map["alteration"] == "Earthquake") return true;
    if (IsUsing_Fast                         && map["alteration"] == "Fast") return true;
    if (IsUsing_Flipped                      && map["alteration"] == "Flipped") return true;
    if (IsUsing_Got_Rotated_CPs_Rotated_90__ && map["alteration"] == "Got Rotated_CPs Rotated 90°") return true;
    if (IsUsing_Holes                        && map["alteration"] == "Holes") return true;
    if (IsUsing_Lunatic                      && map["alteration"] == "Lunatic") return true;
    if (IsUsing_Mini_RPG                     && map["alteration"] == "Mini RPG") return true;
    if (IsUsing_Mirrored                     && map["alteration"] == "Mirrored") return true;
    if (IsUsing_Pool_Hunters                 && map["alteration"] == "Pool Hunters") return true;
    if (IsUsing_Random                       && map["alteration"] == "Random") return true;
    if (IsUsing_Ring_CP                      && map["alteration"] == "Ring CP") return true;
    if (IsUsing_Sections_joined              && map["alteration"] == "Sections Joined") return true;
    if (IsUsing_Select_DEL                   && map["alteration"] == "Select DEL") return true;
    if (IsUsing_Speedlimit                   && map["alteration"] == "Speedlimit") return true;
    if (IsUsing_Start_1_Down                 && map["alteration"] == "Start 1-Down") return true;
    if (IsUsing_Supersized                   && map["alteration"] == "Supersized") return true;
    if (IsUsing_Straight_to_the_Finish       && map["alteration"] == "Straight to the Finish") return true;
    if (IsUsing_Symmetrical                  && map["alteration"] == "Symmetrical") return true;
    if (IsUsing_Tilted                       && map["alteration"] == "Tilted") return true;
    if (IsUsing_YEET                         && map["alteration"] == "YEET") return true;
    if (IsUsing_YEET_Down                    && map["alteration"] == "YEET Down") return true;

 // if (IsUsing_Trainig                      && map["alteration"] == "") return true; // This is in 'season' not 'alteration'
    if (IsUsing_TMGL_Easy                    && map["alteration"] == "TMGL Easy") return true;
 // if (IsUsing__AllOfficialCompetitions     && map["alteration"] == "") return true; // This is in 'season' not 'alteration'
    if (IsUsing_AllOfficialCompetitions      && map["alteration"] == "!AllOfficialCompetitions") return true;
    if (IsUsing_OfficialNadeo                && map["alteration"] == "!OfficialNadeo") return true;
 // if (IsUsing_AllTOTD                      && map["alteration"] == "") return true; // This is in 'season' not 'alteration'

    return false;
}

bool NoSeasonalSettingActive() {
    log("No season is selected, automatically selecting all seasons.", LogLevel::Info, 262);
    NotifyWarn("No season is selected, automatically selecting all seasons.");
    DeselectOrSelectAllSeasons(true);
    return true;
}

bool NoAlterationSettingActive() {
    log("No alteration is selected, automatically selecting all alterations.", LogLevel::Info, 269);
    NotifyWarn("No alteration is selected, automatically selecting all alterations.");
    DeselectOrSelectAllAlterations(true);
    return true;
}
