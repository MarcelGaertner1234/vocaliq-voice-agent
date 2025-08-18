import React, { useState, useRef, useEffect, useCallback } from 'react'
import apiClient from '../services/api'

interface VoiceChatProps {
  voiceId?: string
  language?: 'de' | 'en'
}

const VoiceChat: React.FC<VoiceChatProps> = ({ 
  voiceId = '21m00Tcm4TlvDq8ikWAM', 
  language = 'de' 
}) => {
  const [isCallActive, setIsCallActive] = useState(false)
  const [isConnecting, setIsConnecting] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [isListening, setIsListening] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [audioLevel, setAudioLevel] = useState(0)
  const [lastTtsUrl, setLastTtsUrl] = useState<string | null>(null)
  const ttsQueueRef = useRef<string[]>([])
  const isPlayingRef = useRef<boolean>(false)
  
  const playNextFromQueue = useCallback(async () => {
    if (isPlayingRef.current) {
      console.log('Already playing, skipping queue processing')
      return
    }
    const nextUrl = ttsQueueRef.current.shift()
    if (!nextUrl) { 
      console.log('Queue is empty')
      isPlayingRef.current = false
      return 
    }
    console.log('Playing next from queue:', nextUrl)
    isPlayingRef.current = true
    try {
      if (!audioElRef.current) {
        audioElRef.current = new Audio()
        ;(audioElRef.current as any).playsInline = true
        audioElRef.current.setAttribute('playsinline', 'true')
        audioElRef.current.preload = 'auto'
        audioElRef.current.autoplay = true
        audioElRef.current.muted = false
        audioElRef.current.volume = 1.0
      }
      const audio = audioElRef.current
      try { await unlockAudio() } catch {}
      try { await audioContextRef.current?.resume() } catch {}
      try { audio.pause() } catch {}
      try { audio.currentTime = 0 } catch {}
      audio.src = nextUrl
      audio.onended = () => {
        isPlayingRef.current = false
        playNextFromQueue().catch(() => {})
      }
      await audio.play()
    } catch (e1) {
      try {
        if (!audioContextRef.current) {
          audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)()
        }
        const ctx = audioContextRef.current
        try { await unlockAudio() } catch {}
        try { await ctx.resume() } catch {}
        const resp = await fetch(nextUrl, { cache: 'no-store' })
        const buf = await resp.arrayBuffer()
        const decoded = await ctx.decodeAudioData(buf.slice(0))
        const source = ctx.createBufferSource()
        source.buffer = decoded
        source.connect(ctx.destination)
        source.onended = () => {
          isPlayingRef.current = false
          playNextFromQueue().catch(() => {})
        }
        source.start(0)
      } catch (e2) {
        console.error('TTS queue playback failed', e1, e2)
        isPlayingRef.current = false
        playNextFromQueue().catch(() => {})
      }
    }
  }, [])

  const enqueueTtsUrl = useCallback((absoluteUrl: string) => {
    ttsQueueRef.current.push(absoluteUrl)
    if (!isPlayingRef.current) {
      playNextFromQueue().catch(() => {})
    }
  }, [playNextFromQueue])

  const canvasRef = useRef<HTMLCanvasElement>(null)
  const audioContextRef = useRef<AudioContext | null>(null)
  const analyserRef = useRef<AnalyserNode | null>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const websocketRef = useRef<WebSocket | null>(null)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const recordedChunksRef = useRef<BlobPart[]>([])
  const sliceIntervalRef = useRef<number | null>(null)
  const suspendCaptureRef = useRef<boolean>(false)
  const vadIntervalRef = useRef<number | null>(null)
  const segmentTimerRef = useRef<number | null>(null)
  const segmentStartTsRef = useRef<number>(0)
  const animationFrameRef = useRef<number>(0)
  const keepAliveRef = useRef<number | null>(null)
  const audioElRef = useRef<HTMLAudioElement | null>(null)
  // Audio-Entsperrung (Safari/Autoplay)
  const unlockAudio = async () => {
    try {
      if (!audioContextRef.current) {
        audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)()
      }
      const ctx = audioContextRef.current
      await ctx.resume()
      const osc = ctx.createOscillator()
      const gain = ctx.createGain()
      gain.gain.value = 0.00001
      osc.connect(gain).connect(ctx.destination)
      osc.start(0)
      osc.stop(ctx.currentTime + 0.05)
    } catch {}
  }

  // Mikrofon-Zugriff
  const startMicrophone = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
          sampleRate: 48000,
          channelCount: 1 as any
        } 
      })
      streamRef.current = stream

      // Audio Context für Visualisierung
      audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)()
      analyserRef.current = audioContextRef.current.createAnalyser()
      analyserRef.current.fftSize = 256
      
      const source = audioContextRef.current.createMediaStreamSource(stream)
      source.connect(analyserRef.current)
      
      return stream
    } catch (err) {
      console.error('Mikrofon-Zugriff fehlgeschlagen:', err)
      throw new Error('Mikrofon-Zugriff verweigert')
    }
  }

  // Audio-Visualisierung
  const visualize = useCallback(() => {
    if (!canvasRef.current || !analyserRef.current) return
    
    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const bufferLength = analyserRef.current.fftSize
    const timeData = new Uint8Array(bufferLength)
    
    const draw = () => {
      animationFrameRef.current = requestAnimationFrame(draw)
      
      analyserRef.current!.getByteTimeDomainData(timeData)
      
      // Canvas leeren
      ctx.fillStyle = 'rgba(0, 0, 0, 0.05)'
      ctx.fillRect(0, 0, canvas.width, canvas.height)
      
      // RMS als Lautstärke schätzen
      let sumSquares = 0
      for (let i = 0; i < bufferLength; i++) {
        const v = (timeData[i] - 128) / 128
        sumSquares += v * v
      }
      const rms = Math.sqrt(sumSquares / bufferLength)
      setAudioLevel(Math.min(100, Math.max(0, rms * 100)))
      
      // Modern circular visualizer with gradient
      const centerX = canvas.width / 2
      const centerY = canvas.height / 2
      const radius = 100
      
      // Create gradient for the visualization
      const gradient = ctx.createRadialGradient(centerX, centerY, 0, centerX, centerY, radius * 1.5)
      if (isCallActive) {
        gradient.addColorStop(0, 'rgba(139, 92, 246, 0.8)')
        gradient.addColorStop(0.5, 'rgba(59, 130, 246, 0.6)')
        gradient.addColorStop(1, 'rgba(139, 92, 246, 0.2)')
      } else {
        gradient.addColorStop(0, 'rgba(156, 163, 175, 0.6)')
        gradient.addColorStop(1, 'rgba(156, 163, 175, 0.2)')
      }
      
      ctx.beginPath()
      ctx.strokeStyle = gradient
      ctx.lineWidth = isCallActive ? 4 : 3
      
      for (let i = 0; i < bufferLength; i++) {
        const angle = (i / bufferLength) * Math.PI * 2
        const amp = Math.abs((timeData[i] - 128) / 128)
        const x = centerX + Math.cos(angle) * (radius + amp * 50)
        const y = centerY + Math.sin(angle) * (radius + amp * 50)
        
        if (i === 0) {
          ctx.moveTo(x, y)
        } else {
          ctx.lineTo(x, y)
        }
      }
      
      ctx.closePath()
      ctx.stroke()
      
      // Central circle with gradient
      const innerGradient = ctx.createRadialGradient(centerX, centerY, 0, centerX, centerY, radius * 0.8)
      if (isCallActive) {
        innerGradient.addColorStop(0, 'rgba(139, 92, 246, 0.15)')
        innerGradient.addColorStop(1, 'rgba(59, 130, 246, 0.05)')
      } else {
        innerGradient.addColorStop(0, 'rgba(156, 163, 175, 0.1)')
        innerGradient.addColorStop(1, 'rgba(156, 163, 175, 0.05)')
      }
      
      ctx.beginPath()
      ctx.arc(centerX, centerY, radius * 0.8, 0, Math.PI * 2)
      ctx.fillStyle = innerGradient
      ctx.fill()
      
      // Add subtle inner ring
      ctx.beginPath()
      ctx.arc(centerX, centerY, radius * 0.6, 0, Math.PI * 2)
      ctx.strokeStyle = isCallActive ? 'rgba(139, 92, 246, 0.2)' : 'rgba(156, 163, 175, 0.15)'
      ctx.lineWidth = 1
      ctx.stroke()
    }
    
    draw()
  }, [isCallActive])

  // WebSocket-Verbindung
  const connectWebSocket = async (): Promise<void> => {
    try {
      // WebSocket URL dynamisch ermitteln
      const isHttps = window.location.protocol === 'https:'
      const wsScheme = isHttps ? 'wss' : 'ws'
      const host = window.location.hostname || 'localhost'
      const apiPort = 8001
      const wsUrl = `${wsScheme}://${host}:${apiPort}/api/voice-chat/ws/${Date.now()}`
      
      // Bestehendes Format für MediaRecorder bestimmen
      const candidates = [
        { mime: 'audio/webm;codecs=opus', fmt: 'webm' },
        { mime: 'audio/webm', fmt: 'webm' },
        { mime: 'audio/mp4;codecs=mp4a.40.2', fmt: 'mp4' },
        { mime: 'audio/mp4', fmt: 'mp4' },
      ]
      const chosen = candidates.find(c => (window as any).MediaRecorder && (window as any).MediaRecorder.isTypeSupported?.(c.mime)) || candidates[0]
      const chosenFormat = chosen.fmt
      
      websocketRef.current = new WebSocket(wsUrl)
      websocketRef.current.binaryType = 'arraybuffer'
      const opened = new Promise<void>((resolve) => {
        websocketRef.current!.onopen = () => {
          console.log('WebSocket verbunden')
          setIsConnecting(false)
          setIsCallActive(true)
          
          // Konfiguration senden
          websocketRef.current?.send(JSON.stringify({
            type: 'config',
            voice_id: voiceId,
            language: language,
            format: chosenFormat
          }))
          resolve()
        }
      })
      
      websocketRef.current.onmessage = async (event) => {
        const payload = event.data
        if (payload instanceof Blob || payload instanceof ArrayBuffer) {
          // Audio-Daten empfangen (Blob oder ArrayBuffer)
          let arrayBuf: ArrayBuffer
          if (payload instanceof Blob) {
            arrayBuf = await payload.arrayBuffer()
          } else {
            arrayBuf = payload
          }

          setIsListening(false)
          setIsSpeaking(true)

          // Half‑Duplex: Aufnahme während Wiedergabe pausieren
          suspendCaptureRef.current = true
          if (sliceIntervalRef.current) { window.clearInterval(sliceIntervalRef.current); sliceIntervalRef.current = null }
          if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
            try { mediaRecorderRef.current.stop() } catch {}
          }

          const onPlaybackEnded = () => {
            setIsSpeaking(false)
            setIsListening(true)
            // Aufnahme wieder aufnehmen
            suspendCaptureRef.current = false
            if (streamRef.current && mediaRecorderRef.current && mediaRecorderRef.current.state === 'inactive') {
              window.setTimeout(() => { try { mediaRecorderRef.current?.start() } catch {} }, 200)
            }
          }

          // Primärer Weg: WebAudio
          try {
            if (!audioContextRef.current) {
              audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)()
            }
            const ctx = audioContextRef.current
            try { await unlockAudio() } catch {}
            try { await ctx.resume() } catch {}

            const decodedBuffer = await ctx.decodeAudioData(arrayBuf.slice(0))
            const source = ctx.createBufferSource()
            source.buffer = decodedBuffer
            source.connect(ctx.destination)
            source.onended = () => {
              onPlaybackEnded()
            }
            source.start(0)
            return
          } catch (e) {
            console.warn('WebAudio decode/play failed, falling back to HTMLAudio', e)
          }

          // Fallback: HTMLAudioElement
          try {
            if (!audioElRef.current) {
              audioElRef.current = new Audio()
              ;(audioElRef.current as any).playsInline = true
              audioElRef.current.setAttribute('playsinline', 'true')
              audioElRef.current.preload = 'auto'
              audioElRef.current.autoplay = true
              audioElRef.current.crossOrigin = 'anonymous'
              audioElRef.current.muted = false
              audioElRef.current.volume = 1.0
            }
            const audio = audioElRef.current
            // MP3 Blob erstellen
            const audioBlob = new Blob([arrayBuf], { type: 'audio/mpeg' })
            const audioUrl = URL.createObjectURL(audioBlob)
            try { audio.pause() } catch {}
            try { audio.currentTime = 0 } catch {}
            audio.src = audioUrl

            const canPlay = new Promise<void>((resolve) => {
              let resolved = false
              const onReady = () => { if (!resolved) { resolved = true; cleanup(); resolve() } }
              const cleanup = () => {
                audio.removeEventListener('canplay', onReady)
                audio.removeEventListener('canplaythrough', onReady)
              }
              audio.addEventListener('canplay', onReady, { once: true })
              audio.addEventListener('canplaythrough', onReady, { once: true })
              window.setTimeout(() => onReady(), 400)
            })
            await canPlay
            await audio.play()
            audio.onended = () => {
              try { URL.revokeObjectURL(audioUrl) } catch {}
              onPlaybackEnded()
            }
          } catch (err) {
            console.error('HTMLAudioElement fallback failed', err)
            onPlaybackEnded()
          }
        } else if (typeof payload === 'string') {
          // JSON-Nachricht
          let data: any
          try { data = JSON.parse(payload) } catch { 
            console.error('Failed to parse WebSocket JSON:', payload)
            return 
          }
          console.log('WebSocket Nachricht empfangen:', data)

          if (data.type === 'backchannel' && typeof data.url === 'string') {
            // Backchannel: Leise abspielen während User spricht
            console.log('Backchannel empfangen:', data.text)
            try {
              const absoluteUrl = data.url.startsWith('http') ? data.url : `${window.location.protocol}//${window.location.hostname}:8001${data.url}`
              // Direkt abspielen mit reduzierter Lautstärke
              const backchannelAudio = new Audio(absoluteUrl)
              backchannelAudio.volume = 0.3  // Leiser als normale Antworten
              backchannelAudio.play().catch(console.error)
            } catch (err) {
              console.error('Backchannel playback failed:', err)
            }
            return
          }
          
          if (data.type === 'tts_url' && typeof data.url === 'string') {
            console.log('TTS URL empfangen:', data.url)
            try {
              const absoluteUrl = data.url.startsWith('http') ? data.url : `${window.location.protocol}//${window.location.hostname}:8001${data.url}`
              console.log('Absolute TTS URL:', absoluteUrl)
              setLastTtsUrl(absoluteUrl)
              // In Queue legen und automatisch abspielen
              enqueueTtsUrl(absoluteUrl)
              console.log('TTS URL zur Queue hinzugefügt')
            } catch (err) {
              console.error('WebAudio tts_url failed, fallback to HTMLAudio', err)
              try {
                if (!audioElRef.current) {
                  audioElRef.current = new Audio()
                  ;(audioElRef.current as any).playsInline = true
                  audioElRef.current.setAttribute('playsinline', 'true')
                  audioElRef.current.preload = 'auto'
                  audioElRef.current.autoplay = true
                  audioElRef.current.muted = false
                  audioElRef.current.volume = 1.0
                }
                const audio = audioElRef.current
                const audioUrl = data.url.startsWith('http') ? data.url : `${window.location.protocol}//${window.location.hostname}:8001${data.url}`
                try { await unlockAudio() } catch {}
                try { await audioContextRef.current?.resume() } catch {}
                try { audio.pause() } catch {}
                try { audio.currentTime = 0 } catch {}
                audio.src = audioUrl
                await audio.play()
              } catch (e2) {
                console.error('HTMLAudioElement fallback failed for tts_url', e2)
              }
            }
            return
          }

          if (data.type === 'status') {
            if (data.status === 'interrupted') {
              // KI wurde unterbrochen - Audio stoppen
              console.log('AI interrupted - stopping audio playback')
              if (audioElRef.current) {
                audioElRef.current.pause()
                audioElRef.current.currentTime = 0
              }
              // Queue leeren
              ttsQueueRef.current = []
              isPlayingRef.current = false
              setIsSpeaking(false)
              setIsListening(true)
            } else if (data.status === 'listening') {
              setIsListening(true)
              setIsSpeaking(false)
              // Aufnahme wieder zulassen mit kleinem Delay
              suspendCaptureRef.current = false
              if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'inactive' && streamRef.current) {
                window.setTimeout(() => { try { mediaRecorderRef.current?.start(); segmentStartTsRef.current = Date.now() } catch {} }, 200)
              }
              if (!sliceIntervalRef.current) {
                // Wir nutzen VAD-only; nichts zu tun
              }
            } else if (data.status === 'thinking') {
              setIsListening(false)
              setIsSpeaking(false)
              if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
                try { mediaRecorderRef.current.stop() } catch {}
              }
            } else if (data.status === 'speaking') {
              setIsListening(false)
              setIsSpeaking(true)
              suspendCaptureRef.current = true
              if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
                try { mediaRecorderRef.current.stop() } catch {}
              }
            }
          }
        }
      }
      
      websocketRef.current.onerror = (error) => {
        console.error('WebSocket Fehler:', error)
        setError('Verbindungsfehler')
      }
      
      websocketRef.current.onclose = () => {
        console.log('WebSocket geschlossen')
        if (isCallActive) {
          // Automatischer Reconnect während aktivem Call
          setTimeout(() => { connectWebSocket().catch(() => {}) }, 500)
        } else {
          setIsCallActive(false)
          setIsConnecting(false)
        }
      }

      // Warten, bis Verbindung offen ist
      await opened
      
    } catch (err) {
      console.error('WebSocket-Verbindung fehlgeschlagen:', err)
      throw new Error('Verbindung zum Server fehlgeschlagen')
    }
  }

  // Audio-Aufnahme und Streaming
  const startRecording = (stream: MediaStream) => {
    // Gleiche Logik wie oben zur Auswahl des Formats
    const candidates = [
      'audio/webm;codecs=opus',
      'audio/webm',
      'audio/mp4;codecs=mp4a.40.2',
      'audio/mp4',
    ]
    const mime = candidates.find(m => (window as any).MediaRecorder && (window as any).MediaRecorder.isTypeSupported?.(m)) || 'audio/webm;codecs=opus'
    const mediaRecorder = new MediaRecorder(stream, { mimeType: mime as any })
    
    mediaRecorderRef.current = mediaRecorder
    recordedChunksRef.current = []
    
    mediaRecorder.ondataavailable = (event) => {
      if (suspendCaptureRef.current) return
      if (event.data && event.data.size > 0) {
        try {
          if (websocketRef.current && websocketRef.current.readyState === WebSocket.OPEN) {
            websocketRef.current.send(event.data)
          }
        } catch (e) {
          console.warn('WS send chunk failed', e)
        }
      }
    }
    
    mediaRecorder.onstop = () => {
      try { recordedChunksRef.current = [] } catch {}
      // Nach Abschluss direkt wieder starten
      if (!suspendCaptureRef.current && streamRef.current && mediaRecorderRef.current && mediaRecorderRef.current.state === 'inactive') {
        try { mediaRecorderRef.current.start(250); segmentStartTsRef.current = Date.now() } catch {}
      }
    }
    
    // Mit kleineren timeslices für niedrigere Latenz
    mediaRecorder.start(100)  // 100ms chunks für schnellere Reaktion
    segmentStartTsRef.current = Date.now()
    if (sliceIntervalRef.current) { window.clearInterval(sliceIntervalRef.current); sliceIntervalRef.current = null }

    // Einfache VAD: alle 150ms RMS prüfen; bei Stille ≥600ms Segment abschließen
    if (vadIntervalRef.current) window.clearInterval(vadIntervalRef.current)
    let silentCount = 0
    vadIntervalRef.current = window.setInterval(() => {
      if (suspendCaptureRef.current) { silentCount = 0; return }
      const analyser = analyserRef.current
      if (!analyser) return
      const len = analyser.fftSize
      const buf = new Uint8Array(len)
      analyser.getByteTimeDomainData(buf)
      let sumSq = 0
      for (let i = 0; i < len; i++) { const v = (buf[i] - 128) / 128; sumSq += v*v }
      const rms = Math.sqrt(sumSq / len)
      const isSilent = rms < 0.015  // Sensibler: Stille früher erkennen
      if (isSilent) silentCount++
      else silentCount = 0
      if (silentCount >= 3) { // ~450ms bei 150ms Schrittweite
        silentCount = 0
        if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
          try { mediaRecorderRef.current.stop() } catch {}
        }
      }
    }, 150)

    // Max-Segment-Dauer (~3s): hartes Abschließen, falls keine Stille erkannt wird
    if (segmentTimerRef.current) window.clearInterval(segmentTimerRef.current)
    segmentTimerRef.current = window.setInterval(() => {
      if (suspendCaptureRef.current) return
      const started = segmentStartTsRef.current || Date.now()
      const elapsed = Date.now() - started
      if (elapsed >= 3000) { // 3s Deckel
        try { if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') mediaRecorderRef.current.stop() } catch {}
        segmentStartTsRef.current = Date.now()
      }
    }, 250)
  }

  // Anruf starten
  const startCall = async () => {
    try {
      setIsConnecting(true)
      setError(null)
      
      // Mikrofon starten
      const stream = await startMicrophone()
      // Audio-Entsperrung
      await unlockAudio()
      
      // WebSocket verbinden
      await connectWebSocket()
      
      // Audio-Aufnahme starten
      startRecording(stream)
      
      // Visualisierung starten
      visualize()
      
      setIsListening(true)

      // Keepalive alle 10s, damit Verbindung aktiv bleibt
      if (keepAliveRef.current) window.clearInterval(keepAliveRef.current)
      keepAliveRef.current = window.setInterval(() => {
        try {
          if (websocketRef.current && websocketRef.current.readyState === WebSocket.OPEN) {
            websocketRef.current.send(JSON.stringify({ type: 'ping', t: Date.now() }))
          }
        } catch {}
      }, 5000)
      
    } catch (err: any) {
      setError(err.message || 'Fehler beim Starten des Anrufs')
      setIsConnecting(false)
    }
  }

  // Anruf beenden
  const endCall = () => {
    // VAD stoppen
    if (vadIntervalRef.current) {
      window.clearInterval(vadIntervalRef.current)
      vadIntervalRef.current = null
    }
    if (segmentTimerRef.current) {
      window.clearInterval(segmentTimerRef.current)
      segmentTimerRef.current = null
    }
    // Stop slicing interval
    if (sliceIntervalRef.current) {
      window.clearInterval(sliceIntervalRef.current)
      sliceIntervalRef.current = null
    }
    // Keepalive stoppen
    if (keepAliveRef.current) {
      window.clearInterval(keepAliveRef.current)
      keepAliveRef.current = null
    }
    // Audio stoppen
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop())
      streamRef.current = null
    }
    
    // MediaRecorder stoppen
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop()
      mediaRecorderRef.current = null
    }
    
    // WebSocket schließen
    if (websocketRef.current) {
      websocketRef.current.close()
      websocketRef.current = null
    }
    
    // Audio Context schließen
    if (audioContextRef.current) {
      audioContextRef.current.close()
      audioContextRef.current = null
    }
    
    // Animation stoppen
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current)
    }
    
    setIsCallActive(false)
    setIsConnecting(false)
    setIsSpeaking(false)
    setIsListening(false)
    setAudioLevel(0)
  }

  // Force-Send aktuelles Segment (schließt Aufnahme sofort ab)
  const forceSendSegment = useCallback(() => {
    try {
      suspendCaptureRef.current = false
      if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
        mediaRecorderRef.current.stop()
      }
      try {
        if (websocketRef.current && websocketRef.current.readyState === WebSocket.OPEN) {
          websocketRef.current.send(JSON.stringify({ type: 'force', t: Date.now() }))
        }
      } catch {}
    } catch {}
  }, [])
 
  // Cleanup bei Component Unmount
  useEffect(() => {
    return () => {
      endCall()
    }
  }, [])

  // Keyboard-Shortcuts: Enter/Space senden Segment
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (!isCallActive) return
      if (e.key === 'Enter' || e.code === 'Space') {
        e.preventDefault()
        forceSendSegment()
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [isCallActive, forceSendSegment])

  return (
    <div className="flex flex-col items-center justify-center p-8 bg-gradient-to-br from-purple-50/50 via-white to-blue-50/50 dark:from-gray-900/50 dark:via-gray-800 dark:to-purple-900/20 rounded-3xl shadow-2xl backdrop-blur-sm border border-purple-200/20 dark:border-purple-700/20">
      <audio ref={audioElRef} style={{ display: 'none' }} />
      {/* Modernized Visualizer */}
      <div className="relative mb-8">
        {/* Glow effect behind canvas */}
        <div className="absolute inset-0 rounded-full bg-gradient-to-r from-purple-500/20 to-blue-500/20 blur-3xl animate-pulse" />
        <canvas
          ref={canvasRef}
          width={300}
          height={300}
          className="rounded-full relative z-10"
          style={{ 
            background: 'radial-gradient(circle at center, rgba(139, 92, 246, 0.05), transparent)',
            boxShadow: isCallActive ? '0 0 60px rgba(139, 92, 246, 0.3)' : 'none'
          }}
        />
        
        {/* Status-Overlay */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            {isConnecting && (
              <div className="text-slate-600">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-2"></div>
                <p className="text-sm">Verbinde...</p>
              </div>
            )}
            {isCallActive && !isConnecting && (
              <div>
                {isListening && (
                  <div className="text-emerald-500">
                    <div className="relative w-16 h-16 mx-auto mb-2">
                      <div className="absolute inset-0 bg-emerald-500/20 rounded-full animate-ping"></div>
                      <div className="absolute inset-0 bg-emerald-500/30 rounded-full animate-ping animation-delay-200"></div>
                      <div className="relative w-full h-full bg-gradient-to-br from-emerald-400 to-green-600 rounded-full flex items-center justify-center">
                        <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clipRule="evenodd" />
                        </svg>
                      </div>
                    </div>
                    <p className="text-sm font-medium">Ich höre zu...</p>
                  </div>
                )}
                {isSpeaking && (
                  <div className="text-blue-500">
                    <div className="relative w-16 h-16 mx-auto mb-2">
                      <div className="absolute inset-0 bg-blue-500/20 rounded-full animate-pulse"></div>
                      <div className="relative w-full h-full bg-gradient-to-br from-blue-400 to-indigo-600 rounded-full flex items-center justify-center">
                        <svg className="w-8 h-8 text-white animate-pulse" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M9.383 3.076A1 1 0 0110 4v12a1 1 0 01-1.707.707L4.586 13H2a1 1 0 01-1-1V8a1 1 0 011-1h2.586l3.707-3.707a1 1 0 011.09-.217zM14.657 2.929a1 1 0 011.414 0A9.972 9.972 0 0119 10a9.972 9.972 0 01-2.929 7.071 1 1 0 01-1.414-1.414A7.971 7.971 0 0017 10c0-2.21-.894-4.208-2.343-5.657a1 1 0 010-1.414zm-2.829 2.828a1 1 0 011.415 0A5.983 5.983 0 0115 10a5.984 5.984 0 01-1.757 4.243 1 1 0 01-1.415-1.415A3.984 3.984 0 0013 10a3.983 3.983 0 00-1.172-2.828 1 1 0 010-1.415z" clipRule="evenodd" />
                        </svg>
                      </div>
                    </div>
                    <p className="text-sm font-medium">KI spricht...</p>
                  </div>
                )}
                {!isListening && !isSpeaking && (
                  <div className="text-purple-500">
                    <div className="relative w-16 h-16 mx-auto mb-2">
                      <div className="relative w-full h-full bg-gradient-to-br from-purple-400 to-purple-600 rounded-full flex items-center justify-center">
                        <div className="flex space-x-1">
                          <div className="w-2 h-2 bg-white rounded-full animate-bounce" style={{animationDelay: '0ms'}}></div>
                          <div className="w-2 h-2 bg-white rounded-full animate-bounce" style={{animationDelay: '150ms'}}></div>
                          <div className="w-2 h-2 bg-white rounded-full animate-bounce" style={{animationDelay: '300ms'}}></div>
                        </div>
                      </div>
                    </div>
                    <p className="text-sm font-medium">Verarbeite...</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Modern Call Button */}
      <button
        onClick={isCallActive ? endCall : startCall}
        disabled={isConnecting}
        className={`
          relative px-10 py-5 rounded-full font-semibold text-white shadow-2xl
          transition-all duration-300 transform hover:scale-105
          ${isCallActive 
            ? 'bg-gradient-to-r from-red-500 to-pink-600 hover:from-red-600 hover:to-pink-700' 
            : 'bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700'}
          ${isConnecting ? 'opacity-50 cursor-not-allowed' : ''}
        `}
        style={{
          boxShadow: isCallActive 
            ? '0 20px 40px -10px rgba(239, 68, 68, 0.5)' 
            : '0 20px 40px -10px rgba(139, 92, 246, 0.5)'
        }}
      >
        <div className="flex items-center gap-3">
          {isCallActive ? (
            <>
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                  d="M6 18L18 6M6 6l12 12" />
              </svg>
              <span>Anruf beenden</span>
            </>
          ) : (
            <>
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                  d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
              </svg>
              <span>Anruf ausprobieren</span>
            </>
          )}
        </div>
      </button>

      {/* Senden-Button */}
      {isCallActive && (
        <div className="mt-3">
          <button
            onClick={forceSendSegment}
            className="px-4 py-2 rounded-md bg-emerald-600 hover:bg-emerald-700 text-white text-sm shadow"
          >
            Senden (Enter/Space)
          </button>
        </div>
      )}

      {/* Modern Audio Level Indicator */}
      {isCallActive && (
        <div className="mt-6 w-full max-w-xs">
          <div className="flex items-center justify-between text-sm mb-2">
            <span className="text-gray-600 dark:text-gray-400 font-medium">Audio-Pegel</span>
            <span className="text-purple-600 dark:text-purple-400 font-bold">{Math.round(audioLevel)}%</span>
          </div>
          <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden shadow-inner">
            <div 
              className="h-full bg-gradient-to-r from-purple-400 via-blue-500 to-emerald-400 transition-all duration-100 rounded-full"
              style={{ 
                width: `${audioLevel}%`,
                boxShadow: `0 0 10px rgba(139, 92, 246, ${audioLevel / 100})`
              }}
            />
          </div>
        </div>
      )}

      {/* Fehler-Anzeige */}
      {error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          {error}
        </div>
      )}

      {/* Debug-Player */}
      {lastTtsUrl && (
        <div className="mt-6 w-full max-w-md p-4 border border-slate-200 rounded-xl bg-white shadow-sm">
          <div className="text-sm text-slate-600 mb-2">Letzte Antwort‑Audio URL:</div>
          <div className="text-xs break-all text-slate-500 mb-3">{lastTtsUrl}</div>
          <div className="flex gap-3">
            <button
              className="px-4 py-2 rounded-md bg-indigo-600 text-white text-sm"
              onClick={async () => {
                try { await unlockAudio() } catch {}
                try { await audioContextRef.current?.resume() } catch {}
                try {
                  if (!audioElRef.current) audioElRef.current = new Audio()
                  const a = audioElRef.current
                  a.src = lastTtsUrl!
                  a.muted = false
                  a.volume = 1.0
                  await a.play()
                } catch (e1) {
                  console.warn('HTMLAudio play failed, try WebAudio', e1)
                  try {
                    if (!audioContextRef.current) audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)()
                    const ctx = audioContextRef.current
                    await ctx.resume()
                    const r = await fetch(lastTtsUrl!, { cache: 'no-store' })
                    const b = await r.arrayBuffer()
                    const dec = await ctx.decodeAudioData(b.slice(0))
                    const s = ctx.createBufferSource()
                    s.buffer = dec
                    s.connect(ctx.destination)
                    s.start(0)
                  } catch (e2) {
                    console.error('WebAudio manual play failed', e2)
                  }
                }
              }}
            >Manuell abspielen</button>
            <button
              className="px-4 py-2 rounded-md bg-slate-200 text-slate-700 text-sm"
              onClick={() => {
                try { audioElRef.current?.pause() } catch {}
              }}
            >Stopp</button>
          </div>
        </div>
      )}

      {/* Modern Info Cards */}
      <div className="mt-8 grid grid-cols-2 gap-4 max-w-md">
        <div className="bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm rounded-xl p-4 border border-purple-200/20 dark:border-purple-700/20">
          <div className="text-2xl mb-2">🎤</div>
          <p className="text-xs text-gray-600 dark:text-gray-400">Mikrofon erlauben für beste Qualität</p>
        </div>
        <div className="bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm rounded-xl p-4 border border-blue-200/20 dark:border-blue-700/20">
          <div className="text-2xl mb-2">💬</div>
          <p className="text-xs text-gray-600 dark:text-gray-400">Natürlich sprechen wie am Telefon</p>
        </div>
        <div className="bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm rounded-xl p-4 border border-emerald-200/20 dark:border-emerald-700/20">
          <div className="text-2xl mb-2">⚡</div>
          <p className="text-xs text-gray-600 dark:text-gray-400">KI reagiert in unter 500ms</p>
        </div>
        <div className="bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm rounded-xl p-4 border border-pink-200/20 dark:border-pink-700/20">
          <div className="text-2xl mb-2">🔒</div>
          <p className="text-xs text-gray-600 dark:text-gray-400">Ende-zu-Ende verschlüsselt</p>
        </div>
      </div>
    </div>
  )
}

export default VoiceChat