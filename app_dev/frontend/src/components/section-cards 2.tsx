import { TrendingDownIcon, TrendingUpIcon } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import {
  Card,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

export function SectionCards() {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <Card>
        <CardHeader className="relative pb-2">
          <CardDescription>Total Revenue</CardDescription>
          <CardTitle className="text-2xl font-bold tabular-nums">
            $1,250.00
          </CardTitle>
          <div className="absolute right-4 top-4">
            <Badge variant="outline" className="flex gap-1 rounded-lg text-xs">
              <TrendingUpIcon className="size-3" />
              +12.5%
            </Badge>
          </div>
        </CardHeader>
        <CardFooter className="pt-0 pb-3">
          <div className="text-xs text-muted-foreground">
            Trending up this month
          </div>
        </CardFooter>
      </Card>
      <Card>
        <CardHeader className="relative pb-2">
          <CardDescription>New Customers</CardDescription>
          <CardTitle className="text-2xl font-bold tabular-nums">
            1,234
          </CardTitle>
          <div className="absolute right-4 top-4">
            <Badge variant="outline" className="flex gap-1 rounded-lg text-xs">
              <TrendingDownIcon className="size-3" />
              -20%
            </Badge>
          </div>
        </CardHeader>
        <CardFooter className="pt-0 pb-3">
          <div className="text-xs text-muted-foreground">
            Down 20% this period
          </div>
        </CardFooter>
      </Card>
      <Card>
        <CardHeader className="relative pb-2">
          <CardDescription>Active Accounts</CardDescription>
          <CardTitle className="text-2xl font-bold tabular-nums">
            45,678
          </CardTitle>
          <div className="absolute right-4 top-4">
            <Badge variant="outline" className="flex gap-1 rounded-lg text-xs">
              <TrendingUpIcon className="size-3" />
              +12.5%
            </Badge>
          </div>
        </CardHeader>
        <CardFooter className="pt-0 pb-3">
          <div className="text-xs text-muted-foreground">
            Strong user retention
          </div>
        </CardFooter>
      </Card>
      <Card>
        <CardHeader className="relative pb-2">
          <CardDescription>Growth Rate</CardDescription>
          <CardTitle className="text-2xl font-bold tabular-nums">
            4.5%
          </CardTitle>
          <div className="absolute right-4 top-4">
            <Badge variant="outline" className="flex gap-1 rounded-lg text-xs">
              <TrendingUpIcon className="size-3" />
              +4.5%
            </Badge>
          </div>
        </CardHeader>
        <CardFooter className="pt-0 pb-3">
          <div className="text-xs text-muted-foreground">
            Steady performance
          </div>
        </CardFooter>
      </Card>
    </div>
  )
}
