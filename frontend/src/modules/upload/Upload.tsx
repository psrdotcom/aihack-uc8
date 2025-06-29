import { Button } from "@/components/ui/button";
import React, { useRef, useState, useCallback } from "react";

export function Upload() {
    const [files, setFiles] = useState<File[]>([]);
    const [isDragging, setIsDragging] = useState(false);
    const [uploading, setUploading] = useState(false);
    const [message, setMessage] = useState("");
    const inputRef = useRef<HTMLInputElement>(null);
    const API_BASE_URL = import.meta.env.VITE_API_UPLOAD_URL || "";

    const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        setIsDragging(false);
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            setFiles(Array.from(e.dataTransfer.files));
        }
    };

    const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = () => {
        setIsDragging(false);
    };

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files) {
            setFiles(Array.from(e.target.files));
        }
    };

    const handleClick = () => {
        inputRef.current?.click();
    };

    const handleUpload = async () => {
        if (files.length === 0) {
            setMessage("No files selected.");
            return;
        }
        setUploading(true);
        setMessage("");
        const formData = new FormData();
        files.forEach((file) => {
            formData.append("files", file);
        });
        try {
            // Use API endpoint from env variable
            const response = await fetch(`${API_BASE_URL}/upload`, {
                method: "POST",
                body: formData,
            });
            if (response.ok) {
                setMessage("Files uploaded successfully!");
                setFiles([]);
            } else {
                setMessage("Upload failed.");
            }
        } catch (error) {
            setMessage("An error occurred during upload.");
        } finally {
            setUploading(false);
        }
    };

    // Debounce upload button to prevent multiple rapid clicks
    const uploadTimeout = useRef<NodeJS.Timeout | null>(null);
    const handleUploadDebounced = useCallback(() => {
        if (uploadTimeout.current) return; // Prevent if already waiting
        handleUpload();
        uploadTimeout.current = setTimeout(() => {
            uploadTimeout.current = null;
        }, 1500); // 1.5s debounce
    }, [handleUpload]);

    return (
        <div className="w-full p-8">
            <h1 className="text-xl font-bold mb-4">Upload Files</h1>
            <div
                className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${isDragging ? "border-blue-500 bg-blue-50" : "border-gray-300"}`}
                onDrop={handleDrop}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onClick={handleClick}
            >
                <input
                    type="file"
                    multiple
                    ref={inputRef}
                    className="hidden"
                    onChange={handleFileChange}
                />
                <p className="mb-2">Drag and drop files here, or <span className="text-blue-600 underline">browse</span></p>
                {files.length > 0 && (
                    <ul className="mb-2">
                        {files.map((file, idx) => (
                            <li key={idx} className="text-sm text-gray-700">{file.name}</li>
                        ))}
                    </ul>
                )}
            </div>
            <div className="flex gap-2 mt-4 justify-center">
                <Button variant="default" onClick={handleUploadDebounced}
                    disabled={uploading || files.length === 0}> {uploading ? "Uploading..." : "Upload"}</Button>
                <Button
                    variant="destructive"
                    onClick={() => {setFiles([]); setMessage("");}}
                    disabled={files.length === 0 || uploading}
                >
                    Clear Selection
                </Button>
            </div>
            {message && <p className="mt-4 text-center text-sm">{message}</p>}
        </div>
    );
}