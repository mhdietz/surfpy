"use client"

import Link from "next/link"
import { usePathname, useRouter } from "next/navigation"
import { cn } from "@/lib/utils"
import { Home, List, Plus, BarChart3, Waves } from "lucide-react"

export function BottomNav() {
  const pathname = usePathname()
  const router = useRouter()

  // Don't show bottom nav on login and signup pages
  if (pathname === "/login" || pathname === "/signup") {
    return null
  }

  const navItems = [
    { href: "/", label: "Dashboard", icon: Home },
    { href: "/add", label: "Add", icon: Plus },
    { href: "/sessions-v2", label: "Sessions", icon: List },
    { href: "/forecast-v3", label: "Forecast", icon: Waves },
  ]

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-background border-t md:hidden">
      <div className="flex items-center justify-around py-2">
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = pathname === item.href
          const isForecastTab = item.href === "/forecast-v3";

          const handleClick = (e: React.MouseEvent) => {
            if (isActive && isForecastTab) {
              e.preventDefault(); // Prevent default link navigation
              router.refresh(); // Force a refresh to reset the page state
            }
          };

          return (
            <Link
              key={item.href}
              href={item.href}
              onClick={handleClick}
              className={cn(
                "flex flex-col items-center gap-1 px-3 py-2 text-xs transition-colors",
                isActive ? "text-primary" : "text-muted-foreground hover:text-primary",
                item.href === "/add" && "bg-primary text-primary-foreground p-3 shadow-lg"
              )}
            >
              <Icon className={cn("h-5 w-5", isActive && "fill-current")} />
              <span>{item.label}</span>
            </Link>
          )
        })}
      </div>
    </nav>
  )
}
