import { fetchVerdicts } from '@/lib/api'
import { VerdictList } from '@/components/VerdictList'
import { ShieldIcon } from '@/components/ShieldIcon'
import { ContractHealthChart } from '@/components/ContractHealthChart'
import type { Verdict } from '@/lib/types'

export const dynamic = 'force-dynamic'

export default async function Home() {
  let initialVerdicts: Verdict[] = []
  try {
    initialVerdicts = await fetchVerdicts()
    if (!Array.isArray(initialVerdicts)) initialVerdicts = []
  } catch {
    initialVerdicts = []
  }

  return (
    <div className="min-h-screen bg-[#0d1117]">
      {/* Sticky header */}
      <header className="sticky top-0 z-20 border-b border-[#21262d] bg-[#0d1117]/90 backdrop-blur-sm">
        <div className="max-w-3xl mx-auto px-6 py-4 flex items-center gap-3">
          <ShieldIcon />
          <div>
            <h1 className="text-base font-bold text-[#e6edf3] tracking-tight leading-none">
              API Contract Guardian
            </h1>
            <p className="text-xs text-[#8b949e] mt-1 leading-none">
              Catch breaking changes before they ship.
            </p>
          </div>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-6 py-8">
        <ContractHealthChart />
        <VerdictList initial={initialVerdicts} />
      </main>
    </div>
  )
}
