import { DashboardUserBar } from "@/components/dashboard-user-bar";
import { Sidebar } from "@/components/sidebar";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 overflow-auto flex flex-col">
        <DashboardUserBar />
        <div className="p-6 lg:p-8 max-w-6xl mx-auto flex-1 w-full">{children}</div>
      </main>
    </div>
  );
}
