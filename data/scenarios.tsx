import { Droplets, Radar, Waves, Wind } from "lucide-react";
import type { ReactNode } from "react";
import { ScenarioKey, ScenarioState } from "../types/dashboard";

export const scenarios: ScenarioKey[] = [
  "heavy rainfall",
  "storm surge",
  "sea-level-rise increase",
  "repeated flooding days"
];

export const scenarioIcons: Record<ScenarioKey, ReactNode> = {
  "heavy rainfall": <Droplets className="h-4 w-4" />,
  "storm surge": <Waves className="h-4 w-4" />,
  "sea-level-rise increase": <Wind className="h-4 w-4" />,
  "repeated flooding days": <Radar className="h-4 w-4" />
};

export const mockScenarioData: Record<ScenarioKey, ScenarioState> = {
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
      "[sentinel] Open-Meteo precipitation payload received (8.2 mm/hr)",
      "[simulator.parallel] Running road, drainage, and shelter-route scoring",
      "[simulator.parallel] Scenario heavy_rainfall score aggregate: 0.84",
      "[dispatcher.loop] Verified recommendation consistency against route blockages",
      "[dispatcher.output] Action payload queued: deploy_pumps(zone=south_tampa)"
    ]
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
    ]
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
    ]
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
    ]
  }
};
