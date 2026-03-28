"use client";

import { AlertTriangle, Droplets, Hospital, MapPinned, ShieldAlert } from "lucide-react";
import mapboxgl, { GeoJSONSource, Map as MapboxMap } from "mapbox-gl";
import { useEffect, useMemo, useRef, useState } from "react";
import type { ReactNode } from "react";

import { SystemTrace } from "../components/SystemTrace";
import { mockScenarioData, scenarioIcons, scenarios } from "../data/scenarios";
import type { ActionTicket, FeatureCollection, ScenarioKey } from "../types/dashboard";

mapboxgl.accessToken = process.env.NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN ?? "";

const MAP_SOURCE_ID = "tampa-zones";
const ZONE_LAYER_ID = "zone-fill";
const FACILITY_LAYER_ID = "facility-point";

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

function applyScenarioScore(geojson: FeatureCollection, score: number): FeatureCollection {
  return {
    type: "FeatureCollection",
    features: geojson.features.map((feature) => {
      if (feature.properties?.kind !== "zone") {
        return feature;
      }

      return {
        ...feature,
        properties: {
          ...feature.properties,
          fragility: score
        }
      };
    })
  };
}

export default function DashboardPage() {
  const mapContainerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<MapboxMap | null>(null);
  const baseDataRef = useRef<FeatureCollection | null>(null);
  const activeScoreRef = useRef<number>(mockScenarioData["heavy rainfall"].score);
  const isDev = process.env.NODE_ENV !== "production";
  const mapToken = process.env.NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN?.trim() ?? "";

  const [activeScenario, setActiveScenario] = useState<ScenarioKey>("heavy rainfall");
  const [isLoadingIntelligence, setIsLoadingIntelligence] = useState(false);
  const [showTrace, setShowTrace] = useState(true);
  const [mapReady, setMapReady] = useState(false);

  const scenarioState = useMemo(() => mockScenarioData[activeScenario], [activeScenario]);

  useEffect(() => {
    if (!mapContainerRef.current || mapRef.current || !mapToken) {
      return;
    }

    let disposed = false;

    mapboxgl.accessToken = mapToken;

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
      try {
        const response = await fetch("/data/tampa_data.json");
        if (!response.ok) {
          throw new Error(`Failed to load static map data (${response.status})`);
        }

        const geojson = (await response.json()) as FeatureCollection;
        if (disposed) {
          return;
        }

        baseDataRef.current = geojson;

        map.addSource(MAP_SOURCE_ID, {
          type: "geojson",
          data: applyScenarioScore(geojson, activeScoreRef.current)
        });

        map.addLayer({
          id: ZONE_LAYER_ID,
          type: "fill",
          source: MAP_SOURCE_ID,
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
          id: FACILITY_LAYER_ID,
          type: "circle",
          source: MAP_SOURCE_ID,
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

        setMapReady(true);
      } catch (error) {
        console.error("Failed to initialize map layers:", error);
      }
    });

    mapRef.current = map;

    return () => {
      disposed = true;
      map.remove();
      mapRef.current = null;
      setMapReady(false);
    };
  }, [mapToken]);

  useEffect(() => {
    activeScoreRef.current = scenarioState.score;

    const map = mapRef.current;
    const baseData = baseDataRef.current;

    if (!map || !baseData) {
      return;
    }

    const source = map.getSource(MAP_SOURCE_ID) as GeoJSONSource | undefined;
    if (!source) {
      return;
    }

    source.setData(applyScenarioScore(baseData, scenarioState.score));
  }, [scenarioState.score]);

  useEffect(() => {
    setIsLoadingIntelligence(true);

    const loadingTimer = window.setTimeout(() => {
      setIsLoadingIntelligence(false);
    }, 2000);

    return () => {
      window.clearTimeout(loadingTimer);
    };
  }, [activeScenario]);

  return (
    <main className="relative h-screen w-full overflow-hidden bg-slate-950 text-slate-200">
      <div
        className="absolute inset-0 bg-[radial-gradient(circle_at_20%_20%,rgba(59,130,246,0.15),transparent_45%),radial-gradient(circle_at_80%_40%,rgba(16,185,129,0.12),transparent_40%),linear-gradient(135deg,rgba(15,23,42,0.95),rgba(2,6,23,0.98))]"
        aria-hidden="true"
      />
      <div ref={mapContainerRef} className="absolute inset-0" aria-label="Mapbox canvas" />

      {!mapToken && (
        <div className="absolute right-6 top-20 z-40 rounded border border-amber-500/40 bg-amber-950/70 px-3 py-2 text-xs text-amber-300 backdrop-blur-sm">
          Mapbox token missing. Set NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN in .env.local.
        </div>
      )}

      {mapToken && !mapReady && (
        <div className="absolute right-6 top-20 z-40 rounded border border-blue-500/30 bg-slate-900/70 px-3 py-2 text-xs text-slate-300 backdrop-blur-sm">
          Loading map layers...
        </div>
      )}

      <div className="pointer-events-none absolute inset-0 z-10 shadow-vignette" />

      <header className="absolute left-0 right-0 top-0 z-30 border-b border-slate-800 bg-slate-900/80 backdrop-blur-sm">
        <div className="mx-auto flex h-14 items-center justify-between px-6">
          <div className="flex items-center gap-3">
            <ShieldAlert className="h-5 w-5 text-blue-400" />
            <div>
              <p className="text-sm font-semibold uppercase tracking-wide text-slate-300">DontCollapse</p>
              <p className="text-[11px] text-slate-400">Tampa Bay Resilience Ecosystem Dashboard</p>
            </div>
          </div>

          <div className="flex items-center gap-2 rounded-full border border-emerald-500/30 bg-emerald-950/30 px-3 py-1.5">
            <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-500" />
            <span className="text-xs font-medium text-emerald-300">Open-Meteo: Connected</span>
          </div>

          {isDev && (
            <button
              type="button"
              onClick={() => setShowTrace((prev) => !prev)}
              className="rounded border border-slate-700 bg-slate-800 px-2.5 py-1 text-[11px] font-mono text-slate-300 transition-colors hover:bg-slate-700"
            >
              Trace: {showTrace ? "ON" : "OFF"}
            </button>
          )}
        </div>
      </header>

      <section className="absolute left-4 top-20 z-30 max-h-[calc(100vh-6rem)] w-[380px] space-y-4 overflow-y-auto pr-1 pb-4">
        <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-4 backdrop-blur-sm">
          <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-300">Flood Scenarios</p>
          <div className="grid grid-cols-1 gap-2">
            {scenarios.map((scenario) => {
              const isActive = scenario === activeScenario;

              return (
                <button
                  key={scenario}
                  type="button"
                  aria-pressed={isActive}
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

                <div className="mt-3 rounded border border-slate-700 bg-slate-950/60 p-2">
                  <p className="mb-1 text-[11px] uppercase tracking-wide text-slate-400">Action Payload</p>
                  <code className="block font-mono text-[11px] text-slate-300">
                    {JSON.stringify(scenarioState.actionPayload)}
                  </code>
                </div>
              </div>
            </>
          )}
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-4 backdrop-blur-sm">
          <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-300">Ranked Vulnerable Areas</p>
          <div className="space-y-2">
            {scenarioState.rankedAreas.map((area, index) => (
              <div key={area.name} className="rounded border border-slate-700 bg-slate-800/50 p-2">
                <div className="mb-1 flex items-center justify-between">
                  <p className="text-xs font-medium text-slate-200">
                    {index + 1}. {area.name}
                  </p>
                  <span className={`rounded border px-1.5 py-0.5 text-[10px] font-mono ${severityClass(area.score)}`}>
                    {area.score}
                  </span>
                </div>
                <p className="text-[11px] text-slate-400">{area.reason}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <aside className="absolute right-4 top-20 z-30 w-[310px] rounded-xl border border-slate-800 bg-slate-900/80 p-4 backdrop-blur-sm">
        <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-300">Infrastructure Fragility</p>
        <div className="space-y-2 text-sm">
          {scenarioState.infrastructureScores.map((infra) => (
            <StatusLine
              key={infra.id}
              icon={
                infra.id === "roads" ? (
                  <MapPinned className="h-4 w-4" />
                ) : infra.id === "access-routes" ? (
                  <Hospital className="h-4 w-4" />
                ) : (
                  <Droplets className="h-4 w-4" />
                )
              }
              label={infra.label}
              value={`Score ${infra.score}`}
              tone={infra.score >= 80 ? "critical" : infra.score >= 50 ? "warning" : "stable"}
            />
          ))}
        </div>
      </aside>

      {showTrace && <SystemTrace key={activeScenario} logs={scenarioState.logs} isLoading={isLoadingIntelligence} />}
    </main>
  );
}

function StatusLine({
  icon,
  label,
  value,
  tone
}: {
  icon: ReactNode;
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
