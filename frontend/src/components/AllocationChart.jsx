/**
 * Reusable asset-allocation donut chart. Receives allocation data as props
 * only (e.g. { Equity: 50, Debt: 25, Gold: 15, Real_Estate: 10, Cash: 0 }
 * from a plan returned by POST /api/plans/generate) — it never invents or
 * hard-codes a user's allocation. Hand-rolled SVG so no charting dependency
 * is required.
 */

const ASSET_COLORS = {
  Equity: '#4f46e5',
  Debt: '#0e7490',
  Gold: '#c9971c',
  Real_Estate: '#7c5cbf',
  Cash: '#1a7f4e',
}
const FALLBACK_COLORS = ['#5b6b76', '#a855f7', '#ea580c', '#0891b2', '#be123c']

function colorFor(assetKey, index) {
  return ASSET_COLORS[assetKey] || FALLBACK_COLORS[index % FALLBACK_COLORS.length]
}

function labelFor(assetKey) {
  return assetKey.replace(/_/g, ' ')
}

export default function AllocationChart({ allocation, size = 150, strokeWidth = 26, showLegend = true }) {
  const entries = Object.entries(allocation || {}).filter(([, value]) => Number(value) > 0)
  const total = entries.reduce((sum, [, value]) => sum + Number(value), 0)

  if (!entries.length || total <= 0) {
    return <p className="text-faint">No allocation data available.</p>
  }

  const radius = (size - strokeWidth) / 2
  const circumference = 2 * Math.PI * radius
  let cumulative = 0

  return (
    <div className="allocation-chart">
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} role="img" aria-label="Asset allocation chart">
        <g transform={`rotate(-90 ${size / 2} ${size / 2})`}>
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="var(--color-border)"
            strokeWidth={strokeWidth}
          />
          {entries.map(([assetKey, value], index) => {
            const fraction = Number(value) / total
            const sliceLength = fraction * circumference
            const dashArray = `${sliceLength} ${circumference - sliceLength}`
            const dashOffset = -cumulative
            cumulative += sliceLength
            return (
              <circle
                key={assetKey}
                cx={size / 2}
                cy={size / 2}
                r={radius}
                fill="none"
                stroke={colorFor(assetKey, index)}
                strokeWidth={strokeWidth}
                strokeDasharray={dashArray}
                strokeDashoffset={dashOffset}
              >
                <title>
                  {labelFor(assetKey)}: {value}%
                </title>
              </circle>
            )
          })}
        </g>
      </svg>

      {showLegend && (
        <ul className="allocation-legend">
          {entries.map(([assetKey, value], index) => (
            <li key={assetKey}>
              <span className="allocation-legend__swatch" style={{ background: colorFor(assetKey, index) }} />
              <span>{labelFor(assetKey)}</span>
              <span className="allocation-legend__value">{value}%</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
