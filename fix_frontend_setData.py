import re

path = 'frontend/app/dashboard/page.tsx'
with open(path, 'r') as f:
    code = f.read()

# Replace applyScenarioScore signature to do nothing but return baseData and remove it basically.
# Wait, actually we don't need it. We will just use setFeatureState.

# FIND:
#   useEffect(() => {
#    if (!baseData || !mapReady) return;
#    const map = mapRef.current;
#    if (!map) return;
#
#    const source = map.getSource(MAP_SOURCE_ID) as GeoJSONSource | undefined;
#    if (!source) {
#      return;
#    }
#
#    source.setData(applyScenarioScore(baseData, apiData?.rankedAreas || []));
#  }, [apiData, mapReady]);

to_replace = """  useEffect(() => {
    if (!baseData || !mapReady) return;
    const map = mapRef.current;
    if (!map) return;

    const source = map.getSource(MAP_SOURCE_ID) as GeoJSONSource | undefined;
    if (!source) {
      return;
    }

    source.setData(applyScenarioScore(baseData, apiData?.rankedAreas || []));
  }, [apiData, mapReady]);"""

new_code = """  useEffect(() => {
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

code = code.replace(to_replace, new_code)

# We also need to change map coloring to use feature-state instead of get.
code = code.replace('["coalesce", ["get", "fragility"], 0]', '["coalesce", ["feature-state", "fragility"], 20]')
# Note there are probably two places it used ["get", "fragility"], one for fill and one for circle

# Ensure "applyScenarioScore" is not used incorrectly during first load
first_load = """data: applyScenarioScore(geojson, [])"""
first_load_new = """data: geojson"""
code = code.replace(first_load, first_load_new)

# if the first load relies on get fragility, wait, if we use feature-state, we should probably set feature state immediately after map load. 
# actually Mapbox sets feature state to null initially, so the coalesce will default to 20, which is perfectly fine (green)!


with open(path, 'w') as f:
    f.write(code)

