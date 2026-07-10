"use client";

import {
  Alert,
  Badge,
  Button,
  Card,
  Col,
  Container,
  Row,
  Spinner,
} from "react-bootstrap";

import { AddFileModal } from "../components/AddFileModal";
import { AlertTable } from "../components/AlertTable";
import { FileTable } from "../components/FileTable";
import { useFilesPage } from "../hooks/useFilesPage";

export default function Page() {
  const {
    files,
    alerts,
    isLoading,
    isSubmitting,
    showModal,
    title,
    errorMessage,
    loadData,
    handleUpload,
    handleDelete,
    setShowModal,
    setTitle,
    setSelectedFile,
  } = useFilesPage();

  return (
    <Container fluid className="py-4 px-4 bg-light min-vh-100">
      <Row className="justify-content-center">
        <Col xxl={10} xl={11}>
          <Card className="shadow-sm border-0 mb-4">
            <Card.Body className="p-4">
              <div className="d-flex justify-content-between align-items-start gap-3 flex-wrap">
                <div>
                  <h1 className="h3 mb-2">Управление файлами</h1>
                  <p className="text-secondary mb-0">
                    Загрузка файлов, просмотр статусов обработки и ленты алертов.
                  </p>
                </div>
                <div className="d-flex gap-2">
                  <Button variant="outline-secondary" onClick={() => void loadData()}>
                    Обновить
                  </Button>
                  <Button variant="primary" onClick={() => setShowModal(true)}>
                    Добавить файл
                  </Button>
                </div>
              </div>
            </Card.Body>
          </Card>

          {errorMessage ? (
            <Alert variant="danger" className="shadow-sm">
              {errorMessage}
            </Alert>
          ) : null}

          <Card className="shadow-sm border-0 mb-4">
            <Card.Header className="bg-white border-0 pt-4 px-4">
              <div className="d-flex justify-content-between align-items-center">
                <h2 className="h5 mb-0">Файлы</h2>
                <Badge bg="secondary">{files.length}</Badge>
              </div>
            </Card.Header>
            <Card.Body className="px-4 pb-4">
              {isLoading ? (
                <div className="d-flex justify-content-center py-5">
                  <Spinner animation="border" />
                </div>
              ) : (
                <FileTable files={files} onDelete={handleDelete} />
              )}
            </Card.Body>
          </Card>

          <Card className="shadow-sm border-0">
            <Card.Header className="bg-white border-0 pt-4 px-4">
              <div className="d-flex justify-content-between align-items-center">
                <h2 className="h5 mb-0">Алерты</h2>
                <Badge bg="secondary">{alerts.length}</Badge>
              </div>
            </Card.Header>
            <Card.Body className="px-4 pb-4">
              {isLoading ? (
                <div className="d-flex justify-content-center py-5">
                  <Spinner animation="border" />
                </div>
              ) : (
                <AlertTable alerts={alerts} />
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <AddFileModal
        show={showModal}
        onHide={() => setShowModal(false)}
        onSubmit={handleUpload}
        title={title}
        onTitleChange={setTitle}
        onFileChange={setSelectedFile}
        isSubmitting={isSubmitting}
      />
    </Container>
  );
}
