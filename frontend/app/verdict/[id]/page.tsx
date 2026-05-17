import Link from 'next/link'
import { notFound } from 'next/navigation'
import { fetchVerdict } from '@/lib/api'
import { VerdictBadge } from '@/components/VerdictBadge'
import { BlastRadius } from '@/components/BlastRadius'
import { ShieldIcon } from '@/components/ShieldIcon'
import { timeAgo } from '@/lib/time'

interface Props {
  params: { id: string }
}

export const dynamic = 'force-dynamic'

export default async function VerdictDetail({ params }: Props) {
  let verdict
  try {
    verdict = await fetchVerdict(params.id)
  } catch {
    notFound()
  }

  return (
    <div className="min-h-screen bg-[#0d1117]">
      {/* Header */}
      <header className="border-b border-[#21262d] bg-[#0d1117]/90 backdrop-blur-sm">
        <div className="max-w-3xl mx-auto px-6 py-4 flex items-center gap-4">
          <div className="flex items-center gap-3">
            <ShieldIcon />
            <h1 className="text-sm font-bold text-[#e6edf3] tracking-tight">API Contract Guardian</h1>
          </div>

          <div className="w-px h-5 bg-[#21262d] mx-1" />

          <Link
            href="/"
            className="flex items-center gap-1.5 text-xs text-[#8b949e] hover:text-[#e6edf3] transition-colors"
          >
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to verdicts
          </Link>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-6 py-8 space-y-8">
        {/* Summary card */}
        <div className="rounded-xl bg-[#161b22] border border-[#30363d] p-6">
          <div className="flex items-center gap-3 mb-4">
            <VerdictBadge verdict={verdict.verdict} size="lg" />
            <span className="text-sm text-[#8b949e]" suppressHydrationWarning>
              {timeAgo(verdict.created_at)}
            </span>
          </div>

          <p className="text-[#e6edf3] text-base font-medium leading-relaxed">
            {verdict.change_summary}
          </p>

          {verdict.affected_field && (
            <div className="mt-4 flex items-center gap-2.5">
              <span className="text-xs text-[#8b949e]">Affected field</span>
              <code className="text-sm font-mono bg-[#0d1117] text-[#79c0ff] px-3 py-1 rounded-md border border-[#30363d]">
                {verdict.affected_field}
              </code>
            </div>
          )}
        </div>

        {/* Analysis / Reasoning */}
        <section>
          <SectionLabel>Analysis</SectionLabel>
          <div className="rounded-xl bg-[#161b22] border border-[#30363d] p-6">
            <p className="text-[#adbac7] text-sm leading-7 whitespace-pre-wrap">
              {verdict.reasoning}
            </p>
          </div>
        </section>

        {/* Blast Radius */}
        <BlastRadius blastRadius={verdict.blast_radius} />
      </main>
    </div>
  )
}

function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex items-center gap-3 mb-3">
      <h2 className="text-xs font-semibold text-[#8b949e] uppercase tracking-widest">
        {children}
      </h2>
      <div className="flex-1 h-px bg-[#21262d]" />
    </div>
  )
}
