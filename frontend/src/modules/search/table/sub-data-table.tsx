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
    link?: string;
    creator?: string[] | null;
    description?: string;
    pubDate?: string;
    image_url?: string;
    source_name?: string;
    language?: string;
    country?: string[];
    category?: string[];
    sentiment?: string;
    // ...other properties can be added as needed
}

type SubDataTableProps<TData> = {
    row: Row<TData> | null;
};

export default function SubDataTable<TData>({ row }: SubDataTableProps<TData>) {
    //   const isOpen = row.getIsExpanded();
    if (!row) return <div>No data available</div>;

    // Try to get articles from the row's original data
    // @ts-ignore
    const articles: Article[] = row.original.articles || [];

    if (!articles.length) return <div>No articles found.</div>;

    return (
        <div className="w-full max-w-full overflow-x-auto">
            <Table className="w-full max-w-full">
                <TableCaption className="border-b">
                    Articles for: {typeof row.original === "object" && row.original && "title" in row.original ? (row.original as any).title : "Untitled"}
                </TableCaption>
                <TableHeader className="border-b">
                    <TableRow>
                        <TableHead>Image</TableHead>
                        <TableHead>Source & Description</TableHead>
                        <TableHead>Details</TableHead>
                    </TableRow>
                </TableHeader>
                <TableBody>
                    {articles.map((article, idx) => (
                        <TableRow key={article.article_id || idx}>
                            <TableCell>
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
                            </TableCell>
                            <TableCell className="align-top whitespace-pre-line break-words max-w-xs md:max-w-md lg:max-w-lg xl:max-w-xl text-gray-800 dark:text-gray-100">
                                <div className="font-bold text-base mb-1">Source: {article.source_name}</div>
                                <div>{article.description}</div>
                            </TableCell>
                            <TableCell>
                                <table className="min-w-[200px] text-xs w-full rounded">
                                    <tbody>
                                        <tr className="odd:bg-gray-100/60 dark:odd:bg-white/10">
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
                                        </tr>
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