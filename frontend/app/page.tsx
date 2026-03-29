"use client";

import { Canvas } from "@react-three/fiber";
import Lenis from "lenis";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { ArrowRight } from "lucide-react";
import Link from "next/link";
import { useEffect, useRef, useState } from "react";

import { ResilienceModel } from "../components/landing/ResilienceModel";

gsap.registerPlugin(ScrollTrigger);

export default function HomePage() {
  const lenisRef = useRef<Lenis | null>(null);
  const bgLayerRef = useRef<HTMLDivElement | null>(null);
  const [activeSection, setActiveSection] = useState<"hero" | "threat" | "solution" | "final">("hero");

  useEffect(() => {
    const lenis = new Lenis({
      duration: 1.1,
      smoothWheel: true,
      wheelMultiplier: 0.9,
      touchMultiplier: 1.2
    });
    lenisRef.current = lenis;

    lenis.on("scroll", ScrollTrigger.update);

    const gradients: Record<string, string> = {
      hero:
        "linear-gradient(128deg, rgba(11,22,48,0.995) 0%, rgba(22,54,116,0.99) 52%, rgba(34,82,146,0.985) 100%), radial-gradient(130% 100% at 14% 20%, rgba(145,222,255,0.9), transparent 57%), radial-gradient(105% 85% at 84% 74%, rgba(139,255,241,0.72), transparent 61%)",
      threat:
        "linear-gradient(128deg, rgba(18,12,30,0.995) 0%, rgba(52,28,78,0.99) 50%, rgba(120,34,66,0.985) 100%), radial-gradient(130% 100% at 16% 20%, rgba(174,205,255,0.84), transparent 57%), radial-gradient(105% 85% at 84% 74%, rgba(255,168,206,0.78), transparent 61%)",
      solution:
        "linear-gradient(128deg, rgba(7,22,34,0.995) 0%, rgba(18,58,74,0.99) 52%, rgba(16,94,96,0.985) 100%), radial-gradient(130% 100% at 14% 20%, rgba(161,231,255,0.86), transparent 57%), radial-gradient(105% 85% at 84% 74%, rgba(151,255,222,0.74), transparent 61%)",
      final:
        "linear-gradient(128deg, rgba(9,25,42,0.995) 0%, rgba(24,56,96,0.99) 52%, rgba(36,82,144,0.985) 100%), radial-gradient(130% 100% at 14% 20%, rgba(160,226,255,0.84), transparent 57%), radial-gradient(105% 85% at 84% 74%, rgba(176,210,255,0.74), transparent 61%)"
    };

    const sections = ["hero", "threat", "solution", "final"] as const;
    const triggers = sections.map((id) =>
      ScrollTrigger.create({
        trigger: `#${id}`,
        start: "top center",
        end: "bottom center",
        onEnter: () => {
          setActiveSection(id);
          if (bgLayerRef.current) {
            gsap.to(bgLayerRef.current, {
              background: gradients[id],
              duration: 0.65,
              ease: "power2.out"
            });
          }
        },
        onEnterBack: () => {
          setActiveSection(id);
          if (bgLayerRef.current) {
            gsap.to(bgLayerRef.current, {
              background: gradients[id],
              duration: 0.65,
              ease: "power2.out"
            });
          }
        }
      })
    );

    const tick = (time: number) => {
      lenis.raf(time);
      requestAnimationFrame(tick);
    };

    requestAnimationFrame(tick);

    return () => {
      triggers.forEach((trigger) => trigger.kill());
      lenis.destroy();
      lenisRef.current = null;
    };
  }, []);

  return (
    <main id="landing-root" className="relative min-h-[405vh] bg-slate-950 text-slate-100">
      <div className="pointer-events-none fixed inset-0 z-10">
        <Canvas camera={{ position: [0, 0, 7], fov: 45 }}>
          <ResilienceModel />
        </Canvas>
      </div>

      <div 
        ref={bgLayerRef}
        className="pointer-events-none fixed inset-0 z-0 bg-slate-950 transition-[background] duration-700"
      />
      
      {/* Animated Subtle Heatmap Gradients mimicking map colors */}
      <div 
        id="heat-layer"
        className="pointer-events-none fixed inset-0 z-0 opacity-20 mix-blend-color-dodge transition-all duration-1000 bg-[radial-gradient(40%_40%_at_30%_30%,rgba(34,197,94,0.3),transparent_80%),radial-gradient(50%_50%_at_80%_60%,rgba(249,115,22,0.3),transparent_70%),radial-gradient(40%_40%_at_60%_20%,rgba(220,38,38,0.3),transparent_80%)]" 
      />
      
      {/* Moving dots/grid to simulate a scrolling map abstractly */}
      {/* Taller div so it can scroll upwards infinitely */}
      <div className="pointer-events-none fixed left-0 top-0 w-full h-[200vh] z-0 opacity-[0.06] bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] bg-repeat animate-[slide_120s_linear_infinite]" />
      
      {/* Dark overlay to ensure text readability */}
      <div className="pointer-events-none fixed inset-0 z-0 bg-slate-950/75 mix-blend-multiply" />

      <div className="fixed left-0 right-0 top-4 z-20 flex justify-center px-6">
        <div className="flex items-center gap-2 rounded-full border border-slate-700 bg-slate-900/75 p-1.5 backdrop-blur-md">
          {[
            { id: "hero", label: "Hero" },
            { id: "threat", label: "Threat" },
            { id: "solution", label: "Solution" },
            { id: "final", label: "Final" }
          ].map((item) => (
            <button
              key={item.id}
              type="button"
              onClick={() => lenisRef.current?.scrollTo(`#${item.id}`, { duration: 1.1 })}
              className={[
                "rounded-full px-3 py-1.5 text-[11px] font-medium transition",
                activeSection === item.id ? "bg-blue-500/30 text-blue-100" : "text-slate-300 hover:bg-slate-700/60"
              ].join(" ")}
            >
              {item.label}
            </button>
          ))}
        </div>
      </div>

      <section id="hero" className="relative z-10 flex min-h-screen items-center px-6 pt-16 md:px-14">
        <div className="max-w-4xl">
          <p className="mb-5 text-xs uppercase tracking-[0.35em] text-blue-300/80">DontCollapse</p>
          <h1 className="text-5xl font-semibold leading-[0.95] tracking-tight text-slate-100 md:text-8xl">
            PREDICT.
            <br />
            ADAPT.
            <br />
            SURVIVE.
          </h1>
          <p className="mt-6 max-w-xl text-base text-slate-400 md:text-lg">
            The Autonomous Resilience Ecosystem for Florida's infrastructure. We synthesize weather APIs, bulk DataFrame simulations, and multi-LLM workflows to mathematically predict structural fragility across 2,780+ mapped sub-zones before critical limits cascade.
          </p>

          <div className="mt-6 grid max-w-2xl grid-cols-3 gap-3 rounded-xl border border-slate-800 bg-slate-900/50 p-3 backdrop-blur-sm">
            <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-3">
              <p className="text-2xl font-semibold text-white">6</p>
              <p className="text-xs uppercase tracking-wide text-slate-400">Scenarios</p>
            </div>
            <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-3">
              <p className="text-2xl font-semibold text-white">3</p>
              <p className="text-xs uppercase tracking-wide text-slate-400">AI Agents</p>
            </div>
            <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-3">
              <p className="text-2xl font-semibold text-white">1</p>
              <p className="text-xs uppercase tracking-wide text-slate-400">Shared Reality</p>
            </div>
          </div>

          <p className="mt-4 text-xs uppercase tracking-[0.18em] text-slate-400">Scroll to drive the globe timeline</p>
        </div>
      </section>

      <section id="threat" className="relative z-10 flex min-h-screen items-center justify-start px-6 md:px-14">
        <div className="max-w-md rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-sm">
          <p className="mb-2 text-xs uppercase tracking-[0.2em] text-rose-300">The Threat</p>
          <h2 className="mb-3 text-3xl font-semibold tracking-tight text-slate-100">Fragility Is Accelerating</h2>
          <p className="text-sm text-slate-400">
            Extreme weather and systemic stress test the limits of our public structures. DontCollapse maps hyper-local fragility percentiles across key vectors—from roads to essential facilities—pinpointing exactly where infrastructure will collapse first.
          </p>

          <div className="mt-5 rounded-lg border border-slate-800 bg-slate-950/65 p-3">
            <p className="mb-2 text-[10px] uppercase tracking-[0.18em] text-slate-400">Threat Color Compare</p>
            <div className="grid grid-cols-4 gap-2">
              {[
                { label: "Roads", color: "#f43f5e", score: "84" },
                { label: "Intersections", color: "#f59e0b", score: "73" },
                { label: "Drainage", color: "#eab308", score: "64" },
                { label: "Access", color: "#22c55e", score: "41" }
              ].map((item) => (
                <div key={item.label} className="rounded-md border border-slate-800 bg-slate-900/55 p-2 text-center">
                  <div className="mx-auto h-2.5 w-full rounded-full" style={{ backgroundColor: item.color }} />
                  <p className="mt-2 text-[10px] uppercase tracking-wide text-slate-300">{item.label}</p>
                  <p className="text-xs font-semibold text-white">{item.score}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section id="solution" className="relative z-10 flex min-h-screen items-center justify-end px-6 md:px-14">
        <div className="max-w-md rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-sm">
          <p className="mb-2 text-xs uppercase tracking-[0.2em] text-emerald-300">The Multi-Agent Solution</p>
          <h2 className="mb-3 text-3xl font-semibold tracking-tight text-slate-100">Tri-Node Intelligence.</h2>
          <p className="text-sm text-slate-400">
            A specialized network of asynchronous AI agents continuously processes telemetry, evaluates deterministic risk models, and drives operational readiness.
          </p>

          <div className="mt-5 flex flex-col gap-3">
            {[
              { 
                name: "Sentinel", 
                role: "Early Warning", 
                desc: "Ingests live environmental APIs (e.g. Open-Meteo) and leverages Groq LLMs to continuously observe and generate context-aware status reports.",
                accent: "from-cyan-400 to-sky-500", delay: "0ms" 
              },
              { 
                name: "Simulator", 
                role: "Risk & Prediction", 
                desc: "Runs high-speed, deterministic bulk Pandas processing to dynamically map cascading fragility across 2,783 geographic sub-zones based on active scenarios.",
                accent: "from-violet-400 to-fuchsia-500", delay: "180ms" 
              },
              { 
                name: "Dispatcher", 
                role: "Operations & A2A", 
                desc: "Consolidates findings and formulates mitigation logistics. Simulates Agent-to-Agent (A2A) handshakes to trigger supply allocations down the chain.",
                accent: "from-emerald-400 to-teal-500", delay: "360ms" 
              }
            ].map((agent) => (
              <div key={agent.name} className="flex items-center gap-4 rounded-md border border-slate-700 bg-slate-950/70 p-3 pt-3.5 pb-3.5">
                <div className="relative flex-shrink-0 flex h-12 w-12 items-center justify-center">
                  <div
                    className="absolute h-12 w-12 rounded-full border border-cyan-200/40 animate-spin"
                    style={{ animationDuration: "4.8s", animationDelay: agent.delay }}
                  />
                  <div
                    className="absolute h-8 w-8 rounded-full border border-white/35 animate-spin"
                    style={{ animationDuration: "3.3s", animationDirection: "reverse", animationDelay: agent.delay }}
                  />
                  <div className={`h-3 w-3 rounded-full bg-gradient-to-br ${agent.accent} animate-pulse`} />
                  <span
                    className="absolute h-1.5 w-1.5 rounded-full bg-white/90 animate-ping"
                    style={{ animationDuration: "1.8s", animationDelay: agent.delay }}
                  />
                </div>
                <div className="flex flex-col text-left">
                  <div className="flex items-baseline gap-2 mb-1">
                    <p className="text-[13px] font-bold uppercase tracking-[0.12em] text-slate-200">{agent.name}</p>
                    <span className="text-[9px] uppercase tracking-widest text-slate-500">{agent.role}</span>
                  </div>
                  <p className="text-[11.5px] leading-snug text-slate-400">{agent.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section id="final" className="relative z-10 block min-h-[70vh]">
        {/* Spacer for final section scroll */}
      </section>

      <div className={`fixed inset-0 z-10 flex flex-col items-center justify-center px-6 transition-all duration-1000 ${
        activeSection === "final" ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8 pointer-events-none"
      }`}>
        <div className="w-full max-w-2xl text-center">
          <p className="text-xs uppercase tracking-[0.22em] text-slate-400">Operational Layer</p>
          <h2 className="mt-2 text-4xl font-semibold tracking-tight text-slate-100 md:text-5xl delay-100 transition-all">Ready to Enter the Live Map</h2>
          <p className="mx-auto mt-3 max-w-xl text-sm text-slate-400 md:text-base delay-200 transition-all">
            Transition from narrative intelligence to scenario-level action planning in the dashboard.
          </p>
        </div>
      </div>

      <div className="fixed bottom-8 left-0 right-0 z-20 flex justify-center px-6">
        <Link
          href="/dashboard"
          className="inline-flex items-center gap-2 rounded-full border border-blue-400/60 bg-slate-900/85 px-6 py-3 text-sm font-medium text-blue-100 shadow-[0_0_35px_rgba(59,130,246,0.35)] backdrop-blur-md transition hover:bg-blue-500/25"
        >
          Go to Dashboard
          <ArrowRight className="h-4 w-4" />
        </Link>
      </div>
    </main>
  );
}
