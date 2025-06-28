"use client"

import {
  type ColumnDef,
  flexRender,
  getCoreRowModel,
  useReactTable,
} from "@tanstack/react-table"

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Collapsible, CollapsibleContent } from "@/components/ui/collapsible"
import { CircleCheckBig } from "lucide-react"
import React from "react"
import { Alert, AlertTitle } from "@/components/ui/alert"
import SubDataTable from "./sub-data-table"

interface DataTableProps<TData, TValue> {
  columns: ColumnDef<TData, TValue>[]
  data: TData[]
  onRowSelectionChange?: (rowSelection: Record<string, unknown>) => void
}

export function DataTable<TData, TValue>({
  columns,
  data,
  onRowSelectionChange,
}: DataTableProps<TData, TValue>) {
  const [rowSelection, setRowSelection] = React.useState({})

  // Wrap setRowSelection to notify parent
  const handleRowSelectionChange = React.useCallback((updater: any) => {
    setRowSelection((prev) => {
      const next = typeof updater === 'function' ? updater(prev) : updater
      if (onRowSelectionChange) {
        onRowSelectionChange(next)
      }
      return next
    })
  }, [onRowSelectionChange])

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    onRowSelectionChange: handleRowSelectionChange,
    state: {
      rowSelection,
    },
  })

  return (
  <>
    <div className="mb-4 flex items-center gap-4">
      <Alert variant="default" className="print-hidden">
        <CircleCheckBig />
        <AlertTitle> {table.getFilteredSelectedRowModel().rows.length} of{" "}
            {table.getFilteredRowModel().rows.length} row(s) selected.</AlertTitle>
      </Alert>
      <button
        className="print-hidden px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
        onClick={() => {
          // Hide all except selected rows for printing
          window.requestAnimationFrame(() => {
            document.body.classList.add('printing-selected');
            window.print();
            setTimeout(() => {
              document.body.classList.remove('printing-selected');
            }, 1000);
          });
        }}
      >
        Print
      </button>
    </div>
    <div className="rounded-md border w-full max-w-screen overflow-x-auto">
      <Table className="min-w-full table-auto whitespace-normal">
        <TableHeader>
          {table.getHeaderGroups().map((headerGroup) => (
            <TableRow key={headerGroup.id}>
              {headerGroup.headers.map((header) => {
                return (
                  <TableHead key={header.id} className="break-words max-w-xs">
                    {header.isPlaceholder
                      ? null
                      : flexRender(
                        header.column.columnDef.header,
                        header.getContext()
                      )}
                  </TableHead>
                )
              })}
            </TableRow>
          ))}
        </TableHeader>
        <TableBody>
          {table.getRowModel().rows?.length ? (
            table.getRowModel().rows.map((row) => {
              const isSelected = row.getIsSelected();
              return (
                <Collapsible key={row.id} asChild>
                  <>
                    <TableRow
                      data-state={isSelected && "selected"}
                      className={
                        typeof window !== 'undefined' ?
                          (isSelected ? 'print:block' : 'print:hidden') : ''
                      }
                    >
                      {row.getVisibleCells().map((cell) => (
                        <TableCell key={cell.id} className="break-words max-w-xs">
                          {flexRender(cell.column.columnDef.cell, cell.getContext())}
                        </TableCell>
                      ))}
                    </TableRow>
                    <CollapsibleContent asChild className={
                      'p-0 bg-sidebar-accent text-sidebar-primary-foreground ' +
                      (typeof window !== 'undefined' ? (isSelected ? 'print:block' : 'print:hidden') : '')
                    }>
                      <tr className="p-0 border-b">
                        <td colSpan={columns.length + 1} className="p-0 border-t-0">
                          <SubDataTable row={row} />
                        </td>
                      </tr>
                    </CollapsibleContent>
                  </>
                </Collapsible>
              )
            })
          ) : (
            <TableRow>
              <TableCell colSpan={columns.length} className="h-24 text-center">
                No results.
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </div>
  </>
  )
}