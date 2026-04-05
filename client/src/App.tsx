import { Routes, Route, Navigate } from "react-router-dom";
import { useState, useEffect } from "react";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import RiskRegister from "./pages/RiskRegister";
import SBOM from "./pages/SBOM";
import ActionItems from "./pages/ActionItems";
import Feed from "./pages/Feed";
import Monitoring from "./pages/Monitoring";
import History from "./pages/History";
import Login from "./pages/Login";
import { getMe } from "./api";
import type { User } from "./types";

export default function App() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getMe()
      .then((res) => {
        if (res.authenticated && res.user) {
          setUser(res.user);
        }
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="h-screen flex items-center justify-center bg-ho-bg">
        <div className="text-ho-muted text-sm">Loading...</div>
      </div>
    );
  }

  if (!user) {
    return <Login />;
  }

  return (
    <Layout user={user}>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/risks" element={<RiskRegister />} />
        <Route path="/sbom" element={<SBOM />} />
        <Route path="/actions" element={<ActionItems />} />
        <Route path="/feed" element={<Feed />} />
        <Route path="/monitoring" element={<Monitoring />} />
        <Route path="/history" element={<History />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  );
}
