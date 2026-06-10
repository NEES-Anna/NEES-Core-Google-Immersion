export default function RiskBadge({ risk }) {
  return <span className={`risk-badge risk-${risk || "unknown"}`}>{risk || "pending"}</span>;
}
