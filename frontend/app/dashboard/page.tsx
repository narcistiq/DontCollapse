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
    return "text-red-400 bg-red-950/50 border-red-500/50";
  }
  if (score >= 40) {
    return "text-orange-400 bg-orange-950/50 border-orange-500/50";
  }
  if (score >= 20) {
    return "text-yellow-400 bg-yellow-950/50 border-yellow-500/50";
  }
  return "text-green-400 bg-green-950/50 border-green-500/50";
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


const TypewriterText = ({ text, delay = 10 }: { text: string, delay?: number }) => {
  const [displayed, setDisplayed] = useState("");
  useEffect(() => {
    setDisplayed("");
    let i = 0;
    const timer = setInterval(() => {
      if (i < text.length) {
        setDisplayed(text.substring(0, i + 3));
        i += 3;
      } else {
        setDisplayed(text);
        clearInterval(timer);
      }
    }, delay);
    return () => clearInterval(timer);
  }, [text, delay]);
  return <span>{displayed}</span>;
}

export default function DashboardPage() {
  const mapContainerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<MapboxMap | null>(null);
  const baseDataRef = useRef<FeatureCollection | null>(null);
  const activeScoreRef = useRef<number>(mockScenarioData["heavy rainfall"].score);
  const currentZoneScoresRef = useRef<Map<string, number>>(new Map());

  const isDev = process.env.NODE_ENV !== "production";
  const mapToken = process.env.NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN?.trim() ?? "";

  const [activeScenario, setActiveScenario] = useState<ScenarioKey>("live conditions");
  const [isLoadingIntelligence, setIsLoadingIntelligence] = useState(false);
  const [showTrace, setShowTrace] = useState(true);
  const [mapReady, setMapReady] = useState(false);
  const [apiData, setApiData] = useState<any>(null);
  const [showFragilityInfo, setShowFragilityInfo] = useState(false);
  const [isPanelOpen, setIsPanelOpen] = useState(true);

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
          data: geojson,
          promoteId: "zoneId"
        });

        map.addLayer({
          id: ZONE_LAYER_ID,
          type: "fill",
          source: MAP_SOURCE_ID,
          filter: ["in", ["geometry-type"], ["literal", ["Polygon", "MultiPolygon"]]],
          paint: {
            "fill-color": [
              "interpolate",
              ["linear"],
              ["coalesce", ["feature-state", "fragility"], 20],
              0, "rgba(34, 197, 94, 0.50)",       
              40, "rgba(234, 179, 8, 0.65)",      
              70, "rgba(249, 115, 22, 0.80)",     
              100, "rgba(239, 68, 68, 0.95)"      
            ],
            "fill-color-transition": { "duration": 1500 },
            "fill-outline-color": "rgba(255, 255, 255, 0.10)"
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
              "interpolate",
              ["linear"],
              ["coalesce", ["feature-state", "fragility"], 20],
              0, "#22c55e",     
              40, "#eab308",    
              70, "#f97316",    
              100, "#ef4444"    
            ],
            "circle-color-transition": { "duration": 1500 }
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
    if (!map || !baseData || !mapReady) return;

    const rankedAreas = apiData?.rankedAreas || [];
    const targetScoreMap = new Map<string, number>();
    rankedAreas.forEach((ra: any) => targetScoreMap.set(ra.zoneId || ra.name, ra.score));

    const startTime = performance.now();
    const duration = 1500; // 1.5 seconds transition
    
    // Snapshot the start scores for this transition
    const startScoreMap = new Map<string, number>();
    baseData.features.forEach((feature) => {
      const zId = (feature.properties?.zoneId || feature.properties?.name) as string;
      startScoreMap.set(zId, currentZoneScoresRef.current.get(zId) ?? 20);
    });

    let animationFrameId: number;

    const animate = (time: number) => {
      let progress = (time - startTime) / duration;
      if (progress > 1) progress = 1;
      
      // Easing function (ease out)
      const easeProgress = 1 - Math.pow(1 - progress, 3);

      baseData.features.forEach((feature) => {
        const zId = (feature.properties?.zoneId || feature.properties?.name) as string;
        const target = targetScoreMap.has(zId) ? targetScoreMap.get(zId)! : 20;
        const start = startScoreMap.get(zId)!;
        
        const currentScore = start + (target - start) * easeProgress;
        currentZoneScoresRef.current.set(zId, currentScore);

        const featureZoneId = feature.properties?.zoneId as string;
        if (featureZoneId) {
          map.setFeatureState(
            { source: MAP_SOURCE_ID, id: featureZoneId },
            { fragility: currentScore }
          );
        }
      });

      if (progress < 1) {
        animationFrameId = requestAnimationFrame(animate);
      }
    };

    animationFrameId = requestAnimationFrame(animate);

    return () => {
      if (animationFrameId) cancelAnimationFrame(animationFrameId);
    };
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
              <p className="text-sm font-semibold uppercase tracking-wide text-slate-300">DontCollapse</p>
              <p className="text-[11px] text-slate-400">Tampa Bay Resilience Ecosystem Console</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            

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
        </div>
      </header>

      <section className="absolute left-4 top-20 z-30 max-h-[calc(100vh-6rem)] w-[380px] space-y-4 overflow-y-auto pb-4 pr-1">
        <div className="rounded-xl bg-slate-900/40 p-4 backdrop-blur-md shadow-lg border border-slate-800/50">
          <p className="mb-3 text-[10px] font-bold uppercase tracking-wider text-slate-400">Scenarios</p>
          <div className="grid grid-cols-1 gap-1.5">
            {scenarios.map((scenario) => {
              const isActive = scenario === activeScenario;
              const descriptions: Record<string, string> = {
                "live conditions": "Baseline current environmental state.",
                "heavy rainfall": "Intense focused precipitation over short duration.",
                "storm surge": "Ocean water pushed inland by hurricane forces.",
                "category 5 hurricane": "Catastrophic landfall with total infrastructure failure.",
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
                    "flex items-center justify-between rounded-md px-3 py-2 text-left text-[13px] font-medium transition-all duration-200 cursor-pointer",
                    isActive
                      ? "bg-slate-800 text-white shadow-sm ring-1 ring-slate-700"
                      : "text-slate-400 hover:bg-slate-800/50 hover:text-slate-200"
                  ].join(" ")}
                >
                  <span className="flex items-center gap-2.5">
                    {scenarioIcons[scenario]}
                    <span className="capitalize">{scenario}</span>
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        <div className="rounded-xl bg-slate-900/40 backdrop-blur-md shadow-lg border border-slate-800/50 overflow-hidden transition-all duration-300">
          <button onClick={() => setIsPanelOpen(!isPanelOpen)} className="w-full p-4 flex items-center justify-between hover:bg-slate-800/30 transition-colors">
            <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Intelligence Panel</p>
            <span className="text-slate-500 text-xs">{isPanelOpen ? '▼' : '▲'}</span>
          </button>
          
          <div className={`px-4 pb-4 transition-all duration-500 ease-in-out ${isPanelOpen ? 'opacity-100 max-h-[800px]' : 'opacity-0 max-h-0 pb-0 overflow-hidden'}`}>

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
              <div className="mb-4">
                <div className="mb-1 flex items-center justify-between">
                  <span className="text-[10px] uppercase tracking-wider text-slate-400 font-bold">Primary Focus</span>
                  <span className={`rounded px-1.5 py-0.5 text-[10px] uppercase tracking-wider font-bold flex items-center gap-1 ${severityClass(overallScore)}`}>
                    Index: <AnimatedNumber value={overallScore} />
                  </span>
                </div>
                <p className="text-[13px] text-slate-300 leading-relaxed">{apiData ? apiData.rankedAreas.slice(0,3).map((z: any) => z.zoneName).join(' • ') : scenarioState.affected}</p>
              </div>

              <div className="mb-5 border-l-2 border-slate-700 pl-3">
                <p className="mb-1 text-[10px] font-bold uppercase tracking-wider text-slate-400">Analysis</p>
                <div className="min-h-[80px]"><p className="text-[12.5px] leading-relaxed text-slate-300"><TypewriterText text={apiData ? apiData.narrative : scenarioState.summary} /></p></div>
              </div>

              <div className="mb-5 border-l-2 border-emerald-500/50 pl-3">
                <p className="mb-1 text-[10px] font-bold uppercase tracking-wider text-slate-400">Agent Logistics</p>
                <div className="min-h-[60px]"><p className="text-[12.5px] leading-relaxed text-slate-300"><TypewriterText text={apiData ? apiData.logistics : "Awaiting autonomous loop instructions..."} /></p></div>
              </div>

              <div>
                <p className="mb-3 text-[10px] font-bold uppercase tracking-wider text-slate-400">Priority Responses</p>
                {scenarioState.actions.map((action) => (
                  <div
                    key={action.id}
                    className={`mb-2 flex items-start gap-3 rounded-lg border p-3 ${actionSeverityClass(action.urgency)}`}
                  >
                    <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 opacity-80" />
                    <div>
                      <p className="text-[13px] font-medium text-slate-200 mb-0.5">{action.title}</p>
                      <div className="min-h-[40px]"><p className="text-[11.5px] leading-relaxed text-slate-400"><TypewriterText text={action.detail} delay={5} /></p></div>
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
        </div>
      </section>
      <aside className="absolute right-4 top-20 z-30 w-[310px] rounded-xl bg-slate-900/40 p-4 backdrop-blur-md shadow-lg border border-slate-800/50">
        <p className="mb-4 text-[10px] font-bold uppercase tracking-wider text-slate-400">System Fragility</p>
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
