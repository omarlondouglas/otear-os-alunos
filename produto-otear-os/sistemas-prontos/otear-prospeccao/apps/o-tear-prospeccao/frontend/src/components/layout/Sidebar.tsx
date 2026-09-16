import { useLocation, useNavigate } from 'react-router-dom'
import { cn } from '@/lib/utils'
import {
  LayoutDashboard, Users, Search, Settings, ChevronLeft,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip'
import { useState } from 'react'

const menuItems = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/leads', label: 'Leads', icon: Users },
  { path: '/extraction', label: 'Extra\u00e7\u00e3o', icon: Search },
  { path: '/settings', label: 'Config', icon: Settings },
]

export function Sidebar() {
  const location = useLocation()
  const navigate = useNavigate()
  const [collapsed, setCollapsed] = useState(false)

  return (
    <aside
      className={cn(
        'hidden md:flex flex-col border-r bg-sidebar text-sidebar-foreground transition-all duration-300',
        collapsed ? 'w-16' : 'w-64'
      )}
    >
      <div className={cn('flex items-center h-16 px-4', collapsed ? 'justify-center' : 'gap-2')}>
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
          <span className="text-sm font-extrabold text-primary-foreground">OT</span>
        </div>
        {!collapsed && (
          <div className="flex flex-col">
            <span className="text-sm font-bold text-sidebar-primary">O Tear</span>
            <span className="text-[10px] text-muted-foreground">Prospec\u00e7\u00e3o</span>
          </div>
        )}
      </div>

      <Separator className="bg-sidebar-border" />

      <nav className="flex-1 flex flex-col gap-1 p-2">
        {menuItems.map((item) => {
          const isActive = item.path === '/' ? location.pathname === '/' : location.pathname.startsWith(item.path)
          const Icon = item.icon

          const button = (
            <Button
              key={item.path}
              variant={isActive ? 'secondary' : 'ghost'}
              className={cn(
                'w-full justify-start gap-3 font-medium',
                isActive && 'bg-sidebar-accent text-sidebar-accent-foreground',
                collapsed && 'justify-center px-2'
              )}
              onClick={() => navigate(item.path)}
            >
              <Icon className={cn('h-4 w-4 shrink-0', isActive && 'text-sidebar-primary')} />
              {!collapsed && <span>{item.label}</span>}
            </Button>
          )

          if (collapsed) {
            return (
              <Tooltip key={item.path}>
                <TooltipTrigger asChild>{button}</TooltipTrigger>
                <TooltipContent side="right">{item.label}</TooltipContent>
              </Tooltip>
            )
          }

          return button
        })}
      </nav>

      <Separator className="bg-sidebar-border" />

      <div className="p-2">
        <Button
          variant="ghost"
          size="icon"
          className="w-full"
          onClick={() => setCollapsed(!collapsed)}
        >
          <ChevronLeft className={cn('h-4 w-4 transition-transform', collapsed && 'rotate-180')} />
        </Button>
      </div>
    </aside>
  )
}

