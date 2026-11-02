export interface SlashCommand {
  name: string;
  description: string;
  args?: string;
}

export const COMMANDS: SlashCommand[] = [
  { name: "help", description: "Open the help manual", args: "[section]" },
  { name: "clear", description: "Clear conversation history" },
  { name: "model", description: "Switch the active model", args: "[name]" },
  { name: "facts", description: "Set verification pass count", args: "[1|2|3]" },
  { name: "files", description: "Open the file browser" },
  { name: "email", description: "Open the email view" },
  { name: "sync", description: "Re-index folders and email" },
  { name: "status", description: "Show model, memory, index size, verification level" },
  { name: "logs", description: "Switch to the Activity Log tab" },
  { name: "debug", description: "Toggle Debug tab visibility" },
  { name: "exit", description: "Quit the application" },
];

export function filterCommands(prefix: string): SlashCommand[] {
  const p = prefix.toLowerCase().replace(/^\//, "");
  if (!p) return COMMANDS;
  return COMMANDS.filter((c) => c.name.startsWith(p));
}

export function parseCommand(input: string): { name: string; args: string[] } | null {
  if (!input.startsWith("/")) return null;
  const parts = input.slice(1).trim().split(/\s+/);
  const name = parts[0]?.toLowerCase();
  if (!name) return null;
  return { name, args: parts.slice(1) };
}
