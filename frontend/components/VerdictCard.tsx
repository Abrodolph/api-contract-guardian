import Link from 'next/link'
import type { Verdict } from '@/lib/types'
import { VerdictBadge } from './VerdictBadge'
import { timeAgo } from '@/lib/time'

const LEFT_BORDER: Record<string, string> = {
  BREAKING: 'border-l-red-600',
  SAFE:     'border-l-emerald-600',
  REVIEW:   'border-l-amber-500',
}

export function VerdictCard({ verdict }: { verdict: Verdict }) {
  return (
    <Link
      href={`/verdict/${verdict.id}`}
      className={`group flex items-start gap-5 rounded-lg bg-[#161b22] border border-[#30363d] border-l-4 ${LEFT_BORDER[verdict.verdict]} px-5 py-4 transition-colors hover:bg-[#1c2128] hover:border-[#444c56]`}
    >
      <div className="flex-1 min-w-0 space-y-2">
        <div className="flex items-center gap-3 flex-wrap">
          <VerdictBadge verdict={verdict.verdict} />
          <span
            className="text-xs text-[#8b949e]"
            suppressHydrationWarning
          >
            {timeAgo(verdict.created_at)}
          </span>
        </div>

        <p className="text-[#e6edf3] text-sm font-medium leading-relaxed">
          {verdict.change_summary}
        </p>

        {verdict.affected_field && (
          <div className="flex items-center gap-2">
            <span className="text-xs text-[#8b949e]">Affected field</span>
            <code className="text-xs font-mono bg-[#0d1117] text-[#79c0ff] px-2 py-0.5 rounded border border-[#30363d]">
              {verdict.affected_field}
            </code>
          </div>
        )}
      </div>

      {verdict.verdict === 'BREAKING' && verdict.blast_radius?.total_call_sites > 0 && (
        <div className="shrink-0 text-right pt-0.5">
          <div className="text-2xl font-bold tabular-nums text-red-500 leading-none">
            {verdict.blast_radius.total_call_sites}
          </div>
          <div className="text-[10px] text-[#8b949e] mt-1 uppercase tracking-wide">
            call sites
          </div>
        </div>
      )}

      <div className="shrink-0 pt-1 text-[#444c56] group-hover:text-[#8b949e] transition-colors">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5l7 7-7 7" />
        </svg>
      </div>
    </Link>
  )
}
