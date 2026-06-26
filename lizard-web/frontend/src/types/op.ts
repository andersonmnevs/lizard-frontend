export interface OpSummary {
  op: string
  last_updated: string | null
  total_hides: number
  avg_yield: number | null
  predominant_class: string | null
}

export interface ClassDistribution {
  class: string
  count: number
  pct: number
}

export interface OpDetail {
  op: string
  total_hides: number
  avg_area: number | null
  avg_yield: number | null
  class_distribution: ClassDistribution[]
}
