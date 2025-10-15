const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function uploadFile(file: File) {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`${API_BASE_URL}/api/v1/upload`, {
    method: 'POST',
    body: formData
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || '文件上传失败')
  }

  return await response.json()
}

export async function startAnalysis(fileId: string, standard: string = 'GB/T 14665-2012') {
  const response = await fetch(`${API_BASE_URL}/api/v1/analyze`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      file_id: fileId,
      standard
    })
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || '启动分析失败')
  }

  return await response.json()
}

export async function getAnalysisStatus(analysisId: string) {
  const response = await fetch(`${API_BASE_URL}/api/v1/analyze/${analysisId}`)

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || '获取状态失败')
  }

  return await response.json()
}

export async function getReport(analysisId: string) {
  const response = await fetch(`${API_BASE_URL}/api/v1/report/${analysisId}`)

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || '获取报告失败')
  }

  return await response.json()
}

export async function exportReport(analysisId: string, format: 'json' | 'html' | 'pdf') {
  const response = await fetch(`${API_BASE_URL}/api/v1/report/${analysisId}/export?format=${format}`)

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || '导出失败')
  }

  // 创建下载链接
  const blob = await response.blob()
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `report_${analysisId}.${format}`
  document.body.appendChild(a)
  a.click()
  window.URL.revokeObjectURL(url)
  document.body.removeChild(a)
}
