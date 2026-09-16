import { useTheme } from '@/components/theme-provider'
import { Button } from '@/components/ui/button'
import { Sheet, SheetContent, SheetTrigger, SheetTitle } from '@/components/ui/sheet'
import { Sun, Moon, Menu, LayoutDashboard, Users, Search, Settings } from 'lucide-react'
import { useLocation, useNavigate } from 'react-router-dom'
import { cn } from '@/lib/utils'

const mobileMenuItems = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/leads', label: 'Leads', icon: Users },
  { path: '/extraction', label: 'Extra\u00e7\u00e3o', icon: Search },
  { path: '/settings', label: 'Config', icon: Settings },
]

const pageTitles: Record<string, string> = {
  '/': 'Dashboard',
  '/leads': 'Leads',
  '/extraction': 'Extra\u00e7\u00e3o de Leads',
  '/settings': 'Configura\u00e7\u00f5es',
}

export function Header() {
  const { theme, setTheme } = useTheme()
  const location = useLocation()
  const navigate = useNavigate()

  const title = pageTitles[location.pathname] || 'O Tear'

  return (
    <header className="flex h-14 items-center gap-4 border-b bg-background px-4 md:px-6">
      {/* Mobile menu */}
      <Sheet>
        <SheetTrigger asChild>
          <Button variant="ghost" size="icon" className="md:hidden">
            <Menu className="h-5 w-5" />
          </Button>
        </SheetTrigger>
        <SheetContent side="left" className="w-64 p-0">
          <SheetTitle className="sr-only">Menu de Navega\u00e7\u00e3o</SheetTitle>
          <div className="flex items-center h-16 px-4 gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
              <span className="text-sm font-extrabold text-primary-foreground">OT</span>
            </div>
            <div className="flex flex-col">
              <span className="text-sm font-bold text-primary">O Tear</span>
              <span className="text-[10px] text-muted-foreground">Prospec\u00e7\u00e3o</span>
            </div>
          </div>
          <nav className="flex flex-col gap-1 p-2">
            {mobileMenuItems.map((item) => {
              const isActive = item.path === '/' ? location.pathname === '/' : location.pathname.startsWith(item.path)
              const Icon = item.icon
              return (
                <Button
                  key={item.path}
                  variant={isActive ? 'secondary' : 'ghost'}
                  className={cn('w-full justify-start gap-3', isActive && 'bg-accent')}
                  onClick={() => navigate(item.path)}
                >
                  <Icon className="h-4 w-4" />
                  {item.label}
                </Button>
              )
            })}
          </nav>
        </SheetContent>
      </Sheet>

      <h1 className="text-lg font-semibold">{title}</h1>

      <div className="ml-auto flex items-center gap-2">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
        >
          {theme === 'dark' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
        </Button>
      </div>
    </header>
  )
}

