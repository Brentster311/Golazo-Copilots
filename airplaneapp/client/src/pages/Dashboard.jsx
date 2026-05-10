import { useAuth } from '../context/AuthContext';

export default function Dashboard() {
  const { user, logout } = useAuth();

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Dashboard</h1>
        <button className="btn-logout" onClick={logout}>Log Out</button>
      </div>
      <p>Welcome, <strong>{user.name}</strong>!</p>
      <p>Logged in as: <strong>{user.email}</strong></p>
    </div>
  );
}
