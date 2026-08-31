export interface Player {
  trackId: number
  teamId: number
  x: number
  y: number
  confidence: number
}

export interface Event {
  event_type: string
  timestamp: number
  frame_id: number
  confidence: number
  players_involved: number[]
  metadata: Record<string, any>
}

export interface Match {
  sport_type: string
  start_time: string
  players: Record<number, Player>
  events: Event[]
}

export interface DistanceData {
  trackId: number
  distance: number
  highSpeed: number
}

export interface SprintData {
  start_time: number
  end_time: number
  duration_sec: number
  distance_m: number
  avg_speed_ms: number
}

export interface PlayerReport {
  trackId: number
  teamId: number
  heatmap: {
    grid: number[][]
    total_points: number
    max_density: number
  }
  distance: {
    total_distance_m: number
    high_speed_distance_m: number
    average_speed_ms: number
    max_speed_ms: number
  }
  sprints: SprintData[]
}

export interface HighlightWindow {
  start: number
  end: number
  score: number
}
