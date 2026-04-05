import { useState } from "react";
import { NavLink, useLocation } from "react-router-dom";
import {
  LayoutDashboard,
  AlertTriangle,
  Package,
  CheckSquare,
  Rss,
  Activity,
  Clock,
  LogOut,
  Menu,
  X,
} from "lucide-react";
import clsx from "clsx";
import type { User } from "../types";
import { logout } from "../api";

interface Props {
  user: User;
  children: React.ReactNode;
}

const NAV_ITEMS = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/risks", label: "Risk Register", icon: AlertTriangle },
  { to: "/sbom", label: "SBOM", icon: Package },
  { to: "/actions", label: "Action Items", icon: CheckSquare },
  { to: "/feed", label: "Feed", icon: Rss },
  { to: "/monitoring", label: "Monitoring", icon: Activity },
  { to: "/history", label: "History", icon: Clock },
];

export default function Layout({ user, children }: Props) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();

  const handleLogout = async () => {
    await logout();
    window.location.href = "/";
  };

  const closeSidebar = () => setSidebarOpen(false);

  // Find current page label for mobile header
  const currentPage = NAV_ITEMS.find((item) =>
    item.to === "/" ? location.pathname === "/" : location.pathname.startsWith(item.to),
  );

  const sidebarContent = (
    <>
      {/* Logo */}
      <div className="p-4 border-b border-ho-border">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <img src="/icon-128.png" alt="Hopper Ops" className="w-9 h-9 rounded-md" />
            <div>
              <div className="font-bold text-[15px] tracking-tight">Hopper Ops</div>
              <div className="text-[11px] text-ho-muted">GraceZero AI</div>
            </div>
          </div>
          <button
            onClick={closeSidebar}
            className="md:hidden p-1 text-ho-muted hover:text-ho-text transition-colors"
          >
            <X size={18} />
          </button>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 p-2 overflow-y-auto">
        <div className="px-3 py-2 text-[10px] font-semibold uppercase tracking-widest text-ho-muted">
          Overview
        </div>
        {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            onClick={closeSidebar}
            className={({ isActive }) =>
              clsx(
                "flex items-center gap-2.5 px-3 py-2 rounded-md text-[13px] font-medium transition-colors",
                isActive
                  ? "bg-ho-accent/15 text-ho-text border-r-2 border-ho-accent"
                  : "text-ho-muted hover:text-ho-text hover:bg-ho-accent/5",
              )
            }
          >
            <Icon size={16} />
            {label}
          </NavLink>
        ))}
      </nav>

      {/* User */}
      <div className="p-3 border-t border-ho-border">
        <div className="flex items-center gap-2">
          {user.picture && (
            <img src={user.picture} alt="" className="w-7 h-7 rounded-full" />
          )}
          <div className="flex-1 min-w-0">
            <div className="text-xs font-medium truncate">{user.name}</div>
            <div className="text-[10px] text-ho-muted truncate">{user.email}</div>
          </div>
          <button
            onClick={handleLogout}
            className="p-1 text-ho-muted hover:text-ho-text transition-colors"
            title="Logout"
          >
            <LogOut size={14} />
          </button>
        </div>
      </div>
    </>
  );

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Mobile header */}
      <div className="fixed top-0 left-0 right-0 z-30 md:hidden bg-ho-surface border-b border-ho-border">
        <div className="flex items-center justify-between px-4 h-12">
          <button
            onClick={() => setSidebarOpen(true)}
            className="p-1 text-ho-muted hover:text-ho-text transition-colors"
          >
            <Menu size={20} />
          </button>
          <div className="flex items-center gap-2">
            <img src="/icon-128.png" alt="" className="w-6 h-6 rounded" />
            <span className="text-sm font-semibold">{currentPage?.label || "Hopper Ops"}</span>
          </div>
          <div className="w-6" /> {/* Spacer for centering */}
        </div>
      </div>

      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 md:hidden"
          onClick={closeSidebar}
        />
      )}

      {/* Sidebar — desktop: always visible, mobile: slide-in overlay */}
      <aside
        className={clsx(
          "bg-ho-surface border-r border-ho-border flex flex-col z-50",
          // Desktop
          "hidden md:flex md:w-60 md:min-w-[240px]",
          // Mobile overlay
          sidebarOpen && "!flex fixed inset-y-0 left-0 w-64",
        )}
      >
        {sidebarContent}
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto bg-ho-bg pt-12 md:pt-0">
        <div className="max-w-7xl mx-auto p-4 md:p-6">{children}</div>
      </main>
    </div>
  );
}
