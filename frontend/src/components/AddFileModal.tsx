import { FormEvent } from "react";
import { Button, Form, Modal } from "react-bootstrap";

interface AddFileModalProps {
  show: boolean;
  onHide: () => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  title: string;
  onTitleChange: (value: string) => void;
  onFileChange: (file: File | null) => void;
  isSubmitting: boolean;
}

export function AddFileModal({
  show,
  onHide,
  onSubmit,
  title,
  onTitleChange,
  onFileChange,
  isSubmitting,
}: AddFileModalProps) {
  return (
    <Modal show={show} onHide={onHide} centered>
      <Form onSubmit={onSubmit}>
        <Modal.Header closeButton>
          <Modal.Title>Добавить файл</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form.Group className="mb-3">
            <Form.Group className="mb-3">
              <Form.Label>Название</Form.Label>
              <Form.Control
                value={title}
                onChange={(event) => onTitleChange(event.target.value)}
                placeholder="Например, Договор с подрядчиком"
              />
            </Form.Group>
            <Form.Label>Файл</Form.Label>
            <Form.Control
              type="file"
              onChange={(event) =>
                onFileChange((event.target as HTMLInputElement).files?.[0] ?? null)
              }
            />
          </Form.Group>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="outline-secondary" onClick={onHide}>
            Отмена
          </Button>
          <Button type="submit" variant="primary" disabled={isSubmitting}>
            {isSubmitting ? "Загрузка..." : "Сохранить"}
          </Button>
        </Modal.Footer>
      </Form>
    </Modal>
  );
}
