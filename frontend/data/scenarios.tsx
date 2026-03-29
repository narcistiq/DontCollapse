import { Droplets, Radar, Waves, Wind, Activity, Tornado } from "lucide-react";
import type { ReactNode } from "react";
import { ScenarioKey, ScenarioState } from "../types/dashboard";

export const scenarios: ScenarioKey[] = [
  "live conditions",
  "heavy rainfall",
  "storm surge",
  "category 5 hurricane",
  "sea-level-rise increase",
  "repeated flooding days"
];

export const scenarioIcons: Record<ScenarioKey, ReactNode> = {
  "live conditions": <Activity className="h-4 w-4" color="#10b981" />,
  "heavy rainfall": <Droplets className="h-4 w-4" />,
  "storm surge": <Waves className="h-4 w-4" />,
  "category 5 hurricane": <Tornado className="h-4 w-4" color="#f43f5e" />,
  "sea-level-rise increase": <Wind className="h-4 w-4" />,
  "repeated flooding days": <Radar className="h-4 w-4" />
};

export const mockScenarioData: Record<ScenarioKey, ScenarioState> = {

  "live conditions": {
    summary: "Monitoring real-time telemetry from Tampa open-data sources. Currently tracking elevated humidity and minor traffic anomalies.",
    score: 32,
    affected: "Tampa Metropolitan Baseline",
    actions: [
      {
        id: "live-1",
        title: "Monitor localized street ponding",
        detail: "Current radar indicates minor buildup along South MacDill Ave.",
        urgency: "stable"
      }
    ],
    logs: [
      "[sentinel] Weather monitoring link active.",
      "[sentinel] Live traffic layer synced.",
      "[simulator] Baseline conditions normal. No cascading triggers.",
      "[dispatcher] Standby mode active."
    ],
    rankedAreas: [
      { name: "Downtown Core", score: 32, reason: "Baseline traffic and standard social variance" },
      { name: "Ybor City", score: 30, reason: "Normal operations" }
    ],
    infrastructureScores: [
      { id: "roads", label: "Roads", score: 30 },
      { id: "power", label: "Power Service Areas", score: 15 },
      { id: "access-routes", label: "Hospital/Shelter Routes", score: 20 }
    ],
    actionPayload: { action: "monitor", coordinates: [] }
  },
  "category 5 hurricane": {
    summary: "Catastrophic damage projected. Mass evacuation required immediately. Storm surge expected to exceed 15+ feet across all coastal boundaries.",
    score: 98,
    affected: "Entire Tampa Coastal Bay Region",
    actions: [
      {
        id: "cat5-1",
        title: "Mandatory Evacuation Execution",
        detail: "Reverse lanes on I-4 and I-75 immediately. Deploy state guard.",
        urgency: "critical"
      },
      {
        id: "cat5-2",
        title: "Hospital Hardening",
        detail: "Transfer critical care patients inland by air immediately.",
        urgency: "critical"
      }
    ],
    logs: [
      "[sentinel] WARNING: Cat 5 Hurricane telemetry injected. Sustained winds >157mph.",
      "[simulator] Catastrophic failure across 90% of Tampa power grids.",
      "[simulator] Bridges compromised: Gandy, Howard Frankland, Courtney Campbell.",
      "[dispatcher] OVERRIDE: Declaring State of Emergency."
    ],
    rankedAreas: [
      { name: "MacDill Air Force Base", score: 100, reason: "Direct strike, complete inundation." },
      { name: "Davis Islands", score: 100, reason: "Unsurvivable storm surge and wind." }
    ],
    infrastructureScores: [
      { id: "power", label: "Power Service Areas", score: 100 },
      { id: "roads", label: "Roads", score: 95 },
      { id: "access-routes", label: "Hospital/Shelter Routes", score: 98 },
      { id: "drainage", label: "Drainage Zones", score: 100 }
    ],
    actionPayload: { action: "mandatory_evacuate", coordinates: [] }
  },

  "heavy rainfall": {
    summary:
      "This area is high risk because road elevation is low, flood exposure is high, and it has poor alternate access.",
    score: 84,
    affected: "South Tampa Flood Basin",
    actions: [
      {
        id: "rain-1",
        title: "Place temporary pumps or barriers here",
        detail: "Deploy to the South Tampa low-grade corridor before the next peak precipitation window.",
        urgency: "critical"
      },
      {
        id: "rain-2",
        title: "Prioritize shelter route hardening",
        detail: "Ensure passable access to General Hospital and Central Shelter with lane-level detours.",
        urgency: "warning"
      }
    ],
    logs: [
      "[sentinel] Local precipitation node payload received (8.2 mm/hr)",
      "[simulator.parallel] Running road, drainage, and shelter-route scoring",
      "[simulator.parallel] Scenario heavy_rainfall score aggregate: 0.84",
      "[dispatcher.loop] Verified recommendation consistency against route blockages",
      "[dispatcher.output] Action payload queued: deploy_pumps(zone=south_tampa)"
    ],
    rankedAreas: [
      {
        name: "South Tampa Flood Basin",
        score: 84,
        reason: "Low elevation and poor alternate corridors"
      },
      {
        name: "East Tampa Drainage Cluster",
        score: 73,
        reason: "Drainage overload under peak rainfall"
      },
      {
        name: "Pinellas Shelter Access Corridor",
        score: 58,
        reason: "Flooded intersections reduce shelter reachability"
      }
    ],
    infrastructureScores: [
      { id: "roads", label: "Roads", score: 82 },
      { id: "intersections", label: "Intersections", score: 79 },
      { id: "drainage", label: "Drainage Zones", score: 86 },
      { id: "power", label: "Power Service Areas", score: 57 },
      { id: "access-routes", label: "Hospital/Shelter Routes", score: 81 }
    ],
    actionPayload: {
      action: "deploy_pumps",
      coordinates: [
        [-82.523, 27.902],
        [-82.511, 27.891]
      ]
    }
  },
  "storm surge": {
    summary:
      "This neighborhood has above-average vulnerability because flooding could block routes to shelters and emergency services.",
    score: 78,
    affected: "Pinellas Shelter Access Corridor",
    actions: [
      {
        id: "surge-1",
        title: "Reinforce this evacuation corridor",
        detail: "Stand up temporary barriers and increase traffic control staffing before landfall.",
        urgency: "warning"
      },
      {
        id: "surge-2",
        title: "Stage backup transport assets",
        detail: "Pre-position high-water vehicles at inland transfer points for shelter access continuity.",
        urgency: "warning"
      }
    ],
    logs: [
      "[sentinel] Marine forecast ingested (surge anomaly +0.8 m)",
      "[simulator.parallel] Simulating shoreline inundation overlap",
      "[simulator.parallel] Surge impact intersects 2 critical routes",
      "[dispatcher.loop] Initial route recommendation conflicted with flood mask",
      "[dispatcher.loop] Corrected plan generated with inland fallback corridor"
    ],
    rankedAreas: [
      {
        name: "Pinellas Shelter Access Corridor",
        score: 78,
        reason: "Coastal surge overlaps evacuation routes"
      },
      {
        name: "South Tampa Flood Basin",
        score: 74,
        reason: "Near-bay inundation spillback risk"
      },
      {
        name: "Westshore Utility Zone",
        score: 62,
        reason: "Power and roadway convergence in low-lying area"
      }
    ],
    infrastructureScores: [
      { id: "roads", label: "Roads", score: 76 },
      { id: "intersections", label: "Intersections", score: 72 },
      { id: "drainage", label: "Drainage Zones", score: 69 },
      { id: "power", label: "Power Service Areas", score: 71 },
      { id: "access-routes", label: "Hospital/Shelter Routes", score: 77 }
    ],
    actionPayload: {
      action: "reinforce_corridor",
      coordinates: [
        [-82.747, 27.902],
        [-82.733, 27.893]
      ]
    }
  },
  "sea-level-rise increase": {
    summary:
      "Long-tail exposure is elevated because recurrent tidal encroachment compounds existing drainage constraints over time.",
    score: 62,
    affected: "East Tampa Drainage Cluster",
    actions: [
      {
        id: "slr-1",
        title: "Improve drainage here",
        detail: "Upgrade basin outflow controls and prioritize pump station modernization in phased work.",
        urgency: "warning"
      },
      {
        id: "slr-2",
        title: "Initiate long-term zoning resilience review",
        detail: "Flag parcel groups for flood-compatible standards and elevated utility requirements.",
        urgency: "stable"
      }
    ],
    logs: [
      "[sentinel] Sea-level baseline offset loaded (+14 in scenario projection)",
      "[simulator.parallel] Recalculating drainage retention thresholds",
      "[simulator.parallel] Chronic stress index increased in 3 urban basins",
      "[dispatcher.loop] Prioritized infrastructure modernization over short-term reroutes",
      "[dispatcher.output] Action payload queued: drainage_upgrade(cluster=east_tampa)"
    ],
    rankedAreas: [
      {
        name: "East Tampa Drainage Cluster",
        score: 62,
        reason: "Chronic tidal backflow pressure"
      },
      {
        name: "South Tampa Flood Basin",
        score: 59,
        reason: "Recurrent minor inundation expansion"
      },
      {
        name: "Central Access Belt",
        score: 52,
        reason: "Declining route reliability over long horizon"
      }
    ],
    infrastructureScores: [
      { id: "roads", label: "Roads", score: 61 },
      { id: "intersections", label: "Intersections", score: 58 },
      { id: "drainage", label: "Drainage Zones", score: 74 },
      { id: "power", label: "Power Service Areas", score: 55 },
      { id: "access-routes", label: "Hospital/Shelter Routes", score: 60 }
    ],
    actionPayload: {
      action: "drainage_upgrade",
      coordinates: [
        [-82.426, 27.963],
        [-82.412, 27.953]
      ]
    }
  },
  "repeated flooding days": {
    summary:
      "Cumulative service disruption risk is rising because repeated closures are reducing reliability for emergency routing.",
    score: 49,
    affected: "General Hospital Access Ring",
    actions: [
      {
        id: "repeat-1",
        title: "Prioritize this neighborhood for evacuation planning",
        detail: "Issue staged movement plans for medically vulnerable households during multi-day events.",
        urgency: "stable"
      },
      {
        id: "repeat-2",
        title: "Improve access to shelters here",
        detail: "Increase wayfinding, signage, and dynamic route messaging around repeat disruption nodes.",
        urgency: "stable"
      }
    ],
    logs: [
      "[sentinel] Historic flood-day sequence loaded (last 90 days)",
      "[simulator.parallel] Measuring repeated closure effects on route reliability",
      "[simulator.parallel] Reliability degradation detected on 4 feeder roads",
      "[dispatcher.loop] Confirmed shelter access remains above minimum threshold",
      "[dispatcher.output] Action payload queued: evacuation_planning(zone=central)"
    ],
    rankedAreas: [
      {
        name: "General Hospital Access Ring",
        score: 49,
        reason: "Multi-day disruption compounds travel-time volatility"
      },
      {
        name: "South Tampa Flood Basin",
        score: 47,
        reason: "Repeat closures impact daily service continuity"
      },
      {
        name: "Pinellas Shelter Access Corridor",
        score: 43,
        reason: "Intermittent accessibility losses"
      }
    ],
    infrastructureScores: [
      { id: "roads", label: "Roads", score: 51 },
      { id: "intersections", label: "Intersections", score: 54 },
      { id: "drainage", label: "Drainage Zones", score: 48 },
      { id: "power", label: "Power Service Areas", score: 41 },
      { id: "access-routes", label: "Hospital/Shelter Routes", score: 53 }
    ],
    actionPayload: {
      action: "evacuation_planning",
      coordinates: [
        [-82.501, 27.958],
        [-82.487, 27.948]
      ]
    }
  }
};
