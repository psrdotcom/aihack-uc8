"use client"

import * as React from "react"
import { CalendarIcon } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Calendar } from "@/components/ui/calendar"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
    Popover,
    PopoverContent,
    PopoverTrigger,
} from "@/components/ui/popover"
import { useEffect } from "react"

function formatDate(date: Date | undefined) {
    if (!date) {
        return ""
    }

    return date.toLocaleDateString("en-US", {
        day: "2-digit",
        month: "long",
        year: "numeric",
    })
}

function isValidDate(date: Date | undefined) {
    if (!date) {
        return false
    }
    return !isNaN(date.getTime())
}

type DatePickerProps = {
    value?: Date | undefined
    onChange?: (date: Date | undefined) => void
}

export function DatePicker({ value : initialValue, onChange }: DatePickerProps) {
    const [open, setOpen] = React.useState(false)
    const [date, setDate] = React.useState<Date | undefined>(
        initialValue ?? new Date("2025-06-01")
    )
    const [month, setMonth] = React.useState<Date | undefined>(date)
    const [value, setValue] = React.useState(formatDate(date))

    useEffect(() => {
        if (initialValue && isValidDate(initialValue)) {
            setDate(initialValue)
            setMonth(initialValue)
            setValue(formatDate(initialValue))
        }
    }, [initialValue])
    
    
    const handleDateChange = (date: Date | undefined) => {
        setDate(date)
        setValue(formatDate(date))
        setOpen(false)
        if (onChange) onChange(date)
    }

    return (
        <div className="flex flex-col gap-3">
            <Label htmlFor="date" className="px-1">
                Subscription Date
            </Label>
            <div className="relative flex gap-2">
                <Popover open={open} onOpenChange={setOpen}>
                    <PopoverTrigger asChild>
                        <Button
                            id="date-picker"
                            variant="ghost"
                            className="absolute top-1/2 right-2 size-6 -translate-y-1/2"
                        >
                            <CalendarIcon className="size-3.5" />
                            <span className="sr-only">Select date</span>
                        </Button>
                    </PopoverTrigger>
                    <PopoverContent
                        className="w-auto overflow-hidden p-0"
                        align="end"
                        alignOffset={-8}
                        sideOffset={10}
                    >
                        <Calendar
                            mode="single"
                            selected={date}
                            captionLayout="dropdown"
                            month={month}
                            onMonthChange={setMonth}
                            onSelect={handleDateChange}
                        />
                    </PopoverContent>
                </Popover>
                <Input
                    id="date"
                    value={value}
                    placeholder="June 01, 2025"
                    className="bg-background pr-10"
                    onChange={(e) => {
                        const date = new Date(e.target.value)
                        setValue(e.target.value)
                        if (isValidDate(date)) {
                            setDate(date)
                            setMonth(date)
                            if(onChange) onChange(date)
                        }
                    }}
                    onKeyDown={(e) => {
                        if (e.key === "ArrowDown") {
                            e.preventDefault()
                            setOpen(true)
                        }
                    }}
                />

            </div>
        </div>
    )
}
