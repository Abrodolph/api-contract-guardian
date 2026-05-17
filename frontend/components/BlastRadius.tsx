import type { BlastRadius as BlastRadiusType } from '@/lib/types'

export function BlastRadius({ blastRadius }: { blastRadius: BlastRadiusType }) {
  if (!blastRadius?.consumers?.length) return null

  return (
    <section>
      <div className="flex items-baseline gap-3 mb-3">
        <h2 className="text-xs font-semibold text-[#8b949e] uppercase tracking-widest">
          Blast Radius
        </h2>
        <span className="text-xs text-[#484f58]">
          {blastRadius.total_call_sites} call site{blastRadius.total_call_sites !== 1 ? 's' : ''} across {blastRadius.consumers.length} consumer{blastRadius.consumers.length !== 1 ? 's' : ''}
        </span>
      </div>

      <div className="flex flex-col gap-3">
        {blastRadius.consumers.map(consumer => (
          <div
            key={consumer.name}
            className="rounded-lg bg-[#161b22] border border-[#30363d] overflow-hidden"
          >
            {/* Consumer header */}
            <div className="flex items-center justify-between px-4 py-3 bg-[#1c2128] border-b border-[#30363d]">
              <div className="flex items-center gap-2.5">
                <span className="w-2 h-2 rounded-full bg-red-500 shrink-0" />
                <span className="text-sm font-semibold text-[#e6edf3]">{consumer.name}</span>
              </div>
              <span className="text-xs font-mono text-[#8b949e] bg-[#0d1117] px-2 py-0.5 rounded border border-[#30363d]">
                {consumer.call_sites.length} site{consumer.call_sites.length !== 1 ? 's' : ''}
              </span>
            </div>

            {/* Call sites */}
            <div className="divide-y divide-[#21262d]">
              {consumer.call_sites.map((site, idx) => (
                <div key={idx} className="flex items-center gap-0 px-0 font-mono group">
                  <span className="w-12 shrink-0 text-right text-xs text-[#484f58] px-3 py-2.5 select-none group-hover:text-[#8b949e] transition-colors">
                    {site.line}
                  </span>
                  <span className="w-px h-full bg-[#21262d] shrink-0 self-stretch" />
                  <span className="text-xs text-[#8b949e] px-3 py-2.5 truncate group-hover:text-[#adbac7] transition-colors">
                    {site.file}
                  </span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}
