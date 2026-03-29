import os
import re

path = 'frontend/app/dashboard/page.tsx'
with open(path, 'r') as f:
    code = f.read()

# 1. Update logo link
code = re.sub(
    r'<Link href="/" className="text-sm font-medium text-slate-300 hover:text-white transition-colors flex items-center gap-1">\s*<AlertTriangle className="h-4 w-4" />\s*Home\s*</Link>',
    r'',
    code
)

code = re.sub(
    r'<span className="text-sm font-bold tracking-widest text-slate-100">Don\'tCollapse Dashboard</span>',
    r'<Link href="/" className="text-sm font-bold tracking-widest text-slate-100 hover:text-white cursor-pointer flex items-center gap-2">\n          <AlertTriangle className="h-4 w-4 text-emerald-500" />\n          DontCollapse\n        </Link>',
    code
)

# 2. Add Typewriter
typewriter_code = """
const TypewriterText = ({ text }: { text: string }) => {
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
}

"""
if 'TypewriterText' not in code:
    code = code.replace('export default function Dashboard() {', typewriter_code + 'export default function Dashboard() {')

# 3. Minimizable Intelligence Panel
if 'isPanelOpen' not in code:
    code = code.replace('const [showFragilityInfo, setShowFragilityInfo] = useState(false);',
                        'const [showFragilityInfo, setShowFragilityInfo] = useState(false);\n  const [isPanelOpen, setIsPanelOpen] = useState(true);')

code = code.replace(
    '<div className="rounded-xl bg-slate-900/40 p-4 backdrop-blur-md shadow-lg border border-slate-800/50">\n          <p className="mb-4 text-[10px] font-bold uppercase tracking-wider text-slate-400">Intelligence Panel</p>',
    """<div className="rounded-xl bg-slate-900/40 backdrop-blur-md shadow-lg border border-slate-800/50 overflow-hidden transition-all duration-300">
          <button onClick={() => setIsPanelOpen(!isPanelOpen)} className="w-full p-4 flex items-center justify-between hover:bg-slate-800/30 transition-colors">
            <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Intelligence Panel</p>
            <span className="text-slate-500 text-xs">{isPanelOpen ? '▼' : '▲'}</span>
          </button>
          <div className={`px-4 pb-4 transition-all duration-500 ease-in-out ${isPanelOpen ? 'opacity-100 max-h-[1000px]' : 'opacity-0 max-h-0 pb-0 overflow-hidden'}`}>"""
)

code = code.replace(
    '</div>\n      </section>\n\n      <aside',
    '</div>\n        </div>\n      </section>\n\n      <aside'
)

# 4. Typewriter narrative usage
code = code.replace(
    '<p className="text-[12.5px] leading-relaxed text-slate-300">{apiData ? apiData.narrative : scenarioState.summary}</p>',
    '<p className="text-[12.5px] leading-relaxed text-slate-300"><TypewriterText text={apiData ? apiData.narrative : scenarioState.summary} /></p>'
)

# 5. Make all scores visible
# Some scores were missing because we took top 3. Let's make sure it still maps cleanly.
# The user might have meant the side UI where it says "Area Focus"

with open(path, 'w') as f:
    f.write(code)

