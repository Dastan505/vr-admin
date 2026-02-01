import { useEffect, useMemo, useState } from "react";
import { getCalendarDay, getGames, getResources } from "../api";
import type { Game, Resource, Session, UserInfo } from "../types";
import SessionModal from "../components/SessionModal";

interface CalendarDayProps {
  user: UserInfo;
}

function formatDateInput(date: Date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function formatTime(iso: string) {
  const date = new Date(iso);
  const hours = String(date.getHours()).padStart(2, "0");
  const minutes = String(date.getMinutes()).padStart(2, "0");
  return `${hours}:${minutes}`;
}

const statusLabels: Record<string, string> = {
  arrived: "arrived",
  planned: "planned",
  completed: "completed",
  canceled: "canceled"
};

export default function CalendarDay({ user }: CalendarDayProps) {
  const [date, setDate] = useState(() => formatDateInput(new Date()));
  const [sessions, setSessions] = useState<Session[]>([]);
  const [games, setGames] = useState<Game[]>([]);
  const [resources, setResources] = useState<Resource[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedSession, setSelectedSession] = useState<Session | null>(null);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [sessionsData, gamesData, resourcesData] = await Promise.all([
        getCalendarDay(date),
        getGames(),
        getResources()
      ]);
      setSessions(sessionsData);
      setGames(gamesData);
      setResources(resourcesData);
    } catch {
      setError("Не удалось загрузить календарь");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [date]);

  const timeline = useMemo(() => {
    const groups: { time: string; items: Session[] }[] = [];
    sessions.forEach((session) => {
      const time = formatTime(session.start_at);
      const last = groups[groups.length - 1];
      if (!last || last.time !== time) {
        groups.push({ time, items: [session] });
      } else {
        last.items.push(session);
      }
    });
    return groups;
  }, [sessions]);

  const openCreate = () => {
    setSelectedSession(null);
    setModalOpen(true);
  };

  const openEdit = (session: Session) => {
    setSelectedSession(session);
    setModalOpen(true);
  };

  return (
    <section className="calendar">
      <div className="calendar-controls">
        <div className="date-picker">
          <label>Дата</label>
          <input type="date" value={date} onChange={(event) => setDate(event.target.value)} />
        </div>
        <div className="controls-right">
          <button className="primary" onClick={openCreate}>Новая запись</button>
        </div>
      </div>

      {error && <div className="error-text">{error}</div>}
      {loading && <div className="muted">Загрузка...</div>}

      {!loading && timeline.length === 0 && (
        <div className="empty">Записей на этот день нет</div>
      )}

      <div className="timeline">
        {timeline.map((group) => (
          <div key={group.time} className="time-group">
            <div className="time-label">{group.time}</div>
            <div className="cards">
              {group.items.map((session) => (
                <button
                  key={session.id}
                  className={`session-card status-${session.status}`}
                  onClick={() => openEdit(session)}
                >
                  <div className="card-icon">{session.game_icon || "??"}</div>
                  <div className="card-main">
                    <div className="card-title">{session.game_name}</div>
                    <div className="card-meta">
                      <span>{session.duration_min} мин</span>
                      <span>{session.players || "—"} игроков</span>
                    </div>
                  </div>
                  <div className="card-status">{statusLabels[session.status]}</div>
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>

      {modalOpen && (
        <SessionModal
          open={modalOpen}
          onClose={() => setModalOpen(false)}
          onSaved={() => {
            setModalOpen(false);
            loadData();
          }}
          session={selectedSession}
          games={games}
          resources={resources}
          role={user.role}
          selectedDate={date}
        />
      )}
    </section>
  );
}
