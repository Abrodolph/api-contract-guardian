import type { VerdictType } from '@/lib/types'

const STYLES: Record<VerdictType, string> = {
  BREAKING: 'bg-red-600 text-white shadow-red-900/40',
  SAFE:     'bg-emerald-600 text-white shadow-emerald-900/40',
  REVIEW:   'bg-amber-500 text-white shadow-amber-900/40',
}

interface Props {
  verdict: VerdictType
  size?: 'sm' | 'lg'
}

export function VerdictBadge({ verdict, size = 'sm' }: Props) {
  const padding = size === 'lg' ? 'px-4 py-1.5 text-sm' : 'px-3 py-1 text-xs'
  return (
    <span
      className={`inline-flex items-center rounded font-bold tracking-widest uppercase shadow-md ${padding} ${STYLES[verdict]}`}
    >
      {verdict}
    </span>
  )
}
