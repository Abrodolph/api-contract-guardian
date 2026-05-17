'use client'

import { useEffect, useState, useCallback } from 'react'
import type { Verdict } from '@/lib/types'
import { VerdictCard } from './VerdictCard'

interface Props {
  initial: Verdict[]
}

export function VerdictList({ initial }: Props) {
  const [verdicts, setVerdicts] = useState<Verdict[]>(initial)
  const [status, setStatus] = useState<'ok' | 'error' | 'stale'>('ok')
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date())

  const safeVerdicts = Array.isArray(verdicts) ? verdicts : []

  const poll = useCallback(async () => {
    try {
      const res = await fetch('https://api-contract-guardian-1.onrender.com/verdicts')
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data: Verdict[] = await res.json()
      setVerdicts(data)
      setLastUpdated(new Date())
      setStatus('ok')
    } catch {
      setStatus('error')
    }
  }, [])

  useEffect(() => {
    const id = setInterval(poll, 10_000)
    return () => clearInterval(id)
  }, [poll])

  const breaking = safeVerdicts.filter(v => v.verdict === 'BREAKING').length
  const review   = safeVerdicts.filter(v => v.verdict === 'REVIEW').length
  const safe     = safeVerdicts.filter(v => v.verdict === 'SAFE').length

  return (
    <div>
      {/* Stats + live bar */}
      <div className="flex items-center gap-6 mb-6 pb-5 border-b border-[#21262d] flex-wrap">
        <StatCount value={breaking} label="Breaking" color="text-red-500" />
        <div className="w-px h-5 bg-[#21262d]" />
        <StatCount value={review}   label="Review"   color="text-amber-500" />
        <div className="w-px h-5 bg-[#21262d]" />
        <StatCount value={safe}     label="Safe"     color="text-emerald-500" />

        <div className="ml-auto flex items-center gap-2">
          {status === 'error' ? (
            <span className="text-xs text-red-400">Backend unreachable</span>
          ) : (
            <span className="text-xs text-[#8b949e]" suppressHydrationWarning>
              Live · {lastUpdated.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
            </span>
          )}
          <span
            className={`w-2 h-2 rounded-full ${
              status === 'error' ? 'bg-red-500' : 'bg-emerald-500 animate-pulse'
            }`}
          />
        </div>
      </div>

      {/* List */}
      {safeVerdicts.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-24 text-center">
          <div className="w-12 h-12 rounded-full bg-[#161b22] border border-[#30363d] flex items-center justify-center mb-4">
            <svg className="w-5 h-5 text-[#8b949e]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
          </div>
          <p className="text-[#8b949e] text-sm">No verdicts yet.</p>
          <p className="text-[#484f58] text-xs mt-1">Run the contract guardian to generate results.</p>
        </div>
      ) : (
        <div className="flex flex-col gap-2">
          {safeVerdicts.map(v => (
            <VerdictCard key={v.id} verdict={v} />
          ))}
        </div>
      )}
    </div>
  )
}

function StatCount({ value, label, color }: { value: number; label: string; color: string }) {
  return (
    <div className="flex items-baseline gap-2">
      <span className={`text-2xl font-bold tabular-nums leading-none ${color}`}>{value}</span>
      <span className="text-xs text-[#8b949e] uppercase tracking-wider">{label}</span>
    </div>
  )
}
