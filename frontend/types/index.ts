export type AnalysisStatus = 'pending' | 'processing' | 'completed' | 'failed'

export type ViolationType = 
  | '图层错误'
  | '线宽错误'
  | '颜色错误'
  | '字体错误'
  | '尺寸标注错误'
  | '文字错误'
  | '几何错误'

export type SeverityLevel = '严重' | '警告' | '提示'

export interface Violation {
  id: string
  type: ViolationType
  severity: SeverityLevel
  rule: string
  description: string
  entity_handle?: string
  layer?: string
  location?: {
    x?: number
    y?: number
  }
  entity_details?: Record<string, any>
  suggestion?: string
}

export interface ComplianceReport {
  analysis_id: string
  file_id: string
  filename: string
  standard: string
  analysis_time: string
  total_violations: number
  critical_count: number
  warning_count: number
  info_count: number
  violations: Violation[]
  is_compliant: boolean
  compliance_score: number
}

export interface FileUploadResponse {
  file_id: string
  filename: string
  size: number
  upload_time: string
  message: string
}

export interface AnalysisResponse {
  analysis_id: string
  file_id: string
  status: AnalysisStatus
  message: string
}
