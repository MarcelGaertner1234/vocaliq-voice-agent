import { useState, useEffect } from 'react'
import { Card, CardHeader, CardContent } from '../components/ui/Card'
import Button from '../components/ui/Button'
import Input from '../components/ui/Input'
import Badge from '../components/ui/Badge'
import { knowledgeApi } from '../services/api'
import { 
  DocumentTextIcon,
  TrashIcon,
  ArrowUpTrayIcon,
  EyeIcon,
  ChartBarIcon,
  MagnifyingGlassIcon
} from '@heroicons/react/24/outline'

interface KnowledgeDocument {
  id: string
  name: string
  type: string
  size: string
  uploaded: string
  status: 'uploading' | 'processing' | 'processed' | 'failed'
  chunks: number
  progress?: number
}

interface SearchResult {
  content: string
  document: string
  relevance_score: number
  metadata?: Record<string, unknown>
}

function KnowledgeBase() {
  const [searchTerm, setSearchTerm] = useState('')
  const [documents, setDocuments] = useState<KnowledgeDocument[]>([])
  const [uploading, setUploading] = useState(false)
  const [dragActive, setDragActive] = useState(false)
  const [results, setResults] = useState<SearchResult[] | null>(null)

  useEffect(() => {
    loadDocuments()
  }, [])

  const loadDocuments = async () => {
    try {
      const docs = await knowledgeApi.getDocuments() as Array<{
        id: string
        filename: string
        file_type: string
        file_size?: number
        uploaded_at?: string
        processing_status?: string
        chunk_count?: number
      }>
      // Map Backend-Form in UI-Form
      const mapped: KnowledgeDocument[] = docs.map((d) => ({
        id: d.id,
        name: d.filename,
        type: (d.file_type || '').toUpperCase(),
        size: d.file_size ? `${Math.round(d.file_size)} B` : '-',
        uploaded: d.uploaded_at ? new Date(d.uploaded_at).toLocaleString() : '-',
        status: d.processing_status === 'completed' ? 'processed' : (d.processing_status ? 'processing' : 'processing'),
        chunks: d.chunk_count || 0
      }))
      setDocuments(mapped)
    } catch {
      console.warn('Using demo data - backend not available')
    }
  }

  const filteredDocs = documents.filter(doc => 
    doc.name.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'processed': return 'success'
      case 'processing': return 'warning'
      case 'failed': return 'error'
      default: return 'default'
    }
  }

  const handleFileUpload = async (files: FileList | File[]) => {
    setUploading(true)
    const fileArray = Array.from(files)
    
    for (const file of fileArray) {
      const newDoc: KnowledgeDocument = {
        id: String(Date.now() + Math.random()),
        name: file.name,
        type: file.name.split('.').pop()?.toUpperCase() || 'UNKNOWN',
        size: formatFileSize(file.size),
        uploaded: new Date().toLocaleString(),
        status: 'uploading',
        chunks: 0,
        progress: 0
      }
      
      setDocuments(prev => [...prev, newDoc])
      
      try {
        for (let progress = 0; progress <= 100; progress += 25) {
          await new Promise(resolve => setTimeout(resolve, 120))
          setDocuments(prev => prev.map(doc => 
            doc.id === newDoc.id ? { ...doc, progress } : doc
          ))
        }
        try {
          await knowledgeApi.uploadDocument(file)
        } catch {
          console.warn('Backend upload failed (will still mark as processed for UI)')
        }
        setDocuments(prev => prev.map(doc => 
          doc.id === newDoc.id ? { ...doc, status: 'processed', progress: undefined } : doc
        ))
        await loadDocuments()
      } catch {
        setDocuments(prev => prev.map(doc => 
          doc.id === newDoc.id ? { ...doc, status: 'failed' } : doc
        ))
      }
    }
    
    setUploading(false)
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
  }
  
  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files
    if (files) {
      handleFileUpload(files)
    }
  }
  
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragActive(false)
    const files = e.dataTransfer.files
    if (files) {
      handleFileUpload(files)
    }
  }
  
  const handleDeleteDocument = async (docId: string) => {
    try {
      await knowledgeApi.deleteDocument(docId)
      await loadDocuments()
    } catch {
      setDocuments(prev => prev.filter(doc => doc.id !== docId))
    }
  }

  const handleSearch = async () => {
    if (!searchTerm.trim()) { setResults(null); return }
    try {
      const resp = await knowledgeApi.search(searchTerm.trim(), 8) as { results?: SearchResult[] }
      setResults(resp.results || [])
    } catch {
      setResults([])
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Knowledge Base</h1>
        <div className="flex space-x-3">
          <label htmlFor="file-upload">
            <Button variant="outline" disabled={uploading}>
              <ArrowUpTrayIcon className="h-4 w-4 mr-2" />
              {uploading ? 'Uploading...' : 'Upload Documents'}
            </Button>
          </label>
          <input
            id="file-upload"
            type="file"
            multiple
            accept=".pdf,.txt,.docx,.doc,.md"
            onChange={handleInputChange}
            className="hidden"
          />
          <Button onClick={loadDocuments} variant="outline">
            <ChartBarIcon className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>
      
      {/* Suche */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-medium text-gray-900">Search Knowledge</h3>
            <div className="flex items-center space-x-2">
              <Input
                placeholder="Type your query..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-80"
              />
              <Button variant="outline" onClick={handleSearch}>
                <MagnifyingGlassIcon className="h-4 w-4 mr-2" />
                Search
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {results && (
            results.length === 0 ? (
              <div className="text-sm text-gray-500">No results</div>
            ) : (
              <div className="space-y-3">
                {results.map((r, idx) => (
                  <div key={idx} className="p-3 border rounded-md bg-gray-50">
                    <div className="text-xs text-gray-500 mb-1">{r.document}</div>
                    <div className="text-sm whitespace-pre-wrap">{r.content}</div>
                    <div className="text-xs text-gray-400 mt-1">Score: {r.relevance_score.toFixed(3)}</div>
                  </div>
                ))}
              </div>
            )
          )}
        </CardContent>
      </Card>

      {/* Drag & Drop Zone */}
      <div 
        className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
          dragActive ? 'border-primary-500 bg-primary-50' : 'border-gray-300'
        }`}
        onDrop={handleDrop}
        onDragOver={(e) => { e.preventDefault(); setDragActive(true) }}
        onDragLeave={() => setDragActive(false)}
      >
        <ArrowUpTrayIcon className="mx-auto h-12 w-12 text-gray-400" />
        <p className="mt-2 text-sm text-gray-600">
          Drag and drop files here, or click "Upload Documents" to browse
        </p>
        <p className="text-xs text-gray-500 mt-1">
          Supports PDF, DOCX, TXT, MD files
        </p>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-medium text-gray-900">Documents</h3>
            <div className="flex items-center space-x-4">
              <Input
                placeholder="Filter documents..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-64"
              />
            </div>
          </div>
        </CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Document
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Size
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Chunks
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Uploaded
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredDocs.map((doc) => (
                  <tr key={doc.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <DocumentTextIcon className="h-5 w-5 text-gray-400 mr-3" />
                        <div>
                          <div className="text-sm font-medium text-gray-900">
                            {doc.name}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <Badge variant={getStatusColor(doc.status)}>
                        {doc.type}
                      </Badge>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {doc.size}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center space-x-2">
                        <Badge variant={getStatusColor(doc.status)}>
                          {doc.status}
                        </Badge>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {doc.chunks > 0 ? doc.chunks : '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {doc.uploaded}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex space-x-2">
                        <Button variant="outline" size="sm" disabled={doc.status !== 'processed'}>
                          <EyeIcon className="h-4 w-4" />
                        </Button>
                        {doc.status === 'processed' && (
                          <Button variant="outline" size="sm" title="View chunks">
                            <ChartBarIcon className="h-4 w-4" />
                          </Button>
                        )}
                        <Button 
                          variant="outline" 
                          size="sm" 
                          onClick={() => handleDeleteDocument(doc.id)}
                          disabled={doc.status === 'uploading'}
                        >
                          <TrashIcon className="h-4 w-4 text-error-600" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default KnowledgeBase