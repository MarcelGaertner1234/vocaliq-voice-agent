import { useEffect, useRef, useState } from 'react'
import { Card, CardHeader, CardContent } from '../components/ui/Card'
import Button from '../components/ui/Button'
import Input from '../components/ui/Input'
import { systemApi, knowledgeApi, wsUrlFor, type SystemStatus } from '../services/api'

interface SearchResult {
  content: string
  document: string
  relevance_score: number
  metadata?: Record<string, unknown>
}

interface KnowledgeDocRow {
  id: string
  filename: string
  file_type: string
  file_size?: number
  uploaded_at?: string
  processing_status?: string
  chunk_count?: number
}

function Debug() {
  const [status, setStatus] = useState<SystemStatus[] | { error: string } | null>(null)
  const [docs, setDocs] = useState<KnowledgeDocRow[]>([])
  const [query, setQuery] = useState('Hallo')
  const [results, setResults] = useState<SearchResult[] | null>(null)

  // WebSocket
  const [wsStatus, setWsStatus] = useState<'disconnected'|'connecting'|'connected'|'error'>('disconnected')
  const [wsLog, setWsLog] = useState<string[]>([])
  const wsRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    refreshStatus()
    refreshDocs()
  }, [])

  const refreshStatus = async () => {
    try {
      const s = await systemApi.getStatus()
      setStatus(s)
    } catch (err) {
      console.warn('status failed', err)
      setStatus({ error: 'failed' })
    }
  }

  const refreshDocs = async () => {
    try {
      const d = await knowledgeApi.getDocuments() as KnowledgeDocRow[]
      setDocs(d)
    } catch (err) {
      console.warn('docs failed', err)
      setDocs([])
    }
  }

  const doSearch = async () => {
    try {
      const r = await knowledgeApi.search(query, 5) as { results?: SearchResult[] }
      setResults(r.results || [])
    } catch (err) {
      console.warn('search failed', err)
      setResults([])
    }
  }

  const connectWs = () => {
    if (wsRef.current) wsRef.current.close()
    setWsLog([])
    setWsStatus('connecting')
    const url = wsUrlFor('/api/twilio/websocket')
    const ws = new WebSocket(url)
    wsRef.current = ws
    ws.onopen = () => {
      setWsStatus('connected')
      setWsLog(prev => [...prev, `opened: ${url}`])
      const startFrame = {
        event: 'start',
        start: {
          streamSid: 'DBGSTREAM',
          callSid: 'DBG-CALL',
          customParameters: { from_number: '+49123456789' }
        }
      }
      ws.send(JSON.stringify(startFrame))
      setWsLog(prev => [...prev, 'sent start frame'])
    }
    ws.onmessage = (evt) => {
      setWsLog(prev => [...prev, `msg: ${evt.data?.toString().slice(0, 200)}`])
    }
    ws.onerror = () => {
      setWsStatus('error')
      setWsLog(prev => [...prev, 'error'])
    }
    ws.onclose = () => {
      setWsStatus('disconnected')
      setWsLog(prev => [...prev, 'closed'])
    }
  }

  const stopWs = () => {
    if (!wsRef.current) return
    try {
      wsRef.current.send(JSON.stringify({ event: 'stop' }))
    } catch (err) {
      console.warn('stop failed', err)
    }
    wsRef.current.close()
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Debug</h1>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-medium text-gray-900">System Status</h3>
            <Button variant="outline" size="sm" onClick={refreshStatus}>Refresh</Button>
          </div>
        </CardHeader>
        <CardContent>
          <pre className="text-xs bg-gray-50 p-3 rounded border overflow-auto max-h-60">{JSON.stringify(status, null, 2)}</pre>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-medium text-gray-900">Knowledge</h3>
            <div className="flex items-center space-x-2">
              <Input className="w-64" value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search query" />
              <Button variant="outline" size="sm" onClick={doSearch}>Search</Button>
              <Button variant="outline" size="sm" onClick={refreshDocs}>List</Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div>
              <div className="text-sm font-medium mb-1">Documents</div>
              <pre className="text-xs bg-gray-50 p-3 rounded border overflow-auto max-h-60">{JSON.stringify(docs, null, 2)}</pre>
            </div>
            <div>
              <div className="text-sm font-medium mb-1">Search Results</div>
              <pre className="text-xs bg-gray-50 p-3 rounded border overflow-auto max-h-60">{JSON.stringify(results, null, 2)}</pre>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-medium text-gray-900">Twilio WebSocket</h3>
            <div className="flex items-center space-x-2">
              <Button size="sm" onClick={connectWs} disabled={wsStatus==='connecting'}>Connect</Button>
              <Button size="sm" variant="outline" onClick={stopWs} disabled={wsStatus!=='connected'}>Stop</Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="text-sm mb-2">Status: {wsStatus}</div>
          <pre className="text-xs bg-gray-50 p-3 rounded border overflow-auto max-h-60">{wsLog.join('\n')}</pre>
        </CardContent>
      </Card>
    </div>
  )
}

export default Debug 