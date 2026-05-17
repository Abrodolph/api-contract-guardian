'use client'

import { useEffect, useState } from 'react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import type { TooltipProps } from 'recharts'
import type { NameType, ValueType } from 'recharts/types/component/DefaultTooltipContent'

interface HealthPoint {
  date: string
  BREAKING: number
  SAFE: number
  REVIEW: number
}

const COLORS = {
  BREAKING: '#dc2626',
  REVIEW:   '#f59e0b',
  SAFE:     '#16a34a',
} as const

function formatDate(dateStr: string): string {
  const [, m, d] = dateStr.split('-').map(Number)
  const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
  return `${months[m - 1]} ${d}`
}

function ChartTooltip({ active, payload, label }: TooltipProps<ValueType, NameType>) {
  if (!active || !payload?.length) return null

  const order: Array<keyof typeof COLORS> = ['BREAKING', 'REVIEW', 'SAFE']
  const byName = Object.fromEntries(payload.map(p => [p.name, p]))

  return (
    <div className="bg-[#1c2128] border border-[#30363d] rounded-lg px-4 py-3 shadow-2xl min-w-[140px]">
      <p className="text-[10px] font-semibold text-[#8b949e] uppercase tracking-widest mb-2.5">
        {label ? formatDate(String(label)) : ''}
      </p>
      {order.map(name => {
        const entry = byName[name]
        if (!entry) return null
        return (
          <div key={name} className="flex items-center gap-2 text-xs mb-1 last:mb-0">
            <span
              className="w-2.5 h-2.5 rounded-sm shrink-0"
              style={{ backgroundColor: COLORS[name] }}
            />
            <span className="text-[#8b949e] flex-1">{name}</span>
            <span className="text-[#e6edf3] font-mono font-semibold tabular-nums">
              {Number(entry.value)}
            </span>
          </div>
        )
      })}
    </div>
  )
}

export function ContractHealthChart() {
  const [data, setData] = useState<HealthPoint[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)

  useEffect(() => {
    fetch('https://api-contract-guardian-1.onrender.com/contract-health')
      .then(r => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`)
        return r.json() as Promise<HealthPoint[]>
      })
      .then(setData)
      .catch(() => setError(true))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="h-[220px] rounded-xl bg-[#161b22] border border-[#30363d] mb-6 animate-pulse" />
    )
  }

  if (error || data.length === 0) return null

  return (
    <div className="rounded-xl bg-[#161b22] border border-[#30363d] px-5 pt-5 pb-3 mb-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xs font-semibold text-[#8b949e] uppercase tracking-widest">
          Contract Health
        </h2>
        <span className="text-xs text-[#484f58]">{data.length} days</span>
      </div>

      <ResponsiveContainer width="100%" height={160}>
        <BarChart data={data} barSize={14} barCategoryGap="30%">
          <CartesianGrid vertical={false} stroke="#21262d" strokeDasharray="0" />
          <XAxis
            dataKey="date"
            tickFormatter={formatDate}
            tick={{ fill: '#484f58', fontSize: 11, fontFamily: 'inherit' }}
            axisLine={false}
            tickLine={false}
            dy={6}
          />
          <YAxis
            allowDecimals={false}
            tick={{ fill: '#484f58', fontSize: 11, fontFamily: 'inherit' }}
            axisLine={false}
            tickLine={false}
            dx={-4}
            width={24}
          />
          <Tooltip
            content={<ChartTooltip />}
            cursor={{ fill: '#21262d', rx: 4 }}
          />
          {/* Stack order: BREAKING at bottom, REVIEW middle, SAFE on top */}
          <Bar dataKey="BREAKING" stackId="a" fill={COLORS.BREAKING} radius={[0, 0, 2, 2]} />
          <Bar dataKey="REVIEW"   stackId="a" fill={COLORS.REVIEW}   radius={[0, 0, 0, 0]} />
          <Bar dataKey="SAFE"     stackId="a" fill={COLORS.SAFE}     radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>

      {/* Legend */}
      <div className="flex items-center gap-5 mt-3 justify-end">
        {(Object.entries(COLORS) as [keyof typeof COLORS, string][]).map(([name, color]) => (
          <div key={name} className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-sm" style={{ backgroundColor: color }} />
            <span className="text-[10px] text-[#8b949e] uppercase tracking-wide">{name}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
