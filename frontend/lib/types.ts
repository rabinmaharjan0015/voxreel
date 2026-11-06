export type VideoType = { id: string; name: string; emoji: string; aspect: string; blurb: string; scenes: number };
export type Provider = { id: string; name: string; free: boolean; needs_key: boolean; note: string; models: string[] };
export type Language = { code: string; name: string };
export type Catalog = {
  video_types: VideoType[];
  providers: { llm: Provider[]; tts: Provider[]; visuals: Provider[]; publish: Provider[] };
  voices: Record<string, string[]>;
  languages: Language[];
};
export type Job = {
  id: string; status: "queued" | "running" | "done" | "error"; step: string;
  progress: number; title: string | null; topic: string; video_type: string; created_at: number; video_url: string | null; error: string | null;
};
export type Connections = Record<"youtube" | "tiktok", { configured: boolean; connected: boolean }>;
export type Publication = { id: string; platform: string; status: "queued" | "running" | "done" | "error"; url: string | null; note: string | null; error: string | null };
