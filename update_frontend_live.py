import re

with open("frontend/app/dashboard/page.tsx", "r") as f:
    content = f.read()

# Replace applyScenarioScore signature
old_fn = """function applyScenarioScore(geojson: FeatureCollection, score: number): FeatureCollection {"""
new_fn = """function applyScenarioScore(geojson: FeatureCollection, rankedAreas: any[]): FeatureCollection {
  if (!rankedAreas || rankedAreas.length === 0) return geojson;
  const scoreMap = new Map<string, number>();
  rankedAreas.forEach(ra => scoreMap.set(ra.zoneId, ra.score));
"""
content = content.replace(old_fn, new_fn)

# Replace the inner map logic
old_map = """      return {
        ...feature,
        properties: {
          ...feature.properties,
          fragility: score
        }
      };"""
new_map = """      const zId = feature.properties?.zoneId as string;
      const zoneScore = scoreMap.has(zId) ? scoreMap.get(zId) : feature.properties?.fragility || 50;
      return {
        ...feature,
        properties: {
          ...feature.properties,
          fragility: zoneScore
        }
      };"""
content = content.replace(old_map, new_map)

# Replace the state hooks to add apiData
hook_search = """  const [activeScenario, setActiveScenario] = useState<ScenarioKey>("heavy rainfall");
  const [isLoadingIntelligence, setIsLoadingIntelligence] = useState(false);
  const [showTrace, setShowTrace] = useState(true);
  const [mapReady, setMapReady] = useState(false);

  const scenarioState = useMemo(() => mockScenarioData[activeScenario], [activeScenario]);"""

hook_replace = """  const [activeScenario, setActiveScenario] = useState<ScenarioKey>("heavy rainfall");
  const [isLoadingIntelligence, setIsLoadingIntelligence] = useState(false);
  const [showTrace, setShowTrace] = useState(true);
  const [mapReady, setMapReady] = useState(false);
  const [apiData, setApiData] = useState<any>(null);

  const scenarioState = useMemo(() => mockScenarioData[activeScenario], [activeScenario]);"""
content = content.replace(hook_search, hook_replace)

# Replace the map data assignment
map_call_old1 = """data: applyScenarioScore(geojson, activeScoreRef.current)"""
map_call_new1 = """data: applyScenarioScore(geojson, [])"""
content = content.replace(map_call_old1, map_call_new1)

map_call_old2 = """source.setData(applyScenarioScore(baseData, scenarioState.score));
  }, [scenarioState.score]);"""
map_call_new2 = """source.setData(applyScenarioScore(baseData, apiData?.rankedAreas || []));
  }, [apiData]);"""
content = content.replace(map_call_old2, map_call_new2)

# Insert the API fetch in the activeScenario effect
effect_old = """  useEffect(() => {
    setIsLoadingIntelligence(true);

    const loadingTimer = window.setTimeout(() => {
      setIsLoadingIntelligence(false);
    }, 1600);

    return () => {
      window.clearTimeout(loadingTimer);
    };
  }, [activeScenario]);"""

effect_new = """  useEffect(() => {
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
  }, [activeScenario]);"""
content = content.replace(effect_old, effect_new)

# Override the intelligence panel rendering to use apiData
render_panel_old = """<p className="text-sm text-slate-200">{scenarioState.affected}</p>
              </div>

              <div className="mb-4 border-l-4 border-blue-500 pl-4">
                <p className="mb-1 text-[11px] uppercase tracking-wide text-slate-400">AI Narrative</p>
                <p className="text-sm text-slate-200">{scenarioState.summary}</p>
              </div>

              <div>
                <p className="mb-2 text-[11px] uppercase tracking-wide text-slate-400">Recommended Actions</p>
                {scenarioState.actions.map((action) => ("""

render_panel_new = """<p className="text-sm text-slate-200">{apiData ? apiData.rankedAreas.slice(0,3).map((z: any) => z.zoneName).join(', ') : scenarioState.affected}</p>
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
                {scenarioState.actions.map((action) => ("""
content = content.replace(render_panel_old, render_panel_new)

with open("frontend/app/dashboard/page.tsx", "w") as f:
    f.write(content)
print("Updated frontend/app/dashboard/page.tsx")
