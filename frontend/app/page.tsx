"use client";

import { Canvas } from "@react-three/fiber";
import Lenis from "lenis";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { ArrowRight } from "lucide-react";
import Link from "next/link";
import { useEffect } from "react";

import { ResilienceModel } from "../components/landing/ResilienceModel";

gsap.registerPlugin(ScrollTrigger);

export default function HomePage() {
  useEffect(() => {
    const lenis = new Lenis({
      duration: 1.1,
      smoothWheel: true,
      wheelMultiplier: 0.9,
      touchMultiplier: 1.2
    });

    lenis.on("scroll", ScrollTrigger.update);

    const tick = (time: number) => {
      lenis.raf(time);
      requestAnimationFrame(tick);
    };

    requestAnimationFrame(tick);

    return () => {
      lenis.destroy();
    };
  }, []);

  return (
    <main id="landing-root" className="relative min-h-[500vh] bg-slate-950 text-slate-100">
      <div className="pointer-events-none fixed inset-0 z-0">
        <Canvas camera={{ position: [0, 0, 7], fov: 45 }}>
          <ResilienceModel />
        </Canvas>
      </div>

      <div className="pointer-events-none fixed inset-0 z-0 bg-[radial-gradient(circle_at_20%_20%,rgba(59,130,246,0.2),transparent_42%),radial-gradient(circle_at_85%_70%,rgba(20,184,166,0.16),transparent_34%)]" />

      <section className="relative z-10 flex min-h-screen items-center px-6 md:px-14">
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
            The Autonomous Resilience Ecosystem for Tampa Bay. Score fragility, understand cascading flood risk, and
            prioritize action before infrastructure fails.
          </p>

          <div className="mt-6 grid max-w-2xl grid-cols-3 gap-3 rounded-xl border border-slate-800 bg-slate-900/50 p-3 backdrop-blur-sm">
            <div className="rounded-lg border border-slate-800 bg-slate-950/60 p-3">
              <p className="text-2xl font-semibold text-white">4</p>
              <p className="text-xs uppercase tracking-wide text-slate-400">Flood Scenarios</p>
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

      <section className="relative z-10 flex min-h-screen items-center justify-start px-6 md:px-14">
        <div className="max-w-md rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-sm">
          <p className="mb-2 text-xs uppercase tracking-[0.2em] text-rose-300">The Threat</p>
          <h2 className="mb-3 text-3xl font-semibold tracking-tight text-slate-100">Fragility Is Accelerating</h2>
          <p className="text-sm text-slate-400">
            Water stress is destroying infrastructure. DontCollapse quantifies roads, drainage, and critical access
            vulnerabilities to identify where response must happen first.
          </p>
        </div>
      </section>

      <section className="relative z-10 flex min-h-screen items-center justify-end px-6 md:px-14">
        <div className="max-w-md rounded-xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-sm">
          <p className="mb-2 text-xs uppercase tracking-[0.2em] text-emerald-300">The Multi-Agent Solution</p>
          <h2 className="mb-3 text-3xl font-semibold tracking-tight text-slate-100">Three Agents. One Reality.</h2>
          <p className="text-sm text-slate-400">
            Sentinel ingest, parallel simulation, and loop-based dispatch collaborate in one shared context to produce
            mitigation actions in real time.
          </p>
        </div>
      </section>

      <section className="relative z-10 flex min-h-screen items-end justify-center px-6 pb-20 md:px-14">
        <div className="w-full max-w-3xl rounded-2xl border border-slate-700 bg-slate-900/70 p-8 text-center backdrop-blur-sm">
          <p className="mb-3 text-xs uppercase tracking-[0.2em] text-blue-300">Launch Sequence</p>
          <h2 className="text-4xl font-semibold tracking-tight text-white md:text-6xl">Launch The Dashboard</h2>
          <p className="mx-auto mt-4 max-w-xl text-sm text-slate-400 md:text-base">
            Move from narrative to operations. Enter the live fragility view and coordinate actions across neighborhoods,
            routes, and emergency infrastructure.
          </p>
        </div>
      </section>

      <div className="fixed bottom-5 left-0 right-0 z-20 flex justify-center px-6">
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
