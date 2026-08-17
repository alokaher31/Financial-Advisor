export default function EmptyState({ title, description, action }) {
  return (
    <div className="state-block">
      <h3>{title}</h3>
      {description && <p>{description}</p>}
      {action}
    </div>
  )
}
