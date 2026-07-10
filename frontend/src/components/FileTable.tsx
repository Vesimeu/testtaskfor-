import { Badge, Button, Table } from "react-bootstrap";

import { getDownloadUrl } from "../api/files";
import { FileItem } from "../types";
import { formatDate, formatSize, getProcessingVariant } from "../utils/format";

interface FileTableProps {
  files: FileItem[];
  onDelete: (fileId: string) => void;
}

export function FileTable({ files, onDelete }: FileTableProps) {
  return (
    <div className="table-responsive">
      <Table hover bordered className="align-middle mb-0">
        <thead className="table-light">
          <tr>
            <th>Название</th>
            <th>Файл</th>
            <th>MIME</th>
            <th>Размер</th>
            <th>Статус</th>
            <th>Проверка</th>
            <th>Создан</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          {files.length === 0 ? (
            <tr>
              <td colSpan={8} className="text-center py-4 text-secondary">
                Файлы пока не загружены
              </td>
            </tr>
          ) : (
            files.map((file) => (
              <tr key={file.id}>
                <td>
                  <div className="fw-semibold">{file.title}</div>
                  <div className="small text-secondary">{file.id}</div>
                </td>
                <td>{file.original_name}</td>
                <td>{file.mime_type}</td>
                <td>{formatSize(file.size)}</td>
                <td>
                  <Badge bg={getProcessingVariant(file.processing_status)}>
                    {file.processing_status}
                  </Badge>
                </td>
                <td>
                  <div className="d-flex flex-column gap-1">
                    <Badge bg={file.requires_attention ? "warning" : "success"}>
                      {file.scan_status ?? "pending"}
                    </Badge>
                    <span className="small text-secondary">
                      {file.scan_details ?? "Ожидает обработки"}
                    </span>
                  </div>
                </td>
                <td>{formatDate(file.created_at)}</td>
                <td className="text-nowrap">
                  <div className="d-flex gap-2">
                    <Button
                      as="a"
                      href={getDownloadUrl(file.id)}
                      variant="outline-primary"
                      size="sm"
                    >
                      Скачать
                    </Button>
                    <Button
                      variant="outline-danger"
                      size="sm"
                      onClick={() => onDelete(file.id)}
                    >
                      Удалить
                    </Button>
                  </div>
                </td>
              </tr>
            ))
          )}
        </tbody>
      </Table>
    </div>
  );
}
