import { FormEvent, useEffect, useState } from "react";

import { deleteFile, fetchAlerts, fetchFiles, uploadFile } from "../api/files";
import { AlertItem, FileItem } from "../types";

export function useFilesPage() {
  const [files, setFiles] = useState<FileItem[]>([]);
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [title, setTitle] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  async function loadData() {
    setIsLoading(true);
    setErrorMessage(null);

    try {
      const [filesData, alertsData] = await Promise.all([
        fetchFiles(),
        fetchAlerts(),
      ]);

      setFiles(filesData);
      setAlerts(alertsData);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Произошла ошибка загрузки");
    } finally {
      setIsLoading(false);
    }
  }

  async function handleUpload(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!title.trim() || !selectedFile) {
      setErrorMessage("Укажите название и выберите файл");
      return;
    }

    setIsSubmitting(true);
    setErrorMessage(null);

    try {
      await uploadFile(title.trim(), selectedFile);
      setShowModal(false);
      setTitle("");
      setSelectedFile(null);
      await loadData();
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Ошибка загрузки файла");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleDelete(fileId: string) {
    if (!confirm("Вы действительно хотите удалить этот файл? Все связанные алерты будут удалены.")) {
      return;
    }

    setIsLoading(true);
    setErrorMessage(null);

    try {
      await deleteFile(fileId);
      await loadData();
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Ошибка удаления файла");
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void loadData();
  }, []);

  return {
    files,
    alerts,
    isLoading,
    isSubmitting,
    showModal,
    title,
    selectedFile,
    errorMessage,
    loadData,
    handleUpload,
    handleDelete,
    setShowModal,
    setTitle,
    setSelectedFile,
    setErrorMessage,
  };
}
