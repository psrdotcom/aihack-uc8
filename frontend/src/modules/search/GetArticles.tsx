"use client";
import sampleData from "./table/sample-data.json";

export async function GetArticles({ page = 1, pageSize = 10 }: { page: number; pageSize: number }) {
    // Uncomment below and update the URL when the API is ready
    // const response = await fetch(`/api/NewsArticles?page=${page}&pageSize=${pageSize}`);
    // const result = await response.json();
    // return result;

    // Simulate async delay and use local sample data for now
    await new Promise((resolve) => setTimeout(resolve, 2000));
    const start = (page - 1) * pageSize;
    const end = start + pageSize;
    const data = sampleData.slice(start, end);
    return {
        data,
        total: sampleData.length
    };
}