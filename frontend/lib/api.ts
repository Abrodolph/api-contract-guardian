import type { Verdict } from './types'

const BACKEND = 'http://localhost:8000'

export async function fetchVerdicts(): Promise<Verdict[]> {
  const res = await fetch(`${BACKEND}/verdicts`, { cache: 'no-store' })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}

export async function fetchVerdict(id: string): Promise<Verdict> {
  const res = await fetch(`${BACKEND}/verdicts/${id}`, { cache: 'no-store' })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}
