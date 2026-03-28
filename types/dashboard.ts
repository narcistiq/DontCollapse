export type ScenarioKey = "heavy rainfall" | "storm surge" | "sea-level-rise increase" | "repeated flooding days";

export type ActionTicket = {
  id: string;
  title: string;
  detail: string;
  urgency: "critical" | "warning" | "stable";
};

export type ScenarioState = {
  summary: string;
  score: number;
  affected: string;
  actions: ActionTicket[];
  logs: string[];
};

export type FeatureCollection = GeoJSON.FeatureCollection<
  GeoJSON.Geometry,
  { [name: string]: string | number }
>;
