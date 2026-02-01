import { useEffect, useState } from "react";
import { setToken } from "./api";
import type { UserInfo } from "./types";
import Login from "./pages/Login";
import CalendarDay from "./pages/CalendarDay";

const USER_KEY = "vr_admin_user";

function loadUser(): UserInfo | null {
  const raw = localStorage.getItem(USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as UserInfo;
  } catch {
    return null;
  }
}

export default function App() {
  const [user, setUser] = useState<UserInfo | null>(() => loadUser());
  const [token, setAuthToken] = useState<string>(() => localStorage.getItem("vr_admin_token") || "");

  useEffect(() => {
    if (token) {
      setToken(token);
    }
  }, [token]);

  const handleLogin = (nextToken: string, nextUser: UserInfo) => {
    setToken(nextToken);
    localStorage.setItem("vr_admin_token", nextToken);
    localStorage.setItem(USER_KEY, JSON.stringify(nextUser));
    setAuthToken(nextToken);
    setUser(nextUser);
  };

  const handleLogout = () => {
    setToken("");
    localStorage.removeItem("vr_admin_token");
    localStorage.removeItem(USER_KEY);
    setAuthToken("");
    setUser(null);
  };

  if (!token || !user) {
    return <Login onSuccess={handleLogin} />;
  }

  return (
    <div className="app-shell">
      <header className="app-header">
        <div>
          <div className="title">VR Admin</div>
          <div className="subtitle">Другие Миры — Юго-Восток</div>
        </div>
        <div className="user-block">
          <div className="user-meta">
            <span>{user.email}</span>
            <span className="role-chip">{user.role}</span>
          </div>
          <button className="ghost" onClick={handleLogout}>Выйти</button>
        </div>
      </header>
      <main className="app-main">
        <CalendarDay user={user} />
      </main>
    </div>
  );
}
