"use client";

import { AlertTriangle, Droplets, Hospital, MapPinned, ShieldAlert } from "lucide-react";
import Link from "next/link";
import mapboxgl, { GeoJSONSource, Map as MapboxMap } from "mapbox-gl";
import { useEffect, useMemo, useRef, useState } from "react";
import type { ReactNode } from "react";

import { DraggablePanel } from "../../components/DraggablePanel";
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
  
  const [mapReady, setMapReady] = useState(false);
  const [apiData, setApiData] = useState<any>(null);
  const [showFragilityInfo, setShowFragilityInfo] = useState(false);
  const [hoverInfo, setHoverInfo] = useState<{
    x: number;
    y: number;
    zoneLabel: string;
    score: number | null;
  } | null>(null);
  const [panels, setPanels] = useState({ scenarios: true, intelligence: true, fragility: true, trace: false }) as any;
  
  const [filterScore, setFilterScore] = useState(0);

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
      zoom: 8,
      minZoom: 8,
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
    const map = mapRef.current;
    if (!map || !mapReady) return;

    const getZoneLabel = (props: Record<string, any>, fallbackId: string) => {
      return (
        props.zoneName ||
        props.name ||
        props.zip ||
        props.zipCode ||
        props.ZIP ||
        fallbackId ||
        "Unknown zone"
      );
    };

    const handleHover = (event: any) => {
      const feature = event.features?.[0];
      if (!feature) {
        return;
      }

      const props = (feature.properties || {}) as Record<string, any>;
      const zoneId = String(props.zoneId || props.name || props.zoneName || "");
      const zoneLabel = String(getZoneLabel(props, zoneId));
      const score = currentZoneScoresRef.current.get(zoneId);

      setHoverInfo({
        x: event.point.x,
        y: event.point.y,
        zoneLabel,
        score: typeof score === "number" ? Math.round(score) : null
      });
      map.getCanvas().style.cursor = "pointer";
    };

    const clearHover = () => {
      setHoverInfo(null);
      map.getCanvas().style.cursor = "";
    };

    map.on("mousemove", ZONE_LAYER_ID, handleHover);
    map.on("mouseleave", ZONE_LAYER_ID, clearHover);
    map.on("mousemove", FACILITY_LAYER_ID, handleHover);
    map.on("mouseleave", FACILITY_LAYER_ID, clearHover);

    return () => {
      map.off("mousemove", ZONE_LAYER_ID, handleHover);
      map.off("mouseleave", ZONE_LAYER_ID, clearHover);
      map.off("mousemove", FACILITY_LAYER_ID, handleHover);
      map.off("mouseleave", FACILITY_LAYER_ID, clearHover);
    };
  }, [mapReady, activeScenario]);

  // Update map opacity when filter slider changes
  useEffect(() => {
    if (mapRef.current && mapReady) {
      if (filterScore > 0) {
        mapRef.current.setPaintProperty(ZONE_LAYER_ID, 'fill-opacity', [
          "case",
          [">=", ["coalesce", ["feature-state", "fragility"], 0], filterScore],
          1.0,
          0.04
        ]);
        try { mapRef.current.setPaintProperty(FACILITY_LAYER_ID, 'circle-opacity', ["case", [">=", ["coalesce", ["feature-state", "fragility"], 0], filterScore], 1.0, 0.04]); } catch(e){}
      } else {
        mapRef.current.setPaintProperty(ZONE_LAYER_ID, 'fill-opacity', 1.0);
        try { mapRef.current.setPaintProperty(FACILITY_LAYER_ID, 'circle-opacity', 1.0); } catch(e){}
      }
    }
  }, [filterScore, mapReady, activeScenario]);

  // Update map opacity when filter slider changes
  useEffect(() => {
    if (mapRef.current && mapReady) {
      if (filterScore > 0) {
        mapRef.current.setPaintProperty(ZONE_LAYER_ID, 'fill-opacity', [
          "case",
          [">=", ["coalesce", ["feature-state", "fragility"], 0], filterScore],
          1.0,
          0.04
        ]);
        try { mapRef.current.setPaintProperty(FACILITY_LAYER_ID, 'circle-opacity', ["case", [">=", ["coalesce", ["feature-state", "fragility"], 0], filterScore], 1.0, 0.04]); } catch(e){}
      } else {
        mapRef.current.setPaintProperty(ZONE_LAYER_ID, 'fill-opacity', 1.0);
        try { mapRef.current.setPaintProperty(FACILITY_LAYER_ID, 'circle-opacity', 1.0); } catch(e){}
      }
    }
  }, [filterScore, mapReady, activeScenario]);

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

      {hoverInfo && (
        <div
          className="pointer-events-none absolute z-50 w-56 rounded-md border border-cyan-500/30 bg-slate-950/90 px-3 py-2 text-xs text-slate-200 shadow-xl backdrop-blur-sm"
          style={{ left: hoverInfo.x + 12, top: hoverInfo.y + 12 }}
        >
          <p className="font-semibold text-cyan-300">{hoverInfo.zoneLabel}</p>
          <p className="mt-1 text-slate-300">
            Fragility Score: {hoverInfo.score ?? "N/A"}
          </p>
        </div>
      )}

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

      <header className="absolute top-4 left-4 right-4 z-40 flex items-center justify-between rounded-xl bg-slate-900/60 p-4 backdrop-blur-md shadow-lg border border-slate-800/50">
        <div className="flex items-center gap-4">
          <Link href="/">
            <h1 className="text-xl font-bold tracking-tight text-white/90 uppercase hover:text-cyan-400 transition-colors cursor-pointer">
              DontCollapse
            </h1>
          </Link>
          <div className="h-6 w-px bg-slate-700"></div>
          
          <div className="flex items-center gap-2">
            {[
              { id: "scenarios", label: "Scenarios" },
              { id: "intelligence", label: "Intelligence" },
              { id: "fragility", label: "System Fragility" },
              { id: "trace", label: "Execution Trace" }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setPanels((p: any) => ({ ...p, [tab.id]: !p[tab.id] }))}
                className={`px-3 py-1.5 rounded-md text-xs font-medium uppercase tracking-wider transition-colors ${panels[tab.id as keyof typeof panels] ? 'bg-cyan-900/40 text-cyan-400 border border-cyan-800/50' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 border border-transparent'}`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </header>

      <DraggablePanel id="scenarios" title="Scenarios" visible={panels.scenarios} defaultPosition={{x: 16, y: 80}} onClose={() => setPanels((p: any) => ({...p, scenarios: false}))} width="w-[380px]">
<div className="space-y-4 max-h-[calc(100vh-6rem)] overflow-y-auto pb-4 pr-1"><div className="p-4">
          
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
        </div></div></DraggablePanel>
      <DraggablePanel id="intelligence" title="Intelligence Panel" visible={panels.intelligence} defaultPosition={{x: 16, y: 450}} onClose={() => setPanels((p: any) => ({...p, intelligence: false}))} width="w-[420px]">
  <div className="h-full">
          
          
          <div className="px-4 pb-4">

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
</DraggablePanel>
      <DraggablePanel id="fragility" title="System Fragility" visible={panels.fragility} defaultPosition={{x: 1180, y: 120}} onClose={() => setPanels((p: any) => ({...p, fragility: false}))} width="w-80">
        <div className="px-4 py-3 space-y-4">
          <div className="space-y-4 border-b border-slate-700/50 pb-4">
            <div>
              <p className="text-[11px] text-slate-300 mb-2 flex justify-between">
                <span>Highlight Minimum Risk Level</span>
                <span className="font-mono text-amber-500">{filterScore === 0 ? 'Off' : `${filterScore}+`}</span>
              </p>
              <input 
                type="range" 
                min="0" 
                max="80" 
                step="10" 
                value={filterScore} 
                onChange={(e) => setFilterScore(parseInt(e.target.value))}
                className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer" 
              />
              <div className="flex justify-between text-[9px] text-slate-500 mt-2 font-mono">
                <span>ALL</span>
                <span>EXTREME</span>
              </div>
            </div>
          </div>

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
                score={infra.score}
                tone={infra.score >= 80 ? "critical" : infra.score >= 50 ? "warning" : "stable"}
              />
            ))}
          </div>

          {showFragilityInfo && (
            <div className="border-t border-slate-700/50 pt-3 space-y-2 bg-slate-900/40 rounded p-3">
              <p className="font-semibold text-slate-200 text-[11px]">Understanding Fragility</p>
              <div className="space-y-2 text-[10px] text-slate-300">
                <p><strong className="text-white">Roads:</strong> Predicted % of thoroughfares fully inundated.</p>
                <p><strong className="text-white">Intersections:</strong> Blockage risk at critical junctions.</p>
                <p><strong className="text-white">Drainage:</strong> Likelihood of storm systems exceeding max capacity.</p>
                <p><strong className="text-white">Power:</strong> Substation and grid equipment vulnerability.</p>
                <p><strong className="text-white">Shelter Routes:</strong> Degree of disruption to emergency hubs.</p>
              </div>
            </div>
          )}

          <button 
            onClick={() => setShowFragilityInfo(!showFragilityInfo)} 
            className="relative mt-1 pt-2 border-t border-slate-700/50 text-[10px] font-mono text-white/50 hover:text-white transition-colors cursor-pointer w-full text-right"
          >
            {showFragilityInfo ? "[hide info]" : "[show info]"}
          </button>
        </div>
      </DraggablePanel>

      <DraggablePanel id="trace" title="Execution Trace" visible={panels.trace} defaultPosition={{x: 1000, y: 550}} onClose={() => setPanels((p: any) => ({...p, trace: false}))} width="w-[400px]"><SystemTrace key={activeScenario} logs={scenarioState.logs} isLoading={isLoadingIntelligence} /></DraggablePanel>
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
