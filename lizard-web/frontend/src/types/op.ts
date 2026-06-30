export interface ClassDistribution {
  class: string
  count: number
  pct: number
}

export interface DashboardPeriod {
  total_hides: number
  avg_yield: number | null
}

export interface RecentOp {
  op: string
  date: string
  total_hides: number
}

export interface DashboardData {
  today: DashboardPeriod
  week: DashboardPeriod
  today_class_distribution: ClassDistribution[]
  recent_ops: RecentOp[]
}

export interface OpSummary {
  op: string
  last_updated: string | null
  total_hides: number
  avg_yield: number | null
  predominant_class: string | null
}

export interface OpDetail {
  op: string
  total_hides: number
  avg_area: number | null
  avg_yield: number | null
  class_distribution: ClassDistribution[]
}
