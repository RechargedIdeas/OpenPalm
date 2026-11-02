import { createContext, useContext, useState, useEffect, ReactNode } from "react";

export type View = "chat" | "files" | "email" | "mls" | "charts" | "models" | "watchdog" | "training" | "system" | "settings";
export type BottomTab = "terminal" | "activity" | "debug";
export type Theme = "dark" | "light";

interface UIState {
  activeView: View;
  sidebarCollapsed: boolean;
  bottomCollapsed: boolean;
  bottomMaximized: boolean;
  bottomHeight: number;
  bottomTab: BottomTab;
  debugEnabled: boolean;
  manualOpen: boolean;
  manualChapter: string;
  theme: Theme;
  setActiveView: (view: View) => void;
  toggleSidebar: () => void;
  setBottomCollapsed: (v: boolean) => void;
  setBottomMaximized: (v: boolean) => void;
  setBottomHeight: (h: number) => void;
  setBottomTab: (t: BottomTab) => void;
  setDebugEnabled: (v: boolean) => void;
  setManualOpen: (v: boolean) => void;
  setManualChapter: (c: string) => void;
  toggleTheme: () => void;
}

const UIContext = createContext<UIState | null>(null);

const THEME_KEY = "openpalm-theme";

function loadTheme(): Theme {
  try {
    const stored = localStorage.getItem(THEME_KEY);
    if (stored === "light" || stored === "dark") return stored;
  } catch {}
  return "dark";
}

export function UIProvider({ children }: { children: ReactNode }) {
  const [activeView, setActiveView] = useState<View>("chat");
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [bottomCollapsed, setBottomCollapsed] = useState(false);
  const [bottomMaximized, setBottomMaximized] = useState(false);
  const [bottomHeight, setBottomHeight] = useState(220);
  const [bottomTab, setBottomTab] = useState<BottomTab>("terminal");
  const [debugEnabled, setDebugEnabled] = useState(false);
  const [manualOpen, setManualOpen] = useState(false);
  const [manualChapter, setManualChapter] = useState("getting-started");
  const [theme, setTheme] = useState<Theme>(loadTheme);

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    try {
      localStorage.setItem(THEME_KEY, theme);
    } catch {}
  }, [theme]);

  const toggleTheme = () => setTheme((t) => (t === "dark" ? "light" : "dark"));

  return (
    <UIContext.Provider
      value={{
        activeView,
        sidebarCollapsed,
        bottomCollapsed,
        bottomMaximized,
        bottomHeight,
        bottomTab,
        debugEnabled,
        manualOpen,
        manualChapter,
        theme,
        setActiveView,
        toggleSidebar: () => setSidebarCollapsed((c) => !c),
        setBottomCollapsed,
        setBottomMaximized,
        setBottomHeight,
        setBottomTab,
        setDebugEnabled,
        setManualOpen,
        setManualChapter,
        toggleTheme,
      }}
    >
      {children}
    </UIContext.Provider>
  );
}

export function useUI() {
  const ctx = useContext(UIContext);
  if (!ctx) throw new Error("useUI must be used within UIProvider");
  return ctx;
}
