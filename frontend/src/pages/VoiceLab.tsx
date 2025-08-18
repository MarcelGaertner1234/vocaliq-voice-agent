import React, { useEffect, useState } from 'react'
import Button from '../components/ui/Button'
import Input from '../components/ui/Input'
import { Card } from '../components/ui/Card'
import apiClient from '../services/api'

interface VoiceInfo {
  voice_id: string
  name: string
  category?: string
  description?: string
  preview_url?: string
}

export default function VoiceLab() {
  const [voices, setVoices] = useState<VoiceInfo[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [text, setText] = useState('Hallo, ich bin Ihr virtueller Assistent von VocalIQ. Wie kann ich helfen?')
  const [voiceId, setVoiceId] = useState('21m00Tcm4TlvDq8ikWAM')
  const [audioUrl, setAudioUrl] = useState<string | null>(null)

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      setError(null)
      try {
        const res = await apiClient.get('/voices/recommended', { params: { language: 'de' } })
        const recs: VoiceInfo[] = res.data
        setVoices(recs)
        if (recs.length) setVoiceId(recs[0].voice_id)
      } catch (e: any) {
        setError(e?.response?.data?.detail || 'Konnte Stimmen nicht laden (API-Key gesetzt?)')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const handleSynthesize = async () => {
    setLoading(true)
    setError(null)
    setAudioUrl(null)
    try {
      const res = await apiClient.post('/voices/tts', {
        text,
        voice_id: voiceId,
        stability: 0.5,
        similarity_boost: 0.75,
        style: 0.0
      })
      const { audio_url } = res.data
      setAudioUrl(audio_url)
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Fehler bei TTS')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-semibold tracking-tight">VoiceLab</h1>
      <Card className="p-6">
        <div className="grid gap-4 md:grid-cols-3">
          <div className="md:col-span-2 space-y-4">
            <label className="block text-sm font-medium text-slate-700">Text</label>
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              rows={4}
              className="w-full rounded-md border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            <div>
              <label className="block text-sm font-medium text-slate-700">Stimme</label>
              <select
                value={voiceId}
                onChange={(e) => setVoiceId(e.target.value)}
                className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2"
              >
                {voices.map((v) => (
                  <option key={v.voice_id} value={v.voice_id}>{v.name}</option>
                ))}
              </select>
            </div>
            <Button onClick={handleSynthesize} disabled={loading}>
              {loading ? 'Erzeuge Audio…' : 'TTS Vorschau erzeugen'}
            </Button>
            {error && <div className="text-sm text-red-600">{error}</div>}
          </div>
          <div className="md:col-span-1">
            <div className="rounded-xl border border-slate-200 p-4">
              <div className="text-sm text-slate-600">Vorschau</div>
              {audioUrl ? (
                <audio className="mt-3 w-full" controls src={audioUrl} />
              ) : (
                <div className="mt-3 text-slate-500 text-sm">Noch keine Vorschau erzeugt.</div>
              )}
              {voices.length > 0 && voices[0].preview_url && (
                <div className="mt-4 text-xs text-slate-500">Original-Preview: <a className="underline" href={voices[0].preview_url} target="_blank">{voices[0].name}</a></div>
              )}
            </div>
          </div>
        </div>
      </Card>
    </div>
  )
} 