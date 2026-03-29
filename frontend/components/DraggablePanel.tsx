import React, { useState, useEffect, useRef } from "react";

interface DraggablePanelProps {
  id: string;
  title: string;
  visible: boolean;
  defaultPosition: { x: number; y: number };
  onClose: () => void;
  children: React.ReactNode;
  width?: string;
  className?: string;
}

export function DraggablePanel({ title, visible, defaultPosition, onClose, children, width, className }: DraggablePanelProps) {
  const [position, setPosition] = useState(defaultPosition);
  const [isDragging, setIsDragging] = useState(false);
  const dragStartPos = useRef({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isDragging) return;
      
      const dx = e.clientX - dragStartPos.current.x;
      const dy = e.clientY - dragStartPos.current.y;
      
      setPosition(prev => ({
        x: prev.x + dx,
        y: prev.y + dy
      }));
      
      dragStartPos.current = { x: e.clientX, y: e.clientY };
    };

    const handleMouseUp = () => setIsDragging(false);

    if (isDragging) {
      window.addEventListener("mousemove", handleMouseMove);
      window.addEventListener("mouseup", handleMouseUp);
    }

    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseup", handleMouseUp);
    };
  }, [isDragging]);

  if (!visible) return null;

  return (
    <div 
      className={`absolute z-30 flex flex-col rounded-lg border border-slate-800 bg-slate-950/90 shadow-2xl backdrop-blur-md overflow-hidden ${width || "w-80"} ${className || ""}`}
      style={{ left: position.x, top: position.y }}
    >
      <div 
        className="flex items-center justify-between border-b border-slate-800 bg-slate-900/80 px-3 py-2 cursor-grab active:cursor-grabbing select-none"
        onMouseDown={(e) => {
          setIsDragging(true);
          dragStartPos.current = { x: e.clientX, y: e.clientY };
        }}
      >
        <span className="text-[11px] font-bold uppercase tracking-widest text-slate-300">{title}</span>
        <button 
          onClick={onClose} 
          className="text-slate-500 hover:text-white"
        >
          &times;
        </button>
      </div>
      <div className="flex-1 overflow-y-auto custom-scrollbar">
        {children}
      </div>
    </div>
  );
}
