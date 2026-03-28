"use client";

import { AlertTriangle, Droplets, Hospital, MapPinned, Radar, ShieldAlert, Waves, Wind } from "lucide-react";
import mapboxgl, { GeoJSONSource, Map } from "mapbox-gl";
import { useEffect, useMemo, useRef, useState } from "react";

type ScenarioKey = "heavy rainfall" | "storm surge" | "sea-level-rise increase" | "repeated flooding days";

type ActionTicket = {
  id: string;
  title: string;
  detail: string;
  urgency: "critical" | "warning" | "stable";
};

type ScenarioState = {
  summary: string;
  score: number;
  affected: string;
  actions: ActionTicket[];
  logs: string[];
};

type FeatureCollection = GeoJSON.FeatureCollection<GeoJSON.Geometry, { [name: string]: string | number }>;

const scenarios: ScenarioKey[] = [
  "heavy rainfall",
  "storm surge",
  "sea-level-rise increase",
  "repeated flooding days"
];

const scenarioIcons: Record<ScenarioKey, React.ReactNode> = {
  "heavy rainfall": <Droplets className="h-4 w-4" />,
  "storm surge": <Waves className="h-4 w-4" />,
  "sea-level-rise increase": <Wind className="h-4 w-4" />,
  "repeated flooding days": <Radar className="h-4 w-4" />
};

const mockScenarioData: Record<ScenarioKey, ScenarioState> = {
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

mapboxgl.accessToken = process.env.NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN ?? "";

const severityClass = (score: number) => {
  if (score >= 80) {
    return "text-rose-400 bg-rose-950/50 border-rose-500/50";
  }
  if (score >= 50) {
    return "text-amber-400 bg-amber-950/50 border-amber-500/50";
  }
  return "text-emerald-400 bg-emerald-950/50 border-emerald-500/50";
};

const actionSeverityClass = (urgency: ActionTicket["urgency"]) => {
  if (urgency === "critical") {
    return "text-rose-300 border-rose-500/50 bg-rose-950/20";
  }
  if (urgency === "warning") {
    return "text-amber-300 border-amber-500/50 bg-amber-950/20";
  }
  return "text-emerald-300 border-emerald-500/50 bg-emerald-950/20";
};

export default function DashboardPage() {
  const mapContainerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<Map | null>(null);

  const [activeScenario, setActiveScenario] = useState<ScenarioKey>("heavy rainfall");
  const [isLoadingIntelligence, setIsLoadingIntelligence] = useState(false);
  const [traceLogs, setTraceLogs] = useState<string[]>([]);

  const scenarioState = useMemo(() => mockScenarioData[activeScenario], [activeScenario]);

  useEffect(() => {
    if (!mapContainerRef.current || mapRef.current || !mapboxgl.accessToken) {
      return;
    }

    const map = new mapboxgl.Map({
      container: mapContainerRef.current,
      style: "mapbox://styles/mapbox/dark-v11",
      center: [-82.55, 27.95],
      zoom: 9.2,
      pitch: 38,
      bearing: -16,
      antialias: true
    });

    map.addControl(new mapboxgl.NavigationControl({ showCompass: false }), "top-right");

    map.on("load", async () => {
      const response = await fetch("/data/tampa_data.json");
      const geojson = (await response.json()) as FeatureCollection;

      map.addSource("tampa-zones", { type: "geojson", data: geojson });

      map.addLayer({
        id: "zone-fill",
        type: "fill",
        source: "tampa-zones",
        filter: ["==", ["geometry-type"], "Polygon"],
        paint: {
          "fill-color": [
            "case",
            [">=", ["get", "fragility"], 80],
            "rgba(251, 113, 133, 0.35)",
            [">=", ["get", "fragility"], 50],
            "rgba(251, 191, 36, 0.30)",
            "rgba(52, 211, 153, 0.28)"
          ],
          "fill-outline-color": "rgba(148, 163, 184, 0.45)"
        }
      });

      map.addLayer({
        id: "facility-point",
        type: "circle",
        source: "tampa-zones",
        filter: ["==", ["geometry-type"], "Point"],
        paint: {
          "circle-radius": 6,
          "circle-stroke-width": 1,
          "circle-stroke-color": "rgba(15, 23, 42, 1)",
          "circle-color": [
            "case",
            [">=", ["get", "fragility"], 80],
            "#fb7185",
            [">=", ["get", "fragility"], 50],
            "#fbbf24",
            "#34d399"
          ]
        }
      });
    });

    mapRef.current = map;

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !map.isStyleLoaded()) {
      return;
    }

    const source = map.getSource("tampa-zones") as GeoJSONSource | undefined;
    if (!source) {
      return;
    }

    fetch("/data/tampa_data.json")
      .then((response) => response.json() as Promise<FeatureCollection>)
      .then((geojson) => {
        const updatedFeatures = geojson.features.map((feature) => {
          const next = { ...feature };
          if (next.properties?.kind === "zone") {
            next.properties = {
              ...next.properties,
              fragility: scenarioState.score
            };
          }
          return next;
        });

        source.setData({ ...geojson, features: updatedFeatures });
      })
      .catch(() => {
        // Keep the previous map data if mock fetch fails.
      });
  }, [scenarioState.score]);

  useEffect(() => {
    setIsLoadingIntelligence(true);
    setTraceLogs([]);

    const timers: number[] = [];

    scenarioState.logs.forEach((entry, index) => {
      const timer = window.setTimeout(() => {
        setTraceLogs((prev) => [...prev, entry]);
      }, 420 * (index + 1));
      timers.push(timer);
    });

    const loadingTimer = window.setTimeout(() => {
      setIsLoadingIntelligence(false);
    }, 2000);

    timers.push(loadingTimer);

    return () => {
      timers.forEach((timer) => window.clearTimeout(timer));
    };
  }, [activeScenario, scenarioState.logs]);

  return (
    <main className="relative h-screen w-full overflow-hidden bg-slate-950 text-slate-200">
      <div ref={mapContainerRef} className="absolute inset-0" aria-label="Mapbox canvas" />

      {!mapboxgl.accessToken && (
        <div className="absolute right-6 top-20 z-40 rounded border border-amber-500/40 bg-amber-950/70 px-3 py-2 text-xs text-amber-300 backdrop-blur-sm">
          Mapbox token missing. Set NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN in .env.local.
        </div>
      )}

      <div className="pointer-events-none absolute inset-0 z-10 shadow-vignette" />

      <header className="absolute left-0 right-0 top-0 z-30 border-b border-slate-800 bg-slate-900/80 backdrop-blur-sm">
        <div className="mx-auto flex h-14 items-center justify-between px-6">
          <div className="flex items-center gap-3">
            <ShieldAlert className="h-5 w-5 text-blue-400" />
            <div>
              <p className="text-sm font-semibold uppercase tracking-wide text-slate-300">Tampa Bay Resilience Ecosystem</p>
              <p className="text-[11px] text-slate-400">Multi-Agent Fragility Intelligence Dashboard</p>
            </div>
          </div>

          <div className="flex items-center gap-2 rounded-full border border-emerald-500/30 bg-emerald-950/30 px-3 py-1.5">
            <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-500" />
            <span className="text-xs font-medium text-emerald-300">Open-Meteo: Connected</span>
          </div>
        </div>
      </header>

      <section className="absolute left-4 top-20 z-30 w-[380px] space-y-4 pb-4">
        <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-4 backdrop-blur-sm">
          <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-300">Flood Scenarios</p>
          <div className="grid grid-cols-1 gap-2">
            {scenarios.map((scenario) => {
              const isActive = scenario === activeScenario;
              return (
                <button
                  key={scenario}
                  type="button"
                  onClick={() => setActiveScenario(scenario)}
                  className={[
                    "flex items-center justify-between rounded-lg border px-3 py-2 text-left text-sm transition-all duration-200",
                    isActive
                      ? "border-blue-500 bg-blue-900/40 text-blue-400 shadow-glow"
                      : "border-slate-700 bg-slate-800 text-slate-400 hover:bg-slate-700 hover:text-slate-200"
                  ].join(" ")}
                >
                  <span className="flex items-center gap-2">
                    {scenarioIcons[scenario]}
                    <span className="capitalize">{scenario}</span>
                  </span>
                  <span className="text-[11px] font-mono uppercase tracking-wide">ready</span>
                </button>
              );
            })}
          </div>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-4 backdrop-blur-sm">
          <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-300">Intelligence Panel</p>

          {isLoadingIntelligence ? (
            <div className="space-y-3">
              <div className="h-4 w-2/3 animate-pulse rounded bg-slate-800" />
              <div className="h-3 w-full animate-pulse rounded bg-slate-800" />
              <div className="h-3 w-5/6 animate-pulse rounded bg-slate-800" />
              <div className="h-16 w-full animate-pulse rounded bg-slate-800" />
              <div className="h-16 w-full animate-pulse rounded bg-slate-800" />
            </div>
          ) : (
            <>
              <div className="mb-4 rounded-lg border border-slate-800 bg-slate-950/60 p-3">
                <div className="mb-2 flex items-center justify-between">
                  <span className="text-[11px] uppercase tracking-wide text-slate-400">Area Focus</span>
                  <span className={`rounded border px-2 py-0.5 text-xs font-semibold ${severityClass(scenarioState.score)}`}>
                    Score {scenarioState.score}
                  </span>
                </div>
                <p className="text-sm text-slate-200">{scenarioState.affected}</p>
              </div>

              <div className="mb-4 border-l-4 border-blue-500 pl-4">
                <p className="mb-1 text-[11px] uppercase tracking-wide text-slate-400">AI Narrative</p>
                <p className="text-sm text-slate-200">{scenarioState.summary}</p>
              </div>

              <div>
                <p className="mb-2 text-[11px] uppercase tracking-wide text-slate-400">Recommended Actions</p>
                {scenarioState.actions.map((action) => (
                  <div
                    key={action.id}
                    className={`mb-2 flex items-start gap-3 rounded border p-3 ${actionSeverityClass(action.urgency)}`}
                  >
                    <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
                    <div>
                      <p className="text-sm font-medium text-slate-200">{action.title}</p>
                      <p className="text-xs text-slate-400">{action.detail}</p>
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      </section>

      <aside className="absolute right-4 top-20 z-30 w-[260px] rounded-xl border border-slate-800 bg-slate-900/80 p-4 backdrop-blur-sm">
        <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-300">Infrastructure Status</p>
        <div className="space-y-2 text-sm">
          <StatusLine icon={<MapPinned className="h-4 w-4" />} label="Road Corridors" value="14 monitored" tone="warning" />
          <StatusLine icon={<Hospital className="h-4 w-4" />} label="Hospital Routes" value="3 constrained" tone="critical" />
          <StatusLine icon={<Droplets className="h-4 w-4" />} label="Drainage Zones" value="7 elevated" tone="warning" />
        </div>
      </aside>

      <section className="absolute bottom-4 right-4 z-30 w-[min(560px,calc(100%-2rem))] overflow-hidden rounded-lg border border-slate-800 bg-black/70 shadow-2xl backdrop-blur-md">
        <div className="flex items-center justify-between border-b border-slate-800 bg-slate-900 px-3 py-1">
          <div className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-rose-400" />
            <span className="h-2 w-2 rounded-full bg-amber-400" />
            <span className="h-2 w-2 rounded-full bg-emerald-400" />
          </div>
          <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-300">System Trace</p>
          <span className="text-[10px] font-mono text-slate-500">adk.runtime/live</span>
        </div>

        <div className="h-44 overflow-y-auto p-3 font-mono text-xs text-emerald-400/90">
          {traceLogs.length === 0 ? (
            <p className="animate-pulse text-slate-500">Awaiting agent execution logs...</p>
          ) : (
            traceLogs.map((line, index) => (
              <p key={`${line}-${index}`} className="animate-fade-in-up pb-1">
                {line}
              </p>
            ))
          )}
        </div>
      </section>
    </main>
  );
}

function StatusLine({
  icon,
  label,
  value,
  tone
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  tone: "critical" | "warning" | "stable";
}) {
  const toneStyle =
    tone === "critical"
      ? "text-rose-400"
      : tone === "warning"
        ? "text-amber-400"
        : "text-emerald-400";

  return (
    <div className="flex items-center justify-between rounded border border-slate-800 bg-slate-950/40 px-2 py-1.5">
      <span className="flex items-center gap-2 text-slate-300">
        {icon}
        <span>{label}</span>
      </span>
      <span className={`text-xs font-mono ${toneStyle}`}>{value}</span>
    </div>
  );
}
