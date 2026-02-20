"use client"

import { ChevronRight, type LucideIcon } from "lucide-react"
import { Badge } from "@/components/ui/badge"

import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible"
import {
  SidebarGroup,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarMenuSub,
  SidebarMenuSubButton,
  SidebarMenuSubItem,
} from "@/components/ui/sidebar"

export function NavMain({
  items,
  isAdmin = false,
}: {
  items: {
    title: string
    url: string
    icon?: LucideIcon
    isActive?: boolean
    status?: 'P' | 'A' | 'D'
    items?: {
      title: string
      url: string
      status?: 'P' | 'A' | 'D'
    }[]
  }[]
  isAdmin?: boolean
}) {
  const getStatusBadge = (status?: 'P' | 'A' | 'D') => {
    if (!isAdmin || !status) return null
    
    const colors = {
      P: 'bg-green-500/20 text-green-700 border-green-500/30',
      A: 'bg-orange-500/20 text-orange-700 border-orange-500/30',
      D: 'bg-purple-500/20 text-purple-700 border-purple-500/30',
    }
    
    return (
      <Badge 
        variant="outline" 
        className={`ml-auto text-[10px] px-1 py-0 h-4 ${colors[status]}`}
      >
        {status}
      </Badge>
    )
  }

  return (
    <SidebarGroup>
      <SidebarGroupLabel>Platform</SidebarGroupLabel>
      <SidebarMenu>
        {items.map((item) => (
          <Collapsible
            key={item.title}
            asChild
            defaultOpen={item.isActive}
            className="group/collapsible"
          >
            <SidebarMenuItem>
              <CollapsibleTrigger asChild>
                <SidebarMenuButton tooltip={item.title}>
                  {item.icon && <item.icon />}
                  <span>{item.title}</span>
                  {getStatusBadge(item.status)}
                  <ChevronRight className="ml-auto transition-transform duration-200 group-data-[state=open]/collapsible:rotate-90" />
                </SidebarMenuButton>
              </CollapsibleTrigger>
              <CollapsibleContent>
                <SidebarMenuSub>
                  {item.items?.map((subItem) => (
                    <SidebarMenuSubItem key={subItem.title}>
                      <SidebarMenuSubButton asChild>
                        <a href={subItem.url} className="flex items-center justify-between w-full">
                          <span>{subItem.title}</span>
                          {getStatusBadge(subItem.status)}
                        </a>
                      </SidebarMenuSubButton>
                    </SidebarMenuSubItem>
                  ))}
                </SidebarMenuSub>
              </CollapsibleContent>
            </SidebarMenuItem>
          </Collapsible>
        ))}
      </SidebarMenu>
    </SidebarGroup>
  )
}
