import { UIProvider } from "./stores/ui";
import { AppShell } from "./components/layout/AppShell";
import "./App.css";

function App() {
  return (
    <UIProvider>
      <AppShell />
    </UIProvider>
  );
}

export default App;
