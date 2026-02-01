import { useEffect, useState } from "react";
import {
  cancelSession,
  completeSession,
  createSession,
  deleteSession,
  updateSession
} from "../api";
import type { Game, Resource, Session, SessionCreate, SessionUpdate, SessionStatus } from "../types";

interface SessionModalProps {
  open: boolean;
  onClose: () => void;
  onSaved: () => void;
  session: Session | null;
  games: Game[];
  resources: Resource[];
  role: "owner" | "admin";
  selectedDate: string;
}

const statusOptions: SessionStatus[] = ["planned", "arrived", "completed", "canceled"];

function toLocalInput(iso: string) {
  const date = new Date(iso);
  const pad = (value: number) => String(value).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

function fromLocalInput(value: string) {
  return value;
}

export default function SessionModal({
  open,
  onClose,
  onSaved,
  session,
  games,
  resources,
  role,
  selectedDate
}: SessionModalProps) {
  const [form, setForm] = useState<SessionCreate>({
    resource_id: resources[0]?.id || 0,
    game_id: games[0]?.id || 0,
    start_at: `${selectedDate}T12:00`,
    duration_min: 60,
    players: 2,
    status: "planned",
    contact_name: "",
    contact_phone: "",
    comment: ""
  });
  const [cancelReason, setCancelReason] = useState("");
  const [deleteReason, setDeleteReason] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (session) {
      setForm({
        resource_id: session.resource_id,
        game_id: session.game_id,
        start_at: toLocalInput(session.start_at),
        duration_min: session.duration_min,
        players: session.players || 1,
        status: session.status,
        contact_name: session.contact_name || "",
        contact_phone: session.contact_phone || "",
        comment: session.comment || ""
      });
    } else {
      setForm((prev) => ({
        ...prev,
        resource_id: resources[0]?.id || 0,
        game_id: games[0]?.id || 0,
        start_at: `${selectedDate}T12:00`
      }));
    }
    setCancelReason("");
    setDeleteReason("");
    setError(null);
  }, [session, games, resources, selectedDate]);

  if (!open) return null;

  const handleSave = async () => {
    setSaving(true);
    setError(null);
    try {
      if (!form.resource_id || !form.game_id) {
        throw new Error("Выберите игру и ресурс");
      }
      if (session) {
        const payload: SessionUpdate = {
          resource_id: form.resource_id,
          game_id: form.game_id,
          start_at: fromLocalInput(form.start_at),
          duration_min: form.duration_min,
          players: form.players,
          status: form.status,
          contact_name: form.contact_name,
          contact_phone: form.contact_phone,
          comment: form.comment
        };
        await updateSession(session.id, payload);
      } else {
        const payload: SessionCreate = {
          ...form,
          start_at: fromLocalInput(form.start_at)
        };
        await createSession(payload);
      }
      onSaved();
    } catch (err) {
      setError((err as Error).message || "Ошибка сохранения");
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = async () => {
    if (!session) return;
    if (!cancelReason.trim()) {
      setError("Укажите причину отмены");
      return;
    }
    setSaving(true);
    try {
      await cancelSession(session.id, cancelReason.trim());
      onSaved();
    } catch (err) {
      setError((err as Error).message || "Ошибка отмены");
    } finally {
      setSaving(false);
    }
  };

  const handleComplete = async () => {
    if (!session) return;
    setSaving(true);
    try {
      await completeSession(session.id);
      onSaved();
    } catch (err) {
      setError((err as Error).message || "Ошибка завершения");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!session) return;
    if (!deleteReason.trim()) {
      setError("Укажите причину удаления");
      return;
    }
    setSaving(true);
    try {
      await deleteSession(session.id, deleteReason.trim());
      onSaved();
    } catch (err) {
      setError((err as Error).message || "Ошибка удаления");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="modal-backdrop">
      <div className="modal">
        <div className="modal-header">
          <div>
            <div className="modal-title">{session ? "Редактирование" : "Новая запись"}</div>
            <div className="modal-subtitle">Слот: {selectedDate}</div>
          </div>
          <button className="ghost" onClick={onClose}>Закрыть</button>
        </div>

        <div className="modal-body">
          <div className="form-grid">
            <label>
              Игра
              <select
                value={form.game_id}
                onChange={(event) => setForm({ ...form, game_id: Number(event.target.value) })}
              >
                {games.map((game) => (
                  <option key={game.id} value={game.id}>
                    {game.name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Ресурс
              <select
                value={form.resource_id}
                onChange={(event) => setForm({ ...form, resource_id: Number(event.target.value) })}
              >
                {resources.map((resource) => (
                  <option key={resource.id} value={resource.id}>
                    {resource.name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Начало
              <input
                type="datetime-local"
                value={form.start_at}
                onChange={(event) => setForm({ ...form, start_at: event.target.value })}
              />
            </label>
            <label>
              Длительность (мин)
              <input
                type="number"
                min={5}
                step={5}
                value={form.duration_min}
                onChange={(event) => setForm({ ...form, duration_min: Number(event.target.value) })}
              />
            </label>
            <label>
              Игроков
              <input
                type="number"
                min={1}
                value={form.players ?? 1}
                onChange={(event) => setForm({ ...form, players: Number(event.target.value) })}
              />
            </label>
            <label>
              Статус
              <select
                value={form.status}
                onChange={(event) => setForm({ ...form, status: event.target.value as SessionStatus })}
              >
                {statusOptions.map((status) => (
                  <option key={status} value={status}>
                    {status}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Контакт
              <input
                type="text"
                value={form.contact_name}
                onChange={(event) => setForm({ ...form, contact_name: event.target.value })}
              />
            </label>
            <label>
              Телефон
              <input
                type="text"
                value={form.contact_phone}
                onChange={(event) => setForm({ ...form, contact_phone: event.target.value })}
              />
            </label>
            <label className="full">
              Комментарий
              <textarea
                rows={3}
                value={form.comment}
                onChange={(event) => setForm({ ...form, comment: event.target.value })}
              />
            </label>
          </div>

          {session && (
            <div className="actions-grid">
              <div>
                <label>
                  Причина отмены
                  <input
                    type="text"
                    value={cancelReason}
                    onChange={(event) => setCancelReason(event.target.value)}
                  />
                </label>
                <button className="warning" disabled={saving} onClick={handleCancel}>Отменить</button>
              </div>
              <div>
                <button className="success" disabled={saving} onClick={handleComplete}>Завершить</button>
              </div>
              {role === "owner" && (
                <div>
                  <label>
                    Причина удаления
                    <input
                      type="text"
                      value={deleteReason}
                      onChange={(event) => setDeleteReason(event.target.value)}
                    />
                  </label>
                  <button className="danger" disabled={saving} onClick={handleDelete}>Удалить</button>
                </div>
              )}
            </div>
          )}

          {error && <div className="error-text">{error}</div>}
        </div>

        <div className="modal-footer">
          <button className="ghost" onClick={onClose}>Закрыть</button>
          <button className="primary" disabled={saving} onClick={handleSave}>
            {saving ? "Сохранение..." : "Сохранить"}
          </button>
        </div>
      </div>
    </div>
  );
}
