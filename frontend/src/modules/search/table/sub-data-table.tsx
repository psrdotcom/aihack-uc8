import { useEffect, useState } from "react";
import type { Row } from "@tanstack/react-table";
import {
    Table,
    TableBody,
    TableCaption,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table"

// Define the type for an article based on sample-data.json
interface Article {
    article_id?: string;
    title?: string;
    body?: string;
    source?: string;
    published_date?: string;
    location_mentions?: string;
    officials_involved?: string;
    relevance_category?: string;
    sentiment?: string;
    linked_id?: string;
    // ...other properties can be added as needed
}

type SubDataTableProps<TData> = {
    row: Row<TData> | null;
    originalData?: TData[] | null; // Optional prop to pass original data
};

export default function SubDataTable<TData>({ row, originalData }: SubDataTableProps<TData>) {
    const [articles, setArticles] = useState<Article[]>([]);
    console.log("SubDataTable rendered with row:", row);
    if (!row) return <div>No data available</div>;

    // @ts-ignore
    const rowSpecificData = row.original as Article;
    console.log("Row specific data:", rowSpecificData);

    useEffect(() => {
        // Robustly parse linked_id and match article_id as strings
        const linkedIds = (rowSpecificData?.linked_id ?? "")
            .replace(/[{}\s'\"]/g, "") // remove braces, spaces, quotes
            .split(",")
            .map((id) => id.trim())
            .filter((id) => id.length > 0);
        console.log("Linked IDs (effect):", linkedIds);
        console.log("Original data (effect):", originalData);
        const foundArticles: Article[] = ((originalData as Article[] | undefined) || []).filter((value) => {
            const aid = value.article_id ? String(value.article_id).trim().toLowerCase() : "";
            console.log("Checking article_id:", aid, "against linkedIds:", linkedIds);
            const match = linkedIds.some((id) => id.trim().toLowerCase() === aid);
            if (!match) {
                console.log("No match (effect): article_id=", aid, ", linkedIds=", linkedIds);
            }
            return match;
        });
        console.log("Articles found (effect):", foundArticles);
        setArticles(foundArticles);
    }, [row, originalData, rowSpecificData?.linked_id]);

    if (!articles.length) return <div>No articles found.</div>;

    return (
        <div className="w-full max-w-full overflow-x-auto">
            <Table className="w-full max-w-full">
                <TableCaption className="border-b">
                    Articles for: {typeof row.original === "object" && row.original && "title" in row.original ? (row.original as any).title : "Untitled"}
                </TableCaption>
                <TableHeader className="border-b">
                    <TableRow>
                        {/* <TableHead>Image</TableHead> */}
                        <TableHead>Source & Description</TableHead>
                        <TableHead>Details</TableHead>
                    </TableRow>
                </TableHeader>
                <TableBody>
                    {articles.map((article, idx) => (
                        <TableRow key={article.article_id || idx}>
                            {/* <TableCell>
                                {article.image_url ? (
                                    <div className="aspect-video min-h-[120px] w-full max-w-[213px] flex items-center justify-center overflow-hidden bg-gray-100 rounded">
                                        <img
                                            src={article.image_url}
                                            alt="article"
                                            className="object-cover w-full h-full"
                                            style={{ aspectRatio: '16/9', minHeight: 120 }}
                                        />
                                    </div>
                                ) : null}
                            </TableCell> */}
                            <TableCell className="align-top whitespace-pre-line break-words max-w-xs md:max-w-md lg:max-w-lg xl:max-w-xl text-gray-800 dark:text-gray-100">
                                <div className="font-bold text-base mb-1">Source: {article.source}</div>
                                <div>{article.body}</div>
                            </TableCell>
                            <TableCell>
                                <table className="min-w-[200px] text-xs w-full rounded">
                                    <tbody>
                                        {Object.keys(article)
                                            .filter(
                                                (key) =>
                                                    !["source", "title", "article_id", "image_url", "body"].includes(key)
                                            )
                                            .map((key) => (
                                                <tr key={key} className="odd:bg-gray-100/60 dark:odd:bg-white/10">
                                                    <td className="font-semibold px-2 py-1 text-gray-800 dark:text-gray-100 whitespace-pre-line break-words max-w-xs md:max-w-md lg:max-w-lg xl:max-w-xl">
                                                        {key.charAt(0).toUpperCase() + key.slice(1)}
                                                    </td>
                                                    <td className="py-1 text-gray-800 dark:text-gray-100 whitespace-pre-line break-words max-w-xs md:max-w-md lg:max-w-lg xl:max-w-xl">
                                                        {Array.isArray((article as any)[key])
                                                            ? (article as any)[key].join(", ")
                                                            : (article as any)[key] ?? "-"}
                                                    </td>
                                                </tr>
                                            ))}
                                        {/* <tr className="odd:bg-gray-100/60 dark:odd:bg-white/10">
                                            <td className="font-semibold px-2 py-1 text-gray-800 dark:text-gray-100">Creator</td>
                                            <td className="py-1 text-gray-800 dark:text-gray-100">{article.creator ? article.creator.join(", ") : "-"}</td>
                                        </tr>
                                        <tr className="odd:bg-gray-100/60 dark:odd:bg-white/10">
                                            <td className="font-semibold px-2 py-1 text-gray-800 dark:text-gray-100">Published</td>
                                            <td className="py-1 text-gray-800 dark:text-gray-100">{article.pubDate}</td>
                                        </tr>
                                        <tr className="odd:bg-gray-100/60 dark:odd:bg-white/10">
                                            <td className="font-semibold px-2 py-1 text-gray-800 dark:text-gray-100">Language</td>
                                            <td className="py-1 text-gray-800 dark:text-gray-100">{article.language}</td>
                                        </tr>
                                        <tr className="odd:bg-gray-100/60 dark:odd:bg-white/10">
                                            <td className="font-semibold px-2 py-1 text-gray-800 dark:text-gray-100">Country</td>
                                            <td className="py-1 text-gray-800 dark:text-gray-100">{article.country ? article.country.join(", ") : "-"}</td>
                                        </tr>
                                        <tr className="odd:bg-gray-100/60 dark:odd:bg-white/10">
                                            <td className="font-semibold px-2 py-1 text-gray-800 dark:text-gray-100">Category</td>
                                            <td className="py-1 text-gray-800 dark:text-gray-100">{article.category ? article.category.join(", ") : "-"}</td>
                                        </tr>
                                        <tr className="odd:bg-gray-100/60 dark:odd:bg-white/10">
                                            <td className="font-semibold px-2 py-1 text-gray-800 dark:text-gray-100">Sentiment</td>
                                            <td className="py-1 text-gray-800 dark:text-gray-100">{article.sentiment}</td>
                                        </tr> */}
                                    </tbody>
                                </table>
                            </TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </div>
    );
}