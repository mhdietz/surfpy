"use client"

import { useState } from "react"
import Link from "next/link"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Button } from "@/components/ui/button"
import { Waves, Trophy, Clock, MapPin, ChevronDown, ChevronUp, Timer } from "lucide-react"

// Helper function to format minutes to hours
function formatMinutesToHours(minutes: string | number | null): string {
  if (!minutes || minutes === "0") return "0.0 hours"
  const hours = parseFloat(minutes.toString()) / 60
  return `${hours.toFixed(1)} hours`
}

// Helper function to capitalize first letter of each word
function capitalizeLocation(location: string): string {
  return location
    .split(" ")
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(" ")
}

interface YearlyStats {
  avg_fun_rating: string;
  avg_session_duration_minutes: string;
  sessions_per_week: string;
  total_sessions: number;
  total_surf_time_minutes: string;
  top_locations?: TopLocation[];
}

interface TopLocation {
  location: string;
  session_count: number;
}

interface UserDashboardStatsProps {
  currentUserYearStats: YearlyStats;
  totalSessionsAllTime: number;
  selectedYear: string;
  availableYears: string[];
  setSelectedYear: (year: string) => void;
}

export function UserDashboardStats({
  currentUserYearStats,
  totalSessionsAllTime,
  selectedYear,
  availableYears,
  setSelectedYear,
}: UserDashboardStatsProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  const toggleExpanded = () => {
    setIsExpanded(!isExpanded)
  }

  const topSpot = currentUserYearStats.top_locations && currentUserYearStats.top_locations.length > 0
    ? currentUserYearStats.top_locations[0]
    : null

  return (
    <div className="space-y-4">
      {/* Always show this welcome section */}
      <div className="flex flex-col items-center justify-center space-y-2 text-center">
        <Trophy className="h-12 w-12 text-muted-foreground" />
        <h2 className="text-3xl font-bold">Welcome to Your Surf Dashboard!</h2>
        {totalSessionsAllTime === 0 && (
          <>
            <p className="text-muted-foreground">
              It looks like you haven't logged any sessions yet.
            </p>
            <Link href="/add" passHref>
              <Button size="lg">Log Your First Session</Button>
            </Link>
          </>
        )}
      </div>

      {/* Render stats only if there are sessions */}
      {totalSessionsAllTime > 0 && (
        <>
          <div className="flex items-center justify-between">
            <h1 className="text-3xl font-bold tracking-tight">Your Stats</h1>
            <Select value={selectedYear} onValueChange={setSelectedYear}>
              <SelectTrigger className="w-32">
                <SelectValue placeholder="Select a year" />
              </SelectTrigger>
              <SelectContent>
                {availableYears.map(year => (
                  <SelectItem key={year} value={year}>{year}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* At a Glance View */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            {/* Sessions Tile */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Sessions</CardTitle>
                <Waves className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="text-2xl font-bold">{currentUserYearStats.total_sessions}</div>
              </CardContent>
            </Card>

            {/* Time Tile */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Surf Time</CardTitle>
                <Clock className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="text-2xl font-bold">
                  {formatMinutesToHours(currentUserYearStats.total_surf_time_minutes)}
                </div>
              </CardContent>
            </Card>

            {/* Fun Tile */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Average Fun</CardTitle>
                <Trophy className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="text-2xl font-bold">
                  {parseFloat(currentUserYearStats.avg_fun_rating).toFixed(1)}/10
                </div>
              </CardContent>
            </Card>

            {/* Top Spot Tile */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Top Spot</CardTitle>
                <MapPin className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent className="space-y-3">
                {topSpot ? (
                  <>
                    <div className="text-2xl font-bold">{capitalizeLocation(topSpot.location)}</div>
                    <p className="text-xs text-muted-foreground">
                      {topSpot.session_count} session{topSpot.session_count !== 1 ? "s" : ""}
                    </p>
                  </>
                ) : (
                  <>
                    <div className="text-2xl font-bold">No sessions</div>
                    <p className="text-xs text-muted-foreground">logged yet</p>
                  </>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Expand/Collapse Button */}
          <div className="flex justify-center mt-4">
            <Button variant="outline" onClick={toggleExpanded} className="w-full md:w-auto">
              {isExpanded ? (
                <>
                  <ChevronUp className="h-4 w-4 mr-2" /> Show Less Advanced Metrics
                </>
              ) : (
                <>
                  <ChevronDown className="h-4 w-4 mr-2" /> Show More Advanced Metrics
                </>
              )}
            </Button>
          </div>

          {/* Advanced Metrics View (Conditionally Rendered) */}
          {isExpanded && (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mt-4">
              {/* All-Time Sessions Tile */}
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">All-Time Sessions</CardTitle>
                  <Waves className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="text-2xl font-bold">{totalSessionsAllTime}</div>
                </CardContent>
              </Card>

              {/* Sessions Per Week Tile */}
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Sessions Per Week</CardTitle>
                  <Timer className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="text-2xl font-bold">
                    {parseFloat(currentUserYearStats.sessions_per_week).toFixed(1)}
                  </div>
                </CardContent>
              </Card>

              {/* Average Session Duration Tile */}
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Average Session Duration</CardTitle>
                  <Clock className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="text-2xl font-bold">
                    {formatMinutesToHours(currentUserYearStats.avg_session_duration_minutes)}
                  </div>
                </CardContent>
              </Card>

              {/* Top 3 Spots Tile */}
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Top 3 Spots</CardTitle>
                  <MapPin className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent className="space-y-3">
                  {currentUserYearStats.top_locations && currentUserYearStats.top_locations.length > 0 ? (
                    currentUserYearStats.top_locations.slice(0, 3).map((location, index) => (
                      <div key={index}>
                        <div className={`${index === 0 ? "text-xl font-bold" : "text-lg font-semibold"}`}>
                          {capitalizeLocation(location.location)}
                        </div>
                        <p className="text-xs text-muted-foreground">
                          {location.session_count} session{location.session_count !== 1 ? "s" : ""}
                        </p>
                      </div>
                    ))
                  ) : (
                    <div>
                      <div className="text-2xl font-bold">No sessions</div>
                      <p className="text-xs text-muted-foreground">logged yet</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          )}
        </>
      )}
    </div>
  )
}