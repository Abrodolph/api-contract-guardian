export type VerdictType = 'BREAKING' | 'SAFE' | 'REVIEW'

export interface CallSite {
  file: string
  line: number
}

export interface Consumer {
  name: string
  call_sites: CallSite[]
}

export interface BlastRadius {
  consumers: Consumer[]
  total_call_sites: number
}

export interface Verdict {
  id: string
  verdict: VerdictType
  change_summary: string
  affected_field: string | null
  blast_radius: BlastRadius
  reasoning: string
  created_at: string
}
