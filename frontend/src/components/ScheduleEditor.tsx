import { useState } from 'react'
import { Card, CardHeader, CardContent } from './ui/Card'
import Button from './ui/Button'
import { PlusIcon, TrashIcon, ClockIcon } from '@heroicons/react/24/outline'
import type { ScheduleSlot } from '../store/settingsStore'

interface ScheduleEditorProps {
  schedule: Record<string, ScheduleSlot[]>
  onChange: (schedule: Record<string, ScheduleSlot[]>) => void
}

const weekdays = [
  { key: 'monday', label: 'Montag' },
  { key: 'tuesday', label: 'Dienstag' },
  { key: 'wednesday', label: 'Mittwoch' },
  { key: 'thursday', label: 'Donnerstag' },
  { key: 'friday', label: 'Freitag' },
  { key: 'saturday', label: 'Samstag' },
  { key: 'sunday', label: 'Sonntag' },
]

function ScheduleEditor({ schedule, onChange }: ScheduleEditorProps) {
  const [activeDay, setActiveDay] = useState('monday')

  const addTimeSlot = (day: string) => {
    const newSchedule = {
      ...schedule,
      [day]: [
        ...schedule[day],
        { start: '09:00', end: '17:00' }
      ]
    }
    onChange(newSchedule)
  }

  const removeTimeSlot = (day: string, index: number) => {
    const newSchedule = {
      ...schedule,
      [day]: schedule[day].filter((_, i) => i !== index)
    }
    onChange(newSchedule)
  }

  const updateTimeSlot = (
    day: string,
    index: number,
    field: 'start' | 'end' | 'nextDay',
    value: string | boolean
  ) => {
    const newSchedule = {
      ...schedule,
      [day]: schedule[day].map((slot, i) => 
        i === index ? { ...slot, [field]: value } : slot
      )
    }
    onChange(newSchedule)
  }

  const copyToAllDays = () => {
    const activeSlots = schedule[activeDay]
    const newSchedule = { ...schedule }
    
    weekdays.forEach(day => {
      newSchedule[day.key] = [...activeSlots]
    })
    
    onChange(newSchedule)
  }

  const clearDay = (day: string) => {
    const newSchedule = {
      ...schedule,
      [day]: []
    }
    onChange(newSchedule)
  }

  const formatTimeSlot = (slot: ScheduleSlot) => {
    if (slot.nextDay) {
      return `${slot.start} - ${slot.end} (+1)`
    }
    return `${slot.start} - ${slot.end}`
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <ClockIcon className="h-5 w-5 text-gray-400 mr-2" />
            <h3 className="text-lg font-medium text-gray-900">Agent Schedule</h3>
          </div>
          <div className="flex space-x-2">
            <Button variant="outline" size="sm" onClick={copyToAllDays}>
              Copy to All Days
            </Button>
            <Button variant="outline" size="sm" onClick={() => clearDay(activeDay)}>
              Clear Day
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {/* Day Selector */}
        <div className="mb-6">
          <div className="grid grid-cols-7 gap-2">
            {weekdays.map((day) => (
              <button
                key={day.key}
                onClick={() => setActiveDay(day.key)}
                className={`p-2 text-sm rounded-md transition-colors ${
                  activeDay === day.key
                    ? 'bg-primary-500 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                <div className="font-medium">{day.label}</div>
                <div className="text-xs opacity-75">
                  {schedule[day.key].length} slots
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Time Slots for Active Day */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h4 className="font-medium text-gray-900">
              {weekdays.find(d => d.key === activeDay)?.label} Arbeitszeiten
            </h4>
            <Button size="sm" onClick={() => addTimeSlot(activeDay)}>
              <PlusIcon className="h-4 w-4 mr-1" />
              Add Time Slot
            </Button>
          </div>

          {schedule[activeDay].length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <ClockIcon className="mx-auto h-12 w-12 text-gray-300 mb-2" />
              <p>No working hours configured</p>
              <p className="text-sm">Agent will be offline on this day</p>
            </div>
          ) : (
            <div className="space-y-3">
              {schedule[activeDay].map((slot, index) => (
                <div key={index} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-md">
                  <div className="flex items-center space-x-2">
                    <label className="text-sm text-gray-600">From:</label>
                    <input
                      type="time"
                      value={slot.start}
                      onChange={(e) => updateTimeSlot(activeDay, index, 'start', e.target.value)}
                      className="px-2 py-1 border border-gray-300 rounded text-sm"
                    />
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <label className="text-sm text-gray-600">To:</label>
                    <input
                      type="time"
                      value={slot.end}
                      onChange={(e) => updateTimeSlot(activeDay, index, 'end', e.target.value)}
                      className="px-2 py-1 border border-gray-300 rounded text-sm"
                    />
                  </div>

                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id={`nextDay-${index}`}
                      checked={slot.nextDay || false}
                      onChange={(e) => updateTimeSlot(activeDay, index, 'nextDay', e.target.checked)}
                      className="h-4 w-4"
                    />
                    <label htmlFor={`nextDay-${index}`} className="text-sm text-gray-600">
                      Next day
                    </label>
                  </div>

                  <div className="text-sm text-gray-500 min-w-0 flex-1">
                    {formatTimeSlot(slot)}
                  </div>

                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={() => removeTimeSlot(activeDay, index)}
                  >
                    <TrashIcon className="h-4 w-4 text-error-600" />
                  </Button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Quick Presets */}
        <div className="mt-6 pt-4 border-t border-gray-200">
          <p className="text-sm text-gray-600 mb-3">Quick Presets:</p>
          <div className="flex space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                updateTimeSlot(activeDay, 0, 'start', '09:00')
                updateTimeSlot(activeDay, 0, 'end', '17:00')
              }}
            >
              9-5 Workday
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                const newSchedule = {
                  ...schedule,
                  [activeDay]: [{ start: '23:00', end: '06:00', nextDay: true }]
                }
                onChange(newSchedule)
              }}
            >
              Night Shift
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                const newSchedule = {
                  ...schedule,
                  [activeDay]: [{ start: '00:00', end: '23:59' }]
                }
                onChange(newSchedule)
              }}
            >
              24/7
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export default ScheduleEditor