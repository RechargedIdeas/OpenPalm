import { Sidebar } from "./Sidebar";
import { TopBar } from "./TopBar";
import { useUI } from "../../stores/ui";
import { ChatView } from "../../views/Chat";
import { FilesView } from "../../views/Files";
import { EmailView } from "../../views/Email";
import { MlsCsvView } from "../../views/MlsCsv";
import { ChartsView } from "../../views/Charts";
import { SettingsView } from "../../views/Settings";
import { TrainingView } from "../../views/Training";
import { ModelsView } from "../../views/Models";
import { WatchdogView } from "../../views/Watchdog";
import { SystemView } from "../../views/System";
import { ActivityView } from "../../views/Activity";
import { BottomBar } from "../bottom/BottomBar";
import { ManualOverlay } from "../manual/ManualOverlay";

export function AppShell() {
  const { activeView, bottomMaximized, bottomCollapsed, setBottomCollapsed, manualOpen, manualChapter, setManualOpen } = useUI();

  const views: Record<string, JSX.Element> = {
    chat: <ChatView />,
    files: <FilesView />,
    email: <EmailView />,
    mls: <MlsCsvView />,
    charts: <ChartsView />,
    models: <ModelsView />,
    watchdog: <WatchdogView />,
    training: <TrainingView />,
    system: <SystemView />,
    activity: <ActivityView />,
    settings: <SettingsView />,
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh", background: "var(--bg)", color: "var(--text)" }}>
      <TopBar />
      <div style={{ display: "flex", flex: 1, overflow: "hidden" }}>
        <Sidebar />
        <main
          style={{
            flex: 1,
            overflow: "auto",
            display: bottomMaximized ? "none" : "block",
          }}
        >
          {views[activeView]}
        </main>
      </div>
      {bottomCollapsed && (
        <button
          onClick={() => setBottomCollapsed(false)}
          style={{
            position: "fixed",
            bottom: 8,
            right: 8,
            background: "var(--surface)",
            border: "1px solid var(--border)",
            color: "var(--text)",
            padding: "6px 12px",
            borderRadius: 4,
            cursor: "pointer",
            fontSize: 12,
          }}
        >
          Terminal
        </button>
      )}
      <BottomBar />
      <ManualOverlay open={manualOpen} onClose={() => setManualOpen(false)} initialChapter={manualChapter} />
    </div>
  );
}
