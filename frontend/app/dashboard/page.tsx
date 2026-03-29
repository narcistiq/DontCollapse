"use client";

import { AlertTriangle, Droplets, Hospital, MapPinned, ShieldAlert } from "lucide-react";
import Link from "next/link";
import mapboxgl, { GeoJSONSource, Map as MapboxMap } from "mapbox-gl";
import { useEffect, useMemo, useRef, useState } from "react";
import type { ReactNode } from "react";

import { SystemTrace } from "../../components/SystemTrace";
import { AnimatedNumber } from "../../components/AnimatedNumber";
import { mockScenarioData, scenarioIcons, scenarios } from "../../data/scenarios";
import type { ActionTicket, FeatureCollection, ScenarioKey } from "../../types/dashboard";

const MAP_SOURCE_ID = "tampa-zones";
const ZONE_LAYER_ID = "zone-fill";
const FACILITY_LAYER_ID = "facility-point";

const severityClass = (score: number) => {
  if (score >= 60) {
    return "text-rose-400 bg-rose-950/50 border-rose-500/50";
  }
  if (score >= 40) {
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

function applyScenarioScore(geojson: FeatureCollection, rankedAreas: any[]): FeatureCollection {
  if (!rankedAreas || rankedAreas.length === 0) return geojson;
  const scoreMap = new Map<string, number>();
  rankedAreas.forEach(ra => scoreMap.set(ra.zoneId, ra.score));

  return {
    type: "FeatureCollection",
    features: geojson.features.map((feature) => {
      if (feature.properties?.kind !== "zone") {
        return feature;
      }

      const zId = feature.properties?.zoneId as string;
      const zoneScore = scoreMap.has(zId) ? scoreMap.get(zId) : feature.properties?.fragility || 50;
      return {
        ...feature,
        properties: {
          ...feature.properties,
          fragility: zoneScore ?? 50
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
  const [apiData, setApiData] = useState<any>(null);
  const [showFragilityInfo, setShowFragilityInfo] = useState(false);

  const scenarioState = useMemo(() => mockScenarioData[activeScenario], [activeScenario]);
  const overallScore = apiData?.rankedAreas?.length 
    ? Math.round(apiData.rankedAreas.reduce((sum: number, r: any) => sum + r.score, 0) / apiData.rankedAreas.length)
    : scenarioState.score;

  useEffect(() => {
    if (!mapContainerRef.current || mapRef.current || !mapToken) {
      return;
    }

    let disposed = false;
    mapboxgl.accessToken = mapToken;

    const map = new mapboxgl.Map({
      container: mapContainerRef.current,
      style: "mapbox://styles/mapbox/dark-v11",
      center: [-82.46, 27.95],
      zoom: 11,
      minZoom: 10,
      maxZoom: 16,
      maxBounds: [
        [-82.65, 27.80], // Tight Southwest bounds for Tampa proper
        [-82.35, 28.15]  // Tight Northeast bounds for Tampa proper
      ],
      dragRotate: true,
      pitchWithRotate: true,
      keyboard: false,
      pitch: 45,
      bearing: -16,
      antialias: true
    });

    map.addControl(new mapboxgl.NavigationControl({ showCompass: false }), "top-right");

    const resizeObserver = new ResizeObserver(() => {
      map.resize();
    });
    if (mapContainerRef.current) {
      resizeObserver.observe(mapContainerRef.current);
    }

    // Force a resize calculation to ensure the canvas fills the container
    map.on("style.load", () => {
      setTimeout(() => map.resize(), 100);
    });

    map.on("load", async () => {
      map.resize();
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
          data: applyScenarioScore(geojson, [])
        });

        map.addLayer({
          id: ZONE_LAYER_ID,
          type: "fill",
          source: MAP_SOURCE_ID,
          filter: ["in", ["geometry-type"], ["literal", ["Polygon", "MultiPolygon"]]],
          paint: {
            "fill-color": [
              "case",
              [">=", ["get", "fragility"], 60],
              "rgba(251, 113, 133, 0.45)",  // Red for high fragility
              [">=", ["get", "fragility"], 40],
              "rgba(251, 191, 36, 0.40)",   // Amber for medium
              "rgba(52, 211, 153, 0.35)"    // Emerald for low
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
              [">=", ["get", "fragility"], 60],
              "#fb7185",
              [">=", ["get", "fragility"], 40],
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
      resizeObserver.disconnect();
      map.remove();
      mapRef.current = null;
      setMapReady(false);
    };
  }, [mapToken]);

  useEffect(() => {
    activeScoreRef.current = overallScore;

    const map = mapRef.current;
    const baseData = baseDataRef.current;

    if (!map || !baseData) {
      return;
    }

    const source = map.getSource(MAP_SOURCE_ID) as GeoJSONSource | undefined;
    if (!source) {
      return;
    }

    source.setData(applyScenarioScore(baseData, apiData?.rankedAreas || []));
  }, [apiData, mapReady]);

  useEffect(() => {
    setIsLoadingIntelligence(true);
    let disposed = false;

    fetch("http://localhost:8000/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ scenario: activeScenario })
    })
      .then((res) => res.json())
      .then((data) => {
        if (!disposed) {
          setApiData(data);
          setIsLoadingIntelligence(false);
        }
      })
      .catch((err) => {
        console.error("API Error", err);
        if (!disposed) setIsLoadingIntelligence(false);
      });

    return () => {
      disposed = true;
    };
  }, [activeScenario]);

  return (
    <main className="relative h-screen w-full overflow-hidden bg-slate-950 text-slate-200">
      <div
        className="absolute inset-0 bg-[radial-gradient(circle_at_20%_20%,rgba(59,130,246,0.15),transparent_45%),radial-gradient(circle_at_80%_40%,rgba(16,185,129,0.12),transparent_40%),linear-gradient(135deg,rgba(15,23,42,0.95),rgba(2,6,23,0.98))]"
        aria-hidden="true"
      />
      <div ref={mapContainerRef} className="absolute inset-0 w-full h-full" style={{ width: '100vw', height: '100vh' }} aria-label="Mapbox canvas" />

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
              <p className="text-sm font-semibold uppercase tracking-wide text-slate-300">DontCollapse Dashboard</p>
              <p className="text-[11px] text-slate-400">Tampa Bay Resilience Ecosystem Console</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <div className="rounded-full border border-emerald-500/30 bg-emerald-950/30 px-3 py-1.5">
              <span className="inline-flex items-center gap-2 text-xs font-medium text-emerald-300">
                <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-500" />
                Open-Meteo: Connected
              </span>
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

            <Link
              href="/"
              className="rounded border border-slate-700 bg-slate-800 px-2.5 py-1 text-[11px] font-mono text-slate-300 transition-colors hover:bg-slate-700"
            >
              Back to Landing
            </Link>
          </div>
        </div>
      </header>

      <section className="absolute left-4 top-20 z-30 max-h-[calc(100vh-6rem)] w-[380px] space-y-4 overflow-y-auto pb-4 pr-1">
        <div className="rounded-xl border border-slate-800 bg-slate-900/80 p-4 backdrop-blur-sm">
          <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-300">Flood Scenarios</p>
          <div className="grid grid-cols-1 gap-2">
            {scenarios.map((scenario) => {
              const isActive = scenario === activeScenario;
              const descriptions: Record<string, string> = {
                "heavy rainfall": "Intense focused precipitation over short duration.",
                "storm surge": "Ocean water pushed inland by hurricane forces.",
                "sea-level-rise increase": "Long-term baseline elevation of tidal boundaries.",
                "repeated flooding days": "Cumulative saturation from multi-day event streams."
              };

              return (
                <button
                  key={scenario}
                  type="button"
                  title={descriptions[scenario]}
                  aria-pressed={isActive}
                  onClick={() => setActiveScenario(scenario)}
                  className={[
                    "flex items-center justify-between rounded-lg border px-3 py-2 text-left text-sm transition-all duration-200 cursor-help",
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
                  <span className={`rounded border px-2 py-0.5 text-xs font-semibold flex items-center gap-1 ${severityClass(overallScore)}`}>
                    Score <AnimatedNumber value={overallScore} />
                  </span>
                </div>
                <p className="text-sm text-slate-200">{apiData ? apiData.rankedAreas.slice(0,3).map((z: any) => z.zoneName).join(', ') : scenarioState.affected}</p>
              </div>

              <div className="mb-4 border-l-4 border-blue-500 pl-4">
                <p className="mb-1 text-[11px] uppercase tracking-wide text-slate-400">AI Narrative</p>
                <p className="text-sm text-slate-200">{apiData ? apiData.narrative : scenarioState.summary}</p>
              </div>

              <div className="mb-4 border-l-4 border-emerald-500 pl-4">
                <p className="mb-1 text-[11px] uppercase tracking-wide text-slate-400">A2A Logistics</p>
                <p className="text-sm text-slate-200">{apiData ? apiData.logistics : "Awaiting agent instructions..."}</p>
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

      <aside className="absolute right-4 top-20 z-30 w-[310px] rounded-xl border border-slate-800 bg-slate-900/80 p-4 backdrop-blur-sm">
        <p className="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-300">Infrastructure Fragility</p>
        <div className="space-y-2 text-sm pb-4">
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
              score={infra.score}
              tone={infra.score >= 80 ? "critical" : infra.score >= 50 ? "warning" : "stable"}
            />
          ))}
        </div>
        
        <button 
          onClick={() => setShowFragilityInfo(!showFragilityInfo)} 
          className="absolute bottom-2 right-3 text-[10px] font-mono text-white/50 hover:text-white transition-colors cursor-pointer"
        >
          {showFragilityInfo ? "[hide info]" : "[?] info"}
        </button>
      </aside>

      {showFragilityInfo && (
        <div className="absolute right-[330px] top-20 z-40 w-64 rounded-xl border border-blue-500/30 bg-slate-900/95 p-4 text-xs text-slate-300 shadow-2xl backdrop-blur-md space-y-2">
          <p className="font-semibold text-slate-200 mb-1 border-b border-slate-700/50 pb-1">Understanding Fragility</p>
          <p><strong className="text-white">Roads:</strong> Predicted % of thoroughfares fully inundated.</p>
          <p><strong className="text-white">Intersections:</strong> Blockage risk at critical junctions.</p>
          <p><strong className="text-white">Drainage:</strong> Likelihood of storm systems exceeding max capacity.</p>
          <p><strong className="text-white">Power:</strong> Substation and grid equipment vulnerability.</p>
          <p><strong className="text-white">Shelter Routes:</strong> Degree of disruption to emergency hubs.</p>
        </div>
      )}

      {showTrace && <SystemTrace key={activeScenario} logs={scenarioState.logs} isLoading={isLoadingIntelligence} />}
    </main>
  );
}

function StatusLine({
  icon,
  label,
  score,
  tone
}: {
  icon: ReactNode;
  label: string;
  score: number;
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
      <span className={`text-xs font-mono flex items-center gap-1 ${toneStyle}`}>
        Score <AnimatedNumber value={score} />
      </span>
    </div>
  );
}
