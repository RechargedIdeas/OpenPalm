import { useRef, useEffect } from "react";
import { useUI, BottomTab } from "../../stores/ui";
import { TerminalTab } from "./TerminalTab";
import { ActivityLogTab } from "./ActivityLogTab";
import { DebugTab } from "./DebugTab";

export function BottomBar() {
  const {
    bottomCollapsed,
    bottomMaximized,
    bottomHeight,
    bottomTab,
    debugEnabled,
    setBottomCollapsed,
    setBottomMaximized,
    setBottomHeight,
    setBottomTab,
  } = useUI();

  const dragRef = useRef<HTMLDivElement>(null);
  const startY = useRef(0);
  const startH = useRef(0);

  useEffect(() => {
    const onMove = (e: MouseEvent) => {
      if (!dragRef.current?.dataset.dragging) return;
      const delta = startY.current - e.clientY;
      const next = Math.max(80, Math.min(window.innerHeight * 0.6, startH.current + delta));
      setBottomHeight(next);
    };
    const onUp = () => {
      if (dragRef.current) delete dragRef.current.dataset.dragging;
    };
    window.addEventListener("mousemove", onMove);
    window.addEventListener("mouseup", onUp);
    return () => {
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("mouseup", onUp);
    };
  }, [setBottomHeight]);

  if (bottomCollapsed) return null;

  const tabs: { id: BottomTab; label: string }[] = [
    { id: "terminal", label: "Terminal" },
    { id: "activity", label: "Activity Log" },
    ...(debugEnabled ? [{ id: "debug" as BottomTab, label: "Debug" }] : []),
  ];

  return (
    <div
      style={{
        height: bottomMaximized ? "calc(100vh - 48px)" : bottomHeight,
        display: "flex",
        flexDirection: "column",
        borderTop: "1px solid #313244",
        background: "#181825",
        flexShrink: 0,
      }}
    >
      <div
        ref={dragRef}
        onMouseDown={(e) => {
          if (bottomMaximized) return;
          startY.current = e.clientY;
          startH.current = bottomHeight;
          if (dragRef.current) dragRef.current.dataset.dragging = "1";
        }}
        style={{ height: 6, cursor: bottomMaximized ? "default" : "ns-resize", background: "#313244" }}
      />
      <div style={{ display: "flex", alignItems: "center", padding: "4px 8px", gap: 4, borderBottom: "1px solid #313244" }}>
        {tabs.map((t) => (
          <button
            key={t.id}
            onClick={() => setBottomTab(t.id)}
            style={{
              background: bottomTab === t.id ? "#313244" : "transparent",
              border: "none",
              color: "#cdd6f4",
              padding: "4px 10px",
              borderRadius: 4,
              cursor: "pointer",
              fontSize: 12,
            }}
          >
            {t.label}
          </button>
        ))}
        <div style={{ flex: 1 }} />
        <button
          onClick={() => setBottomMaximized(!bottomMaximized)}
          style={{ background: "none", border: "none", color: "#cdd6f4", cursor: "pointer", fontSize: 14 }}
          title={bottomMaximized ? "Restore" : "Maximize"}
        >
          {bottomMaximized ? "🗗" : "⬜"}
        </button>
        <button
          onClick={() => { setBottomCollapsed(true); setBottomMaximized(false); }}
          style={{ background: "none", border: "none", color: "#cdd6f4", cursor: "pointer", fontSize: 14 }}
          title="Collapse"
        >
          ─
        </button>
      </div>
      <div style={{ flex: 1, overflow: "hidden" }}>
        {bottomTab === "terminal" && <TerminalTab />}
        {bottomTab === "activity" && <ActivityLogTab />}
        {bottomTab === "debug" && debugEnabled && <DebugTab />}
      </div>
    </div>
  );
}
