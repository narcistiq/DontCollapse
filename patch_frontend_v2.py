import re
import os

path = 'frontend/app/dashboard/page.tsx'
with open(path, 'r') as f:
    code = f.read()

# 1. Faster Typewriter component
old_typewriter = """const TypewriterText = ({ text }: { text: string }) => {
  const [displayed, setDisplayed] = useState("");
  useEffect(() => {
    setDisplayed("");
    let i = 0;
    const timer = setInterval(() => {
      if (i < text.length) {
        setDisplayed(prev => prev + text.charAt(i));
        i++;
      } else {
        clearInterval(timer);
      }
    }, 15);
    return () => clearInterval(timer);
  }, [text]);
  return <span>{displayed}</span>;
}"""

new_typewriter = """const TypewriterText = ({ text, delay = 10 }: { text: string, delay?: number }) => {
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
}"""

if old_typewriter in code:
    code = code.replace(old_typewriter, new_typewriter)

# 2. Add fixed height to analysis and logistics
code = code.replace(
    '<p className="text-[12.5px] leading-relaxed text-slate-300"><TypewriterText text={apiData ? apiData.narrative : scenarioState.summary} /></p>',
    '<div className="min-h-[80px]"><p className="text-[12.5px] leading-relaxed text-slate-300"><TypewriterText text={apiData ? apiData.narrative : scenarioState.summary} /></p></div>'
)

code = code.replace(
    '<p className="text-[12.5px] leading-relaxed text-slate-300">{apiData ? apiData.logistics : "Awaiting autonomous loop instructions..."}</p>',
    '<div className="min-h-[60px]"><p className="text-[12.5px] leading-relaxed text-slate-300"><TypewriterText text={apiData ? apiData.logistics : "Awaiting autonomous loop instructions..."} /></p></div>'
)

# 3. Typewriter in Actions
code = code.replace(
    '<p className="text-[11.5px] leading-relaxed text-slate-400">{action.detail}</p>',
    '<div className="min-h-[40px]"><p className="text-[11.5px] leading-relaxed text-slate-400"><TypewriterText text={action.detail} delay={5} /></p></div>'
)

# 4. Implement feature-state instead of setData for smooth transitions
# First we need to get rid of applyScenarioScore injecting into setData
# Then we find where map is updated on activeScenario change.

with open(path, 'w') as f:
    f.write(code)

