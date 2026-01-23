import { SidebarProvider } from "@/components/ui/sidebar"
import { AppSidebar } from "@/components/app-sidebar"
import { BottomNav } from "@/features/dashboard/components/mobile/bottom-nav"

export default function TransactionsMobileLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <SidebarProvider defaultOpen={false}>
      <AppSidebar />
      <main className="flex-1">
        {children}
        <BottomNav />
      </main>
    </SidebarProvider>
  )
}
