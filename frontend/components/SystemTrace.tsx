import { useEffect, useState, useRef } from "react";
import { Loader2, Code2, Cpu, FileJson, ServerCog, Workflow } from "lucide-react";

interface SystemTraceProps {
  logs: string[];
  isLoading?: boolean;
}

const getAgentIcon = (line: string) => {
  if (line.toLowerCase().includes("sentinel")) return <ServerCog className="w-3 h-3 text-blue-400" />;
  if (line.toLowerCase().includes("simulator")) return <Cpu className="w-3 h-3 text-purple-400" />;
  if (line.toLowerCase().includes("dispatcher")) return <Workflow className="w-3 h-3 text-amber-400" />;
  if (line.toLowerCase().includes("groq")) return <Code2 className="w-3 h-3 text-rose-400" />;
  return <FileJson className="w-3 h-3 text-emerald-400" />;
};

export function SystemTrace({ logs, isLoading }: SystemTraceProps) {
  const [visibleLogs, setVisibleLogs] = useState<string[]>([]);
  const logEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setVisibleLogs([]);
    if (!logs.length) return;
    
    const timers: number[] = [];
    logs.forEach((line, index) => {
      const timer = window.setTimeout(() => {
        setVisibleLogs((prev) => [...prev, line]);
      }, 300 * (index + 1) + Math.random() * 200);
      timers.push(timer);
    });

    return () => {
      timers.forEach((timer) => window.clearTimeout(timer));
    };
  }, [logs]);

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [visibleLogs]);

  return (
    <div className="flex flex-col h-full w-full bg-slate-950/40">
      <div className="flex items-center justify-between border-b border-slate-800/80 bg-slate-950/80 px-2 py-1.5 shrink-0">
        <div className="flex items-center gap-2">
          {isLoading && <Loader2 className="w-3 h-3 animate-spin text-slate-400" />}
          <span className="text-[10px] uppercase font-bold tracking-widest text-slate-300">Live Execution</span>
        </div>
        <span className="text-[9px] font-mono text-slate-500">live-trace</span>
      </div>

      <div
        className="h-32 overflow-y-auto p-2 font-mono text-[10px] space-y-1.5 custom-scrollbar"
        role="log"
        aria-live="polite"
        aria-relevant="additions"
      >
        {visibleLogs.length === 0 ? (
          <p className="animate-pulse text-slate-500 px-1">
            {isLoading ? "Starting execution pipelines..." : "System idle."}
          </p>
        ) : (
          <>
            {visibleLogs.map((line, index) => (
              <div key={`${line}-${index}`} className="flex animate-fade-in-up items-start gap-1.5 rounded bg-slate-900/40 p-1.5 border border-slate-800/50">
                <div className="mt-0.5 shrink-0 opacity-80">{getAgentIcon(line)}</div>
                <div className="flex-1 text-slate-300 leading-relaxed tracking-tight break-all">
                  {line}
                </div>
              </div>
            ))}
            <div ref={logEndRef} />
          </>
        )}
      </div>
    </div>
  );
}
