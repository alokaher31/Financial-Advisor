/**
 * Simple markdown renderer that handles basic formatting without external dependencies.
 * Handles: bold (**text**), headers (###), and tables (|col|col|).
 */
export default function MarkdownRenderer({ children, className = '' }) {
  if (!children) return null

  const renderMarkdown = (text) => {
    const lines = text.split('\n')
    const elements = []
    let currentTable = null
    let isInTable = false

    lines.forEach((line, idx) => {
      // Check for table rows (lines with pipes)
      if (line.trim().startsWith('|') && line.trim().endsWith('|')) {
        const cells = line
          .trim()
          .slice(1, -1)
          .split('|')
          .map((cell) => cell.trim())

        // Skip separator rows (|---|---|)
        if (cells.every((cell) => /^-+$/.test(cell))) {
          return
        }

        if (!isInTable) {
          // Start new table
          currentTable = { headers: cells, rows: [] }
          isInTable = true
        } else {
          // Add row to current table
          currentTable.rows.push(cells)
        }
      } else {
        // If we were in a table, render it now
        if (isInTable && currentTable) {
          elements.push(
            <table key={`table-${idx}`} className="markdown-table">
              <thead>
                <tr>
                  {currentTable.headers.map((header, i) => (
                    <th key={i} className="markdown-table-header">
                      {header}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {currentTable.rows.map((row, i) => (
                  <tr key={i}>
                    {row.map((cell, j) => (
                      <td key={j} className="markdown-table-cell">
                        {renderInlineMarkdown(cell)}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          )
          isInTable = false
          currentTable = null
        }

        // Handle headers (### text)
        const headerMatch = line.match(/^(#{1,6})\s+(.+)$/)
        if (headerMatch) {
          const level = headerMatch[1].length
          const content = headerMatch[2]
          const Tag = `h${level}`
          elements.push(
            <Tag key={`header-${idx}`} className="markdown-header">
              {renderInlineMarkdown(content)}
            </Tag>
          )
        } else if (line.trim()) {
          // Regular paragraph
          elements.push(
            <p key={`p-${idx}`} className="markdown-paragraph">
              {renderInlineMarkdown(line)}
            </p>
          )
        }
      }
    })

    // Handle any remaining table
    if (isInTable && currentTable) {
      elements.push(
        <table key="table-final" className="markdown-table">
          <thead>
            <tr>
              {currentTable.headers.map((header, i) => (
                <th key={i} className="markdown-table-header">
                  {header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {currentTable.rows.map((row, i) => (
              <tr key={i}>
                {row.map((cell, j) => (
                  <td key={j} className="markdown-table-cell">
                    {renderInlineMarkdown(cell)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      )
    }

    return elements
  }

  const renderInlineMarkdown = (text) => {
    if (!text) return null

    // Handle bold (**text**)
    const parts = []
    let lastIndex = 0
    const boldRegex = /\*\*(.+?)\*\*/g
    let match

    while ((match = boldRegex.exec(text)) !== null) {
      // Add text before bold
      if (match.index > lastIndex) {
        parts.push(text.substring(lastIndex, match.index))
      }
      // Add bold text
      parts.push(<strong key={`bold-${match.index}`}>{match[1]}</strong>)
      lastIndex = match.index + match[0].length
    }

    // Add remaining text
    if (lastIndex < text.length) {
      parts.push(text.substring(lastIndex))
    }

    return parts.length > 0 ? parts : text
  }

  return <div className={`markdown-content ${className}`}>{renderMarkdown(children)}</div>
}