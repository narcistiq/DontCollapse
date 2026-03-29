import re

with open("frontend/app/dashboard/page.tsx", "r") as f:
    text = f.read()

# Replace scenarioState.score with overallScore calculated from apiData
# Around line 79
text = text.replace(
    'const scenarioState = useMemo(() => mockScenarioData[activeScenario], [activeScenario]);',
    '''const scenarioState = useMemo(() => mockScenarioData[activeScenario], [activeScenario]);
  const overallScore = apiData?.rankedAreas?.length 
    ? Math.round(apiData.rankedAreas.reduce((sum: number, r: any) => sum + r.score, 0) / apiData.rankedAreas.length)
    : scenarioState.score;'''
)

text = text.replace(
    'activeScoreRef.current = scenarioState.score;',
    'activeScoreRef.current = overallScore;'
)

# In the render:
text = text.replace(
    'severityClass(scenarioState.score)',
    'severityClass(overallScore)'
)
text = text.replace(
    'Score <AnimatedNumber value={scenarioState.score} />',
    'Score <AnimatedNumber value={overallScore} />'
)

with open("frontend/app/dashboard/page.tsx", "w") as f:
    f.write(text)
    
print("Page patched.")
