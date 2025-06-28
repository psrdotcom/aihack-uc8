"use client"
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { DataTable } from "./table/data-table";
import { columns, type GroupedCategory } from "./table/columns";
import { useEffect, useRef, useState } from "react";
import { GetArticles } from "./GetArticles";
import { Pagination, PaginationContent, PaginationItem, PaginationPrevious, PaginationLink, PaginationNext } from "@/components/ui/pagination";
import { Skeleton } from "@/components/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { useReactToPrint } from "react-to-print";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

function renderSkeletonTable() {
    return (
        <div className="rounded-md border w-full max-w-screen overflow-x-auto">
            <Table className="min-w-full table-auto whitespace-normal">
                <TableHeader>
                    <TableRow>
                        {columns.map((col, idx) => (
                            <TableHead key={col.id || idx} className="break-words max-w-xs">
                                {typeof col.header === 'string' ? col.header : null}
                            </TableHead>
                        ))}
                    </TableRow>
                </TableHeader>
                <TableBody>
                    {[...Array(5)].map((_, rowIdx) => (
                        <TableRow key={rowIdx}>
                            {columns.map((col, colIdx) => (
                                <TableCell key={col.id || colIdx} className="break-words max-w-xs">
                                    <Skeleton className="h-6 w-full rounded" />
                                </TableCell>
                            ))}
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </div>
    );
}

export default function Search() {
    const [data, setData] = useState<GroupedCategory[]>([]);
    const [loading, setLoading] = useState<boolean>(false);
    const [page, setPage] = useState(1);
    const [pageSize, setPageSize] = useState(10);
    const [total, setTotal] = useState(0);
    const [rowSelection, setRowSelection] = useState<Record<string, unknown>>({});

    let componentRef = useRef(null);

    const handlePrint = useReactToPrint({
        contentRef: componentRef,
        documentTitle: `${'test'}-Print`,
        onPrintError: () => alert("there is an error when printing"),
    });

    const fetchData = async (pageNum = page, size = pageSize) => {
        setLoading(true);
        const result = await GetArticles({ page: pageNum, pageSize: size });
        setData(result.data);
        setTotal(result.total);
        setLoading(false);
    };

    useEffect(() => {
        fetchData(page, pageSize);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [page, pageSize]);

    const totalPages = Math.ceil(total / pageSize);

    return (
        <div className="p-8 max-w-full overflow-x-auto gap-8" ref={componentRef}>
            <div className="flex flex-col md:flex-row items-center gap-4 print-hidden">
                <Textarea className="flex-[2] min-h-[56px]" />
                <div className="flex-1 flex justify-center">
                    <Button onClick={() => fetchData(page, pageSize)} className="w-auto px-8">Submit</Button>
                    <button
                        onClick={handlePrint}
                        className="bg-cyan-500 px-6 py-2 text-white border border-cyan-500 font-bold rounded-md mb-3 w-full lg:w-fit my-6 max-w-sm"
                    >
                        Print Payslip
                    </button>
                </div>
            </div>
            <div className="grid col-span-12">
            </div>
            <div className="">
                {loading ?
                    renderSkeletonTable()
                    :
                    <div>
                        <DataTable columns={columns} data={data} onRowSelectionChange={setRowSelection} />
                        {/* You can use rowSelection here as needed, e.g., for debugging: */}

                        <div className="flex items-center justify-between mt-4 print-hidden">
                            <div>
                                <label htmlFor="page-size" className="mr-2">Page Size:</label>
                                <select
                                    id="page-size"
                                    className="border rounded px-2 py-1"
                                    value={pageSize}
                                    onChange={e => { setPageSize(Number(e.target.value)); setPage(1); }}
                                >
                                    {[5, 10, 20, 50].map(size => (
                                        <option key={size} value={size}>{size}</option>
                                    ))}
                                </select>
                            </div>
                            <Pagination>
                                <PaginationContent>
                                    <PaginationItem>
                                        <PaginationPrevious href="#" onClick={e => { e.preventDefault(); if (page > 1) setPage(page - 1); }} />
                                    </PaginationItem>
                                    {[...Array(totalPages)].map((_, idx) => (
                                        <PaginationItem key={idx}>
                                            <PaginationLink
                                                href="#"
                                                isActive={page === idx + 1}
                                                onClick={e => { e.preventDefault(); setPage(idx + 1); }}
                                            >
                                                {idx + 1}
                                            </PaginationLink>
                                        </PaginationItem>
                                    ))}
                                    <PaginationItem>
                                        <PaginationNext href="#" onClick={e => { e.preventDefault(); if (page < totalPages) setPage(page + 1); }} />
                                    </PaginationItem>
                                </PaginationContent>
                            </Pagination>
                        </div>
                    </div>
                }
                {/* <pre className="w-full">{JSON.stringify(rowSelection, null, 2)}</pre>
                <Tabs defaultValue="analysis" className="w-full">
                    <TabsList>
                        <TabsTrigger value="analysis">Analysis</TabsTrigger>
                        <TabsTrigger value="comparision">Comparision</TabsTrigger>
                    </TabsList>
                    <TabsContent value="analysis">
                    </TabsContent>
                    <TabsContent value="comparision">

                    </TabsContent>
                </Tabs> */}
            </div>
        </div>
    )
}