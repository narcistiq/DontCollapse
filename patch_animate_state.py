import re

path = 'frontend/app/dashboard/page.tsx'
with open(path, 'r') as f:
    code = f.read()

# We need to manage previous active score map, but wait, feature-state is preserved in the map!
# We can just read the current state? Mapbox doesn't easily expose a synchronous "getFeatureState".
# But we can keep a ref in React of the current zone scores.

# FIND:
#   const activeScoreRef = useRef<number>(mockScenarioData["heavy rainfall"].score);
to_replace_ref = "  const activeScoreRef = useRef<number>(mockScenarioData[\"heavy rainfall\"].score);"
new_ref = """  const activeScoreRef = useRef<number>(mockScenarioData["heavy rainfall"].score);
  const currentZoneScoresRef = useRef<Map<string, number>>(new Map());"""

code = code.replace(to_replace_ref, new_ref)

effect_to_replace = """  useEffect(() => {
    if (!baseData || !mapReady) return;
    const map = mapRef.current;
    if (!map) return;

    const rankedAreas = apiData?.rankedAreas || [];
    const scoreMap = new Map<string, number>();
    rankedAreas.forEach((ra: any) => scoreMap.set(ra.zoneId, ra.score));

    baseData.features.forEach((feature) => {
      const zId = feature.properties?.zoneId as string;
      const zoneScore = scoreMap.has(zId) ? scoreMap.get(zId) : feature.properties?.fragility || 20;

      if (feature.id) {
        map.setFeatureState(
          { source: MAP_SOURCE_ID, id: feature.id },
          { fragility: zoneScore }
        );
      }
    });

  }, [apiData, mapReady, baseData]);"""


new_effect = """  useEffect(() => {
    if (!baseData || !mapReady) return;
    const map = mapRef.current;
    if (!map) return;

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

        if (feature.id) {
          map.setFeatureState(
            { source: MAP_SOURCE_ID, id: feature.id },
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
  }, [apiData, mapReady, baseData]);"""

code = code.replace(effect_to_replace, new_effect)

with open(path, 'w') as f:
    f.write(code)

