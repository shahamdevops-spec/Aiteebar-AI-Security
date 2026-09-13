import React from 'react'

interface TableColumn<T> {
  key: keyof T
  label: string
  render?: (value: any, row: T) => React.ReactNode
  className?: string
}

interface TableProps<T> {
  columns: TableColumn<T>[]
  data: T[]
  rowKey?: keyof T | ((row: T) => string)
  className?: string
  striped?: boolean
  hover?: boolean
}

export function Table<T extends Record<string, any>>({
  columns,
  data,
  rowKey,
  className = '',
  striped = true,
  hover = true,
}: TableProps<T>) {
  const getRowKey = (row: T, index: number): string => {
    if (!rowKey) return String(index)
    if (typeof rowKey === 'function') return rowKey(row)
    return String(row[rowKey as keyof T])
  }

  return (
    <div className={`overflow-x-auto ${className}`}>
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-700 bg-slate-900/50">
            {columns.map((col) => (
              <th
                key={String(col.key)}
                className="px-4 py-3 text-left font-semibold text-slate-300"
              >
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.length === 0 ? (
            <tr>
              <td colSpan={columns.length} className="px-4 py-8 text-center text-slate-400">
                No data available
              </td>
            </tr>
          ) : (
            data.map((row, index) => (
              <tr
                key={getRowKey(row, index)}
                className={`border-b border-slate-700/50 ${
                  striped && index % 2 === 1 ? 'bg-slate-800/30' : ''
                } ${hover ? 'hover:bg-slate-800/50' : ''} transition-colors`}
              >
                {columns.map((col) => (
                  <td
                    key={String(col.key)}
                    className={`px-4 py-3 text-slate-300 ${col.className || ''}`}
                  >
                    {col.render
                      ? col.render(row[col.key], row)
                      : row[col.key]}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  )
}
