import {
  LayoutDashboard,
  Users,
  FileText,
  FilePlus,
  ClipboardList,
  TrendingDown,
  BarChart3,
  CreditCard,
  CalendarCheck,
  LogOut,
  Shield,
} from "lucide-react";
import { NavLink } from "@/components/NavLink";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import nyaradzoLogo from "@/assets/nyaradzo-logo.png";
import { toast } from "sonner";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarFooter,
  useSidebar,
} from "@/components/ui/sidebar";

const mainItems = [
  { title: "Dashboard", url: "/dashboard", icon: LayoutDashboard },
  { title: "Policy Holders", url: "/policyholders", icon: Users },
  // { title: "Churn Analytics", url: "/churn", icon: TrendingDown },
  { title: "Churn Prediction", url: "/churn-prediction", icon: BarChart3 },
  { title: "Reports", url: "/reports", icon: BarChart3 },
];

const managementItems = [
  { title: "Register Policy", url: "/register-policy", icon: FilePlus },
  { title: "File a Claim", url: "/claims/new", icon: ClipboardList },
  { title: "Claims Management", url: "/claims", icon: FileText },
  { title: "Matured Policies", url: "/matured", icon: CalendarCheck },
  { title: "Payment Updates", url: "/payments", icon: CreditCard },
];

export function AppSidebar() {
  const { state } = useSidebar();
  const collapsed = state === "collapsed";
  const location = useLocation();
  const navigate = useNavigate();
  const { logout, user } = useAuth();
  
  const isActive = (path: string) => location.pathname === path || location.pathname.startsWith(path + '/');

  const handleLogout = () => {
    console.log('🚪 [SIDEBAR] Logout initiated by user:', user?.email);
    
    try {
      logout();
      console.log('✅ [SIDEBAR] Logout successful, clearing state');
      
      toast.success('Logged out successfully', {
        description: 'You have been securely logged out',
        position: 'bottom-right',
        duration: 3000,
      });
      
      console.log('🧭 [SIDEBAR] Redirecting to login page');
      navigate('/', { replace: true });
    } catch (error) {
      console.error('❌ [SIDEBAR] Logout error:', error);
      toast.error('Logout failed', {
        description: 'An error occurred while logging out',
        position: 'bottom-right',
      });
    }
  };
  return (
    <Sidebar collapsible="icon" className="border-r-0">
      <SidebarContent className="bg-sidebar">
        {/* Logo */}
        <div className="flex items-center gap-3 px-4 py-5 border-b border-sidebar-border">
          <img src={nyaradzoLogo} alt="Nyaradzo" className="h-9 w-9 rounded-lg object-contain" />
          {!collapsed && (
            <div>
              <h2 className="text-sm font-bold text-sidebar-foreground font-sans tracking-wide">NYARADZO</h2>
              <p className="text-[10px] text-sidebar-foreground/60 font-sans">Policy Management System</p>
            </div>
          )}
        </div>

        <SidebarGroup>
          <SidebarGroupLabel className="text-sidebar-foreground/50 text-[10px] uppercase tracking-widest font-sans">Overview</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {mainItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton
                    asChild
                    isActive={isActive(item.url)}
                    className="text-sidebar-foreground/80 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground data-[active=true]:bg-sidebar-accent data-[active=true]:text-sidebar-primary"
                  >
                    <NavLink to={item.url} end={item.url === '/dashboard'} activeClassName="">
                      <item.icon className="h-4 w-4" />
                      {!collapsed && <span className="font-sans text-sm">{item.title}</span>}
                    </NavLink>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        <SidebarGroup>
          <SidebarGroupLabel className="text-sidebar-foreground/50 text-[10px] uppercase tracking-widest font-sans">Management</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {managementItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton
                    asChild
                    isActive={isActive(item.url)}
                    className="text-sidebar-foreground/80 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground data-[active=true]:bg-sidebar-accent data-[active=true]:text-sidebar-primary"
                  >
                    <NavLink to={item.url} end activeClassName="">
                      <item.icon className="h-4 w-4" />
                      {!collapsed && <span className="font-sans text-sm">{item.title}</span>}
                    </NavLink>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter className="bg-sidebar border-t border-sidebar-border">
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton 
              onClick={handleLogout}
              className="text-sidebar-foreground/60 hover:text-sidebar-foreground hover:bg-sidebar-accent hover:text-destructive cursor-pointer transition-colors"
            >
              <LogOut className="h-4 w-4" />
              {!collapsed && <span className="font-sans text-sm">Logout</span>}
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
    </Sidebar>
  );
}
