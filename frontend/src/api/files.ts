import { AlertItem, FileItem } from "../types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function fetchFiles(): Promise<FileItem[]> {
  const response = await fetch(`${API_BASE_URL}/files`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Не удалось загрузить список файлов");
  }
  return response.json() as Promise<FileItem[]>;
}

export async function fetchAlerts(): Promise<AlertItem[]> {
  const response = await fetch(`${API_BASE_URL}/alerts`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Не удалось загрузить ленту алертов");
  }
  return response.json() as Promise<AlertItem[]>;
}

export async function uploadFile(title: string, file: File): Promise<FileItem> {
  const formData = new FormData();
  formData.append("title", title.trim());
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/files`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error("Не удалось загрузить файл на сервер");
  }

  return response.json() as Promise<FileItem>;
}

export async function deleteFile(fileId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/files/${fileId}`, {
    method: "DELETE",
  });

  if (!response.ok) {
    throw new Error("Не удалось удалить файл");
  }
}

export function getDownloadUrl(fileId: string): string {
  return `${API_BASE_URL}/files/${fileId}/download`;
}
