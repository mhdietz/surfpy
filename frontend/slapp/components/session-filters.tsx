"use client"

import { useState } from "react"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Slider } from "@/components/ui/slider"
import { Button } from "@/components/ui/button"
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible"
import { Filter, ChevronDown, X } from "lucide-react"

// --- Filter Types ---
export interface SessionFiltersState {
  showOnlyMySessions: boolean
  location: string
  dateRange: string
  swellHeight: string
  swellPeriod: string
  swellDirection: string
  funRating: number
  surfer: string // This will now hold the selected surfer's display_name or "any"
}

interface SessionFiltersProps {
  filters: SessionFiltersState
  setFilters: (filters: SessionFiltersState) => void
  initialState: SessionFiltersState
  availableSurferNames: string[] // New prop for the dropdown options
}

export function SessionFilters({ filters, setFilters, initialState, availableSurferNames }: SessionFiltersProps) {
  const [isMoreFiltersOpen, setIsMoreFiltersOpen] = useState(false)

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFilters({ ...filters, [name]: value })
  }

  const handleSelectChange = (name: string, value: string) => {
    setFilters({ ...filters, [name]: value })
  }

  const handleSliderCommit = (value: number[]) => {
    setFilters({ ...filters, funRating: value[0] })
  }

  const handleClearFilters = () => {
    setFilters(initialState)
  }

  return (
    <div className="p-4 border rounded-lg bg-card text-card-foreground mb-8">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 items-end">
        <div>
          <Label htmlFor="location">Location</Label>
          <Input id="location" name="location" placeholder="e.g., Lido Beach" value={filters.location} onChange={handleInputChange} />
        </div>
        <div>
            <Label>Surfer Name</Label>
            <Select name="surfer" onValueChange={(v) => handleSelectChange("surfer", v)} value={filters.surfer}>
                <SelectTrigger><SelectValue placeholder="Select Surfer" /></SelectTrigger>
                <SelectContent>
                    <SelectItem value="any">Any Surfer</SelectItem>
                    {availableSurferNames.map(name => (
                        <SelectItem key={name} value={name}>{name}</SelectItem>
                    ))}
                </SelectContent>
            </Select>
        </div>
        <div>
          <Label htmlFor="dateRange">Date</Label>
          <Select name="dateRange" onValueChange={(v) => handleSelectChange("dateRange", v)} value={filters.dateRange}>
            <SelectTrigger><SelectValue placeholder="Select date range" /></SelectTrigger>
            <SelectContent>
                <SelectItem value="any">Any Time</SelectItem>
                <SelectItem value="past7">Past 7 Days</SelectItem>
                <SelectItem value="past30">Past 30 Days</SelectItem>
                <SelectItem value="thisMonth">This Month</SelectItem>
                <SelectItem value="thisYear">This Year</SelectItem>
                <SelectItem value="lastYear">Last Year</SelectItem>
                <SelectItem value="2023">2023</SelectItem>
                <SelectItem value="2022">2022</SelectItem>
            </SelectContent>
          </Select>
        </div>
        
        <div>
            <Label>Primary Swell Height</Label>
            <Select name="swellHeight" onValueChange={(v) => handleSelectChange("swellHeight", v)} value={filters.swellHeight}>
                <SelectTrigger><SelectValue placeholder="Swell Height" /></SelectTrigger>
                <SelectContent>
                    <SelectItem value="any">Any Height</SelectItem>
                    <SelectItem value="1-2">1-2 ft</SelectItem>
                    <SelectItem value="2-3">2-3 ft</SelectItem>
                    <SelectItem value="3-5">3-5 ft</SelectItem>
                    <SelectItem value="5+">5+ ft</SelectItem>
                </SelectContent>
            </Select>
        </div>
        <div>
            <Label>Primary Swell Period</Label>
            <Select name="swellPeriod" onValueChange={(v) => handleSelectChange("swellPeriod", v)} value={filters.swellPeriod}>
                <SelectTrigger><SelectValue placeholder="Swell Period" /></SelectTrigger>
                <SelectContent>
                    <SelectItem value="any">Any Period</SelectItem>
                    <SelectItem value="1-5">1-5 s</SelectItem>
                    <SelectItem value="5-8">5-8 s</SelectItem>
                    <SelectItem value="8-12">8-12 s</SelectItem>
                    <SelectItem value="12+">12+ s</SelectItem>
                </SelectContent>
            </Select>
        </div>
        <div>
            <Label>Primary Swell Direction</Label>
            <Select name="swellDirection" onValueChange={(v) => handleSelectChange("swellDirection", v)} value={filters.swellDirection}>
                <SelectTrigger><SelectValue placeholder="Swell Direction" /></SelectTrigger>
                <SelectContent>
                    <SelectItem value="any">Any Direction</SelectItem>
                    <SelectItem value="N">N</SelectItem>
                    <SelectItem value="NE">NE</SelectItem>
                    <SelectItem value="E">E</SelectItem>
                    <SelectItem value="SE">SE</SelectItem>
                    <SelectItem value="S">S</SelectItem>
                    <SelectItem value="SW">SW</SelectItem>
                    <SelectItem value="W">W</SelectItem>
                    <SelectItem value="NW">NW</SelectItem>
                </SelectContent>
            </Select>
        </div>
        <div className="space-y-2 pt-2">
            <Label>Min Fun Rating: {filters.funRating}</Label>
            <Slider defaultValue={[filters.funRating]} max={10} step={1} onValueCommit={handleSliderCommit} />
        </div>
        <div className="flex gap-2 col-span-full justify-end">
            <Button variant="outline" onClick={handleClearFilters} className="w-full md:w-auto">
                <X className="mr-2 h-4 w-4" />
                Clear Filters
            </Button>
        </div>
      </div>
    </div>
  )
}
