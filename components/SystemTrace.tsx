"use client";

import { useEffect, useState, useRef } from "react";

interface SystemTraceProps {
  logs: string[];
  isLoading?: boolean;
}

export function SystemTrace({ logs, isLoading }: SystemTraceProps) {
  const [visibleLogs, setVisibleLogs] = useState<string[]>([]);
  const logEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const timers: number[] = [];

    logs.forEach((line, index) => {
      const timer = window.setTimeout(() => {
        setVisibleLogs((prev) => [...prev, line]);
      }, 420 * (index + 1));
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
    <section className="absolute bottom-4 right-4 z-30 w-[min(560px,calc(100%-2rem))] overflow-hidden rounded-lg border border-slate-800 bg-black/70 shadow-2xl backdrop-blur-md">
      <div className="flex items-center justify-between border-b border-slate-800 bg-slate-900 px-3 py-1">
        <div className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-rose-400" />
          <span className="h-2 w-2 rounded-full bg-amber-400" />
          <span className="h-2 w-2 rounded-full bg-emerald-400" />
        </div>
        <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-300">System Trace</p>
        <span className="text-[10px] font-mono text-slate-500">adk.runtime/live</span>
      </div>

      <div
        className="h-44 overflow-y-auto p-3 font-mono text-xs text-emerald-400/90"
        role="log"
        aria-live="polite"
        aria-relevant="additions"
      >
        {visibleLogs.length === 0 ? (
          <p className="animate-pulse text-slate-500">
            {isLoading ? "Executing agent workflows..." : "Awaiting agent execution logs..."}
          </p>
        ) : (
          <>
            {visibleLogs.map((line, index) => (
              <p key={`${line}-${index}`} className="animate-fade-in-up pb-1 leading-relaxed">
                <span className="mr-2 text-emerald-500/40">{">"}</span>
                {line}
              </p>
            ))}
            <div ref={logEndRef} />
          </>
        )}
      </div>
    </section>
  );
}
