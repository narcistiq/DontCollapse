export type ScenarioKey = "heavy rainfall" | "storm surge" | "sea-level-rise increase" | "repeated flooding days";

export type ActionTicket = {
  id: string;
  title: string;
  detail: string;
  urgency: "critical" | "warning" | "stable";
};

export type RankedArea = {
  name: string;
  score: number;
  reason: string;
};

export type InfrastructureScore = {
  id: "roads" | "intersections" | "drainage" | "power" | "access-routes";
  label: string;
  score: number;
};

export type ScenarioState = {
  summary: string;
  score: number;
  affected: string;
  actions: ActionTicket[];
  logs: string[];
  rankedAreas: RankedArea[];
  infrastructureScores: InfrastructureScore[];
  actionPayload: {
    action: string;
    coordinates: [number, number][];
  };
};

export type FeatureCollection = GeoJSON.FeatureCollection<
  GeoJSON.Geometry,
  { [name: string]: string | number }
>;
