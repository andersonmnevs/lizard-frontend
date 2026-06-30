export interface HideItem {
  id: number
  hide_num: string
  processed_at: string
  class: string
  yield_pct: number | null
  area: number | null
  op: string
}

export interface HideListResponse {
  items: HideItem[]
  total: number
  page: number
  limit: number
}

export interface Hide {
  id: number
  hide_num: string
  op: string
  processed_at: string
  class: string
  yield_pct: number | null
  area: number | null
  image_available: boolean
  prev_hide_id: number | null
  next_hide_id: number | null
}

export type HideDetail = Hide
